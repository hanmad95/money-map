import pandas as pd
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import and_

from money_map.models.orm_models import (Transactions_Table,
                                         Transactions_Labeled_Table,
                                         Participants_Labeled_Table)

# =============================================================================

def recreate_transactions_labeled(engine:Any,
                   target_table_name:str=Transactions_Labeled_Table.__tablename__,
                   chunksize:int=10000)->None:

    with Session(engine) as session:

        query = session.query(Transactions_Table,
                            Participants_Labeled_Table.category_id,
                            Participants_Labeled_Table.category_1,
                            Participants_Labeled_Table.category_2,
                            Participants_Labeled_Table.category_3
                            ).join(Participants_Labeled_Table,
                                   and_(
                        Transactions_Table.sender_bank_name==Participants_Labeled_Table.sender_bank_name,
                        Transactions_Table.sender_iban==Participants_Labeled_Table.sender_iban,
                        Transactions_Table.receiver_name==Participants_Labeled_Table.receiver_name,
                        Transactions_Table.receiver_iban==Participants_Labeled_Table.receiver_iban,
                        Transactions_Table.booking_text==Participants_Labeled_Table.booking_text,
                        Transactions_Table.purpose_char==Participants_Labeled_Table.purpose_char))

        for chunk in pd.read_sql(query.statement,session.bind,chunksize=chunksize):
            chunk.to_sql(con=session.bind,
                        name=target_table_name,
                        if_exists="replace",
                        chunksize=chunksize,
                        index=False)

    return

# =============================================================================
