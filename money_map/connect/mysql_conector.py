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
    def create_db_url(self,user:str,pw:str,host:str,db:str,port:int) -> str:
        '''Generate MYSQL Database Connection URL

        Parameters
        ----------
        user : str
            Username
        pw : str
            Password
        host : str
            Hostname
        db : str
            Database Name

        Returns
        -------
        str
           Connection URL
        '''
        return f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db}"

    def create_sql_engine(self) -> Any:
        '''Create SQLAlchemy Engine

        Returns
        -------
        Any
            SQLAlchemy Engine
        '''
        load_dotenv(find_dotenv())
        return create_engine(self.create_db_url(user=os.getenv("MYSQL_USER"),
                                                pw=os.getenv("MYSQL_PASSWORD"),
                                                host=os.getenv("MYSQL_HOST"),
                                                db=os.getenv("MYSQL_DATABASE"),
                                                port=int(os.getenv("MYSQL_PORT"))))

    def create_tables(self) -> None:
        ''' Creates all tables in defined database, if not existing.
        '''
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
