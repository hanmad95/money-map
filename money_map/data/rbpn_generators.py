
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
    def create_random_transactions(self,
                                   start_date:date,
                                   end_date:date,
                                   start_balance:float,
                                   num_unique_sender:int,
                                   num_unique_receiver:int
                                   ) -> pd.DataFrame:
        # init
        new_entry:Dict[str,Union[str,float]] = {}
        transactions:List[Dict[str,Union[str,float]] ] = []


        for k in range(num_unique_sender):
            new_entry.update(self.create_random_sender())

            for i in range(num_unique_receiver):
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


    # TODO:
    def repeat_some_transactions(df: pd.DataFrame) -> pd.DataFrame:

        return df



    def add_balance_after_booking(df:pd.DataFrame,
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

        return df

    def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
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

        negative_numbers= [round(-abs(random.gauss(-150, 150)),2) for i
                        in range(int(total_samples*expenses_ratio))]
        positive_numbers= [round(abs(random.gauss(2500, 500)),2) for i
                        in range(int(total_samples*(1-expenses_ratio)+1))]
        pos_amounts = negative_numbers + positive_numbers

        return pos_amounts

    # random new_entry related to sender
    def create_random_sender(self) -> Dict[str,str]:

        new_entry = {}
        new_entry["sender_account_type"] = random.choice(self.pos_sender_account_types)
        new_entry["sender_iban"] =  self.fake.iban()
        new_entry["sender_bic"] =  self.fake.bban()
        new_entry["sender_bank_name"] = random.choice(self.pos_sender_bank_names)

        return new_entry

    # random new_entry related to receiver
    def create_random_receiver(self) -> Dict[str,str]:

        new_entry = {}
        new_entry["receiver_name"] = random.choice([self.fake.name(),self.fake.company()])
        new_entry["receiver_iban"] = self.fake.iban()
        new_entry["receiver_bic"] = self.fake.bban()
        new_entry["purpose"] = self.fake.text(max_nb_chars=40)

        return new_entry

    #endregion

    # region [overwrite]
    #endregion
