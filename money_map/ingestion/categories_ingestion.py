# stdlib
from pathlib import Path
from typing import List

from attrs import define
import pandas as pd
import json

from sqlalchemy import select, inspect
from sqlalchemy.orm import Session

# custom class
from money_map.ingestion.ingestor import Ingestor
from money_map.models.orm_models import Transaction_Categories_Table
from money_map.connect.mysql_conector import MySQLConnector

# =============================================================================
# Transaction Categories
# =============================================================================

@define
class Categories_Ingestor(Ingestor):

    # reion [init]
    target_table_name:str = Transaction_Categories_Table.__tablename__
    primary_key_col:str = inspect(Transaction_Categories_Table).primary_key[0].name
    connector:MySQLConnector = MySQLConnector()
    # endregion

    # region [public]
    def ingest_data(self,file_path:Path,verbose:bool=True)-> None:

        if file_path is not None:
            df = self.read_data(file_path=file_path)

        df = self.clean_data(df=df)
        self.connector.create_tables()

        contained_ids = self.request_processed_ids()

        if not contained_ids:
            self.store_data(df=df)
            if verbose:
                print(" -> Recreated: ", Transaction_Categories_Table.__tablename__)
        else:
            if verbose:
                print(" -> ", Transaction_Categories_Table.__tablename__,
                      " already exists!")
        return

    # endregion

    # region [private]
    # endregion

    # region [class]
    # endregion

    # region [properties]
    # endregion

    # region [protected]
    def read_data(self,file_path: Path,
                  file_format: str = ".json") -> pd.DataFrame:

        if file_format == ".json":
            with open(file_path) as f:
                DEFAULT_CATEGORIES = json.load(f)
            rows = []
            for lvl1_key, lvl1_val in DEFAULT_CATEGORIES.items():
                for lvl2_key,lvl2_val in lvl1_val.items():
                    for ele in lvl2_val:
                        rows.append([lvl1_key,lvl2_key,ele])

            df = pd.DataFrame(rows,columns=["category_1","category_2","category_3"])
            df = df.reset_index()
            df = df.rename({"index":"category_id"},axis="columns")
        else:
            raise Exception("Unknown File Format!")

        return df

    def clean_data(self,df: pd.DataFrame) -> pd.DataFrame:
        return df

    def request_processed_ids(self) -> List[str]:
        with Session(self.connector.create_sql_engine()) as session:
            stmt = select(Transaction_Categories_Table.category_id).distinct()
            df = pd.read_sql(stmt,session.bind)
            res = list(df[self.primary_key_col].tolist())
        return res

    def store_data(self, df: pd.DataFrame,
                   if_exists:str='replace') -> None:
        df.to_sql(con=self.connector.create_sql_engine(),
                  name=self.target_table_name,
                  if_exists=if_exists,
                  index=False)
        return

    # endregion

    # region [overwrite]
    # endregion
