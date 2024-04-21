# stdlib
import os
from pathlib import Path
from typing import List,Any,Union

from attrs import define
import pandas as pd
import json
from dotenv import load_dotenv,find_dotenv

from sqlalchemy import create_engine, select, inspect
from sqlalchemy.orm import Session

# custom class
from money_map.models.orm_models import Transaction_Categories_Table, Base
from money_map.models.categories import TRANSACTION_CATEGORIES
from money_map.ingestion.ingestor import Ingestor

# TODO:  Add connector and replace not required functions
# =============================================================================
# Transaction Categories
# =============================================================================

@define
class Categories_Ingestor(Ingestor):

    # reion [init]
    target_table_name:str = Transaction_Categories_Table.__tablename__
    primary_key_col:str = inspect(Transaction_Categories_Table).primary_key[0].name
    # endregion

    # region [public]
    def ingest_data(self,file_path:Union[Path,None],verbose:bool=True)-> None:

        if file_path is not None:
            df = self.read_data(file_path=file_path)
        else:
            df = self.read_data_internally()

        df = self.clean_data(df=df)
        self._create_tables()

        contained_ids = self.request_processed_ids()

        if not contained_ids:
            self.store_data(df=df)
            if verbose:
                print(" -> Init: ", Transaction_Categories_Table.__tablename__)
        else:
            if verbose:
                print(" -> ", Transaction_Categories_Table.__tablename__,
                      " already exists!")
        return

    # endregion

    # region [private]
    def _create_db_url(self,user:str,pw:str,host:str,db:str) -> str:
        return f"mysql+pymysql://{user}:{pw}@{host}/{db}"

    def _create_sql_engine(self) -> Any:
        load_dotenv(find_dotenv())
        return create_engine(self._create_db_url(user=os.getenv("USER"),
                                                pw=os.getenv("PASSWORD"),
                                                host=os.getenv("HOST"),
                                                db=os.getenv("DATABASE")))

    def _create_tables(self) -> None:
        Base.metadata.create_all(bind=self._create_sql_engine())
        return
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

    def read_data_internally(self) -> pd.DataFrame:

        rows = []
        for lvl1_key, lvl1_val in TRANSACTION_CATEGORIES.items():
            for lvl2_key,lvl2_val in lvl1_val.items():
                for ele in lvl2_val:
                    rows.append([lvl1_key,lvl2_key,ele])

        df = pd.DataFrame(rows,columns=["category_1","category_2","category_3"])
        df = df.reset_index()
        df = df.rename({"index":"category_id"},axis="columns")

        return df

    def clean_data(self,df: pd.DataFrame) -> pd.DataFrame:
        return df

    def request_processed_ids(self) -> List[str]:
        with Session(self._create_sql_engine()) as session:
            stmt = select(Transaction_Categories_Table.category_id).distinct()
            df = pd.read_sql(stmt,session.bind)
            res = list(df[self.primary_key_col].tolist())
        return res

    def store_data(self, df: pd.DataFrame,
                   if_exists:str='replace') -> None:
        df.to_sql(con=self._create_sql_engine(),
                  name=self.target_table_name,
                  if_exists=if_exists,
                  index=False)
        return

    # endregion

    # region [overwrite]
    # endregion
