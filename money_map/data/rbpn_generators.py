
import random
from datetime import date
from typing import List, Dict, Union

import pandas as pd
from attrs import define, field

from faker import Faker
from faker.providers import (bank, company, date_time, person, lorem)

# ==============================================================================
# Constants [Possible Value Pools]
# ==============================================================================

POS_INCOME_BOOKING_TEXTS:List[str] = ["GUTSCHRIFT","EINZAHLUNG","LOHN/GEHALT"]
POS_EXPENSE_BOOKING_TEXTS:List[str] = ["LASTSCHRIFT","SEPA-UEBERWEISUNG","DAUERAUFTRAG",
                                       "Kartenzahlung girocard","Aufladung Mobilfunkguthaben",
                                       "Auszahlung girocard","Kartenzahlung V PAY","ABSCHLUSS"]
POS_MONTHLY_BOOKING_TEXTS:List[str] = ["DAUERAUFTRAG","ABSCHLUSS","LOHN/GEHALT"]
POS_SENDER_ACCOUNT_TYPES:List[str] = ["Girokonto"]
POS_SENDER_BANK_NAMES:List[str] = ["RBPN"]

# ==============================================================================
# Column Mapping
# ==============================================================================

RBPN_COLUMN_MAPPING:Dict[str,str] = {'sender_account_type': 'Bezeichnung Auftragskonto',
                                    'sender_iban': 'IBAN Auftragskonto',
                                    'sender_bic': 'BIC Auftragskonto',
                                    'sender_bank_name': 'Bankname Auftragskonto',
                                    'booking_date': 'Buchungstag',
                                    'value_date': 'Valutadatum',
                                    'receiver_name': 'Name Zahlungsbeteiligter',
                                    'receiver_iban': 'IBAN Zahlungsbeteiligter',
                                    'receiver_bic': 'BIC (SWIFT-Code) Zahlungsbeteiligter',
                                    'booking_text': 'Buchungstext',
                                    'purpose': 'Verwendungszweck',
                                    'amount': 'Betrag',
                                    'currency': 'Waehrung',
                                    'balance_after_booking': 'Saldo nach Buchung',
                                    'notes': 'Bemerkung',
                                    'default_category': 'Kategorie',
                                    'tax_relevant': 'Steuerrelevant',
                                    'creditor_id': 'Glaeubiger ID',
                                    'mandate_reference': 'Mandatsreferenz'}

# ==============================================================================
# RBPN Data Generator
# ==============================================================================

@define
class RBPN_Generator:

    # region [init]
    pos_sender_account_types:List[str]=field(default=POS_SENDER_ACCOUNT_TYPES,init=True)
    pos_sender_bank_names:List[str]=field(default=POS_SENDER_BANK_NAMES,init=True)
    pos_income_booking_texts:List[str]=field(default=POS_INCOME_BOOKING_TEXTS,init=True)
    pos_expense_booking_texts:List[str]=field(default=POS_EXPENSE_BOOKING_TEXTS,init=True)
    pos_monthly_booking_texts:List[str]=field(default=POS_MONTHLY_BOOKING_TEXTS,init=True)
    faker_seed:int=field(default=1234,init=True)

    # post init
    fake:Faker=field(init=False)
    pos_amounts:List[float] = field(init=False)

    def __attrs_post_init__(self) -> None:
        # init faker
        self.fake = self.init_faker(faker_seed=self.faker_seed)
        # create possible variables for specific columns
        self.pos_amounts = self.create_possible_amounts()

    def init_faker(self,faker_seed:int) -> Faker:
        '''Initializing faker object, containing providers: person, bank,
           company, date_time and lorem.

        Parameters
        ----------
        faker_seed : int
            Input for Faker.seed() function

        Returns
        -------
        Faker
            Faker object used to generate random data.
        '''

        # init faker with specific seed
        fake = Faker()
        Faker.seed(faker_seed)

        # add required providers
        fake.add_provider(person)
        fake.add_provider(bank)
        fake.add_provider(company)
        fake.add_provider(date_time)
        fake.add_provider(lorem)

        return fake

    #endregion

    # region [public]

    def generate_random_data(self,
                             start_date:date,
                             end_date:date,
                             num_unique_sender:int,
                             num_unique_receiver:int,
                             start_balance:float,
                             ) -> pd.DateOffset:

        df = self.create_random_transactions(start_date=start_date,
                                             end_date=end_date,
                                             num_unique_sender=num_unique_sender,
                                             num_unique_receiver=num_unique_receiver)

        df = self.repeat_some_transactions_monthly(df=df,
                                                   start_date=start_date,
                                                   end_date=end_date)

        df = self.add_balance_after_booking(df=df,
                                            start_balance=start_balance)

        df = self.rename_columns(df=df)

        return df


    def create_random_transactions(self,
                                   start_date:date,
                                   end_date:date,
                                   num_unique_sender:int,
                                   num_unique_receiver:int
                                   ) -> pd.DataFrame:
        # init
        new_entry:Dict[str,Union[str,float]] = {}
        transactions:List[Dict[str,Union[str,float]] ] = []


        for i in range(num_unique_sender):
            new_entry.update(self.create_random_sender())

            for j in range(num_unique_receiver):
                new_entry.update(self.create_random_receiver())

                # insert other required columns
                buchungstag = self.fake.date_between(start_date=start_date,
                                    end_date=end_date)
                new_entry["booking_date"] = buchungstag
                new_entry["value_date"] = buchungstag
                new_entry["purpose"] = self.fake.paragraph(nb_sentences=1)
                new_entry["amount"] = random.choice(self.pos_amounts)

                # define booking text
                if float(new_entry["amount"]) > 0:
                    new_entry["booking_text"] = random.choice(self.pos_income_booking_texts)
                else:
                    new_entry["booking_text"] = random.choice(self.pos_expense_booking_texts)
                    pass

                # constants (not that relevant, but required)
                new_entry["currency"] = "EUR"
                new_entry["notes"] = None
                new_entry["default_category"] = None
                new_entry["tax_relevant"] = None
                new_entry["creditor_id"] = None
                new_entry["mandate_reference"] = None

                # append row to transaction
                transactions.append(new_entry.copy())

        # define balance after booking based on start balance
        df = pd.DataFrame(transactions)

        return df

    def repeat_some_transactions_monthly(self,
                                         df: pd.DataFrame,
                                         start_date:date,
                                         end_date:date
                                         ) -> pd.DataFrame:

        # define months between given start and end date
        month_range = (pd.date_range(start_date,end_date,freq="MS")
                        .to_series().reset_index(drop=True))

        # filter ut relevant transactions
        target_rows = df.loc[df["booking_text"].isin(self.pos_monthly_booking_texts)]
        others = df.loc[~df["booking_text"].isin(self.pos_monthly_booking_texts)]

        # init result dataframe
        new_data = pd.DataFrame()

        # iterate over all rows
        for i in range(target_rows.shape[0]):
            cur_date = target_rows.iloc[[i]]["booking_date"].values[0]
            cur_day = min(cur_date.day,28)
            # define new dates
            new_dates = month_range.apply(lambda x: x.replace(day=cur_day))
            # repeat data & adjust dates
            cur_new_data = pd.concat([target_rows.iloc[[i]]]*(month_range.shape[0]))
            cur_new_data["booking_date"] = new_dates.dt.date.values
            cur_new_data["value_date"] = new_dates.dt.date.values
            new_data=pd.concat([new_data,cur_new_data],axis="index")

        return pd.concat([others,new_data],axis="index")



    def add_balance_after_booking(self,
                                  df:pd.DataFrame,
                                  start_balance:float,
                                  booking_date_col_name:str = "booking_date",
                                  amount_col_name:str = "amount",
                                  res_col_name:str = "balance_after_booking",
                                  temp_col_name:str = "start_balance"
                                  ) -> pd.DataFrame:

        df = df.sort_values(booking_date_col_name)
        df[temp_col_name] = start_balance
        df[res_col_name] = df[amount_col_name].cumsum() + df[temp_col_name]
        df = df.drop(columns=[temp_col_name])

        return df.reset_index(drop=True)

    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=RBPN_COLUMN_MAPPING)

    #endregion

    # region [private]
    #endregion

    # region [class]
    #endregion

    # region [properties]
    #endregion

    # region [protected]
    def create_possible_amounts(self,
                                total_samples:int=1000,
                                expenses_ratio:float=0.90
                                ) -> List[float]:
        '''Creates a list of possible amounts used for random transactions.
           Amounts can be positive = income or negative = expense.

        Parameters
        ----------
        total_samples : int, optional
            Number of samples, by default 1000
        expenses_ratio : float, optional
            Ratio of amount samples that are expenses (value < 0), by default 0.90

        Returns
        -------
        List[float]
            List containing possible amounts.
            total_samples*(1-expenses_ratio) are positive numbers and
            total_samples*expenses_ratio are negative numbers.
        '''

        negative_numbers= [round(-abs(random.gauss(-150, 150)),2) for i
                        in range(int(total_samples*expenses_ratio))]
        positive_numbers= [round(abs(random.gauss(2500, 500)),2) for i
                        in range(int(total_samples*(1-expenses_ratio)+1))]
        pos_amounts = negative_numbers + positive_numbers

        return pos_amounts

    # random new_entry related to sender
    def create_random_sender(self) -> Dict[str,str]:
        '''Creating random sender data for a random RBPN transaction.

        Returns
        -------
        Dict[str,str]
            Contains random sender data, part of random RBPN transaction.
        '''

        new_entry = {}
        new_entry["sender_account_type"] = random.choice(self.pos_sender_account_types)
        new_entry["sender_iban"] =  self.fake.iban()
        new_entry["sender_bic"] =  self.fake.bban()
        new_entry["sender_bank_name"] = random.choice(self.pos_sender_bank_names)

        return new_entry

    # random new_entry related to receiver
    def create_random_receiver(self) -> Dict[str,str]:
        '''Creating random receiver data for a random RBPN transaction.

        Returns
        -------
        Dict[str,str]
            Contains random receiver data, part of random RBPN transaction.
        '''

        new_entry = {}
        new_entry["receiver_name"] = random.choice([self.fake.name(),self.fake.company()])
        new_entry["receiver_iban"] = self.fake.iban()
        new_entry["receiver_bic"] = self.fake.bban()
        new_entry["purpose"] = self.fake.text(max_nb_chars=40)

        return new_entry

    #endregion

    # region [overwrite]
    #endregion
