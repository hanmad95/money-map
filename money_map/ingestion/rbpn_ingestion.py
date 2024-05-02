# stdlib
import re
from pathlib import Path
from typing import List,Dict

from attrs import define
import pandas as pd

from sqlalchemy import select, inspect
from sqlalchemy.orm import Session

# custom class
from money_map.connect.mysql_conector import MySQLConnector
from money_map.models.orm_models import Transactions_Table
from money_map.ingestion.ingestor import Ingestor

# =============================================================================
# Constants for cleaning input data
# =============================================================================

RBPN_COLUMN_MAPPING:Dict[str,str] = {
    'Bezeichnung Auftragskonto':'sender_account_type',
    'IBAN Auftragskonto':'sender_iban',
    'BIC Auftragskonto':'sender_bic',
    'Bankname Auftragskonto':'sender_bank_name',
    'Buchungstag':'booking_date',
    'Valutadatum':'value_date',
    'Name Zahlungsbeteiligter':'receiver_name',
    'IBAN Zahlungsbeteiligter':'receiver_iban',
    'BIC (SWIFT-Code) Zahlungsbeteiligter':'receiver_bic',
    'Buchungstext':'booking_text',
    'Verwendungszweck':'purpose',
    'Betrag':'amount',
    'Waehrung':'currency',
    'Saldo nach Buchung':'balance_after_booking',
    'Bemerkung':'notes',
    'Kategorie':'default_category',
    'Steuerrelevant':'tax_relevant',
    'Glaeubiger ID':'creditor_id',
    'Mandatsreferenz':'mandate_reference'}


RBPN_UMLAUTE_MAPPING:Dict[str,str] = {'ü':'ue', 'Ü':'Ue',
                                      'ä':'ae',  'Ä':'Ae',
                                      'ö':'oe',  'Ö':'Oe',
                                      'ß':'ss'}

# =============================================================================
# RBPN_Ingestor
# =============================================================================

@define
class RBPN_Ingestor(Ingestor):

    # reion [init]
    target_table_name:str = Transactions_Table.__tablename__
    primary_key_col:str = inspect(Transactions_Table).primary_key[0].name
    connector:MySQLConnector = MySQLConnector()
    # endregion

    # region [public]
    def ingest_data(self,file_path:Path,verbose:bool=True)-> None:

        df = self.read_data(file_path=file_path)
        df = self.clean_data(df=df)

        contained_ids = self.request_processed_ids()
        df = df[~df[self.primary_key_col].isin(contained_ids)]

        # ingest new data
        if not df.empty:
            self.store_data(df=df)
            if verbose:
                print('->', df.shape[0], 'new rows ingested!')
        else:
            if verbose:
                print('-> Data is already contained in SQL DB: ',
                      Transactions_Table.__tablename__)
        return

    # endregion

    # endregion

    # region [class]
    # endregion

    # region [properties]
    # endregion

    # region [protected]
    def read_data(self,file_path: Path,
                  file_format: str = '.csv') -> pd.DataFrame:

        if file_format == '.csv':
            try:
                df = pd.read_csv(file_path,sep=';')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path,sep=';',encoding='latin1')
                df = df.replace(RBPN_UMLAUTE_MAPPING,regex=True)
            return df
        else:
            raise Exception('Unknown File Format!')

    def clean_data(self,df: pd.DataFrame) -> pd.DataFrame:

        # drop empty rows
        df = df.dropna(how='all')

        # assure all required columns are there
        assert all([False for ele in RBPN_COLUMN_MAPPING.keys()
                    if ele not in df.columns])
        df = df[list(RBPN_COLUMN_MAPPING.keys())]

        # rename columns
        df = df.rename(columns=RBPN_COLUMN_MAPPING)

        # change data types for transaction information
        try:
            df['booking_date'] = pd.to_datetime(df['booking_date'],format='%Y-%m-%d')
            df['value_date'] = pd.to_datetime(df['value_date'],format='%Y-%m-%d')
        except ValueError:
            df['booking_date'] = pd.to_datetime(df['booking_date'],format='%d.%m.%Y')
            df['value_date'] = pd.to_datetime(df['value_date'],format='%d.%m.%Y')

        df['amount'] = df['amount'].astype(str).str.replace(',','.').astype(float)
        df['balance_after_booking'] = (df['balance_after_booking'].astype(str)
                                    .str.replace(',','.').astype(float))

        # define day, month, year based on booking_date
        df['day'] = df['booking_date'].dt.day.astype(str).str.zfill(2)
        df['month'] = df['booking_date'].dt.month.astype(str).str.zfill(2)
        df['year'] = df['booking_date'].dt.year.astype(str)

        # check if transaction id columns do not contain nan
        transaction_id_columns = ['booking_date','sender_iban',
                                  'balance_after_booking','purpose']
        assert not df[transaction_id_columns].isnull().values.any()

        # add transaction id (primary key)
        df['transaction_id'] = (df['sender_iban'].astype(str).str[-10:] + '_' +
                                df['day'] + df['month']+ df['year']+ '_' +
                                df['balance_after_booking'].astype(int).astype(str) + '_' +
                                df['purpose'].astype(str).str[:8])

        # add column purpose_chars
        df['purpose_char'] = df['purpose'].apply(self.remove_numbers_and_symbols)
        df['purpose_char'] = df['purpose_char'].str.lower()

        # assure some columns are not null
        not_nullable_cols = ['sender_iban', 'sender_bank_name','receiver_name',
                             'receiver_iban', 'booking_text', 'purpose',
                             'transaction_id', 'purpose_char']
        df[not_nullable_cols] = df[not_nullable_cols].fillna('')

        # drop cols, rows & duplicates
        df = df.drop(columns=['day','month','year'])
        df = df.drop_duplicates()

        return df

    def request_processed_ids(self) -> List[str]:
        engine = self.connector.create_sql_engine()
        with Session(engine) as session:
            stmt = select(Transactions_Table.transaction_id).distinct()
            df = pd.read_sql(stmt,session.bind)
            res = list(df[self.primary_key_col].tolist())
        return res

    def store_data(self,
                   df: pd.DataFrame,
                   if_exists:str='append') -> None:
        engine = self.connector.create_sql_engine()
        df.to_sql(con=engine,
                  name=self.target_table_name,
                  if_exists=if_exists,
                  index=False)
        return

    # Function to remove numbers from a string using regular expressions
    def remove_numbers_and_symbols(self, text):
        return re.sub(r'[^a-zA-Z\s]', '', text)

    # endregion

    # region [overwrite]
    # endregion
