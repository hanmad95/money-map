import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any, Union


class Ingestor(ABC):

    # region [init]
    target_table_name:str
    primary_key_col:str
    connector:Any
    # endregion

    # region [public]
    @abstractmethod
    def ingest_data(self,
                    file_path: Union[Path,None],
                    verbose:bool
                    ) -> pd.DataFrame:
        pass
    # endregion

    # region [private]

    # endregion

    # region [class]
    # endregion

    # region [properties]
    # endregion

    # region [protected]
    @abstractmethod
    def read_data(self,
                  file_path: Path,
                  file_format: str
                  ) -> pd.DataFrame:
        pass

    @abstractmethod
    def clean_data(self,
                   data: pd.DataFrame
                   ) -> pd.DataFrame:
        pass

    @abstractmethod
    def request_processed_ids(self,
                              ) -> List[str]:
        pass

    @abstractmethod
    def store_data(self,
                   df: pd.DataFrame,
                   if_exists:str='append') -> None:
        pass



    # endregion

    # region [overwrite]
    # endregion
