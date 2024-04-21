import os
from typing import Any
from dotenv import load_dotenv,find_dotenv
from sqlalchemy import create_engine

from money_map.models.orm_models import Base

class  MySQLConnector:

    # region [init]
    # Instance variables and instance methods are associated with the object.
    #endregion

    # region [public]
    # Public variables and public methods are accessible outside the object + (staticmethods).
    def create_db_url(self,user:str,pw:str,host:str,db:str) -> str:
        return f"mysql+pymysql://{user}:{pw}@{host}/{db}"

    def create_sql_engine(self) -> Any:
        load_dotenv(find_dotenv())
        return create_engine(self.create_db_url(user=os.getenv("USER"),
                                                pw=os.getenv("PASSWORD"),
                                                host=os.getenv("HOST"),
                                                db=os.getenv("DATABASE")))

    def create_tables(self) -> None:
        Base.metadata.create_all(bind=self.create_sql_engine())
        return

    #endregion

    # region [private]
    #endregion

    # region [class]
    # Class variables and class methods are associated with a class (classmethods).
    #endregion

    # region [properties]
    #endregion

    # region [protected]
    # Protected variables and protected methods, accessed by class they are in and inheriting classes.
    #endregion

    # region [overwrite]
    # Overwrite variables and methods given by parent class.
    #endregion
