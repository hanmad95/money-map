import streamlit as st
import pandas as pd
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, exists

from money_map.connect.mysql_conector import MySQLConnector
from money_map.ingestion.categories_ingestion import Categories_Ingestor
from money_map.models.orm_models import (Transactions_Table,
                                         Transactions_Labeled_Table,
                                         Participants_Labeled_Table,
                                         Transaction_Categories_Table)
from money_map.tabs.tab_statistics import compute_tab_statistics
from money_map.tabs.tab_labeling import compute_tab_labeling

# ==============================================================================
# Fetch Data Functions
# ==============================================================================

@st.cache_data(ttl="1h")
def get_available_categories(_engine:Any) -> pd.DataFrame:
    with Session(_engine) as session:
        stmt = select(Transaction_Categories_Table)
        df = pd.read_sql(stmt, session.bind)
    return df

@st.cache_data(ttl="1h")
def get_labeled_transactions(_engine:Any) -> pd.DataFrame:
    with Session(_engine) as session:
        stmt = select(Transactions_Labeled_Table)
        df = pd.read_sql(stmt, session.bind)
    return df

def get_number_labeled_transactions(_engine:Any) -> int:
    with Session(_engine) as session:
        count = int(session.query(Participants_Labeled_Table).count())
    return count

def get_unlabeled_transactions(_engine:Any) -> pd.DataFrame:

    with Session(_engine) as session:

        stmt =select(Transactions_Table.sender_bank_name,
                     Transactions_Table.sender_iban,
                     Transactions_Table.receiver_name,
                     Transactions_Table.receiver_iban,
                     Transactions_Table.booking_text,
                     Transactions_Table.purpose_char
                     ).distinct()

        stmt = stmt.filter(~exists()
                           .where(
                            and_(
                Transactions_Table.sender_bank_name==Participants_Labeled_Table.sender_bank_name,
                Transactions_Table.sender_iban==Participants_Labeled_Table.sender_iban,
                Transactions_Table.receiver_name==Participants_Labeled_Table.receiver_name,
                Transactions_Table.receiver_iban==Participants_Labeled_Table.receiver_iban,
                Transactions_Table.booking_text==Participants_Labeled_Table.booking_text,
                Transactions_Table.purpose_char==Participants_Labeled_Table.purpose_char)))

        df = pd.read_sql(stmt, session.bind)
        df = df.sort_values(["receiver_name","purpose_char"])

    return df

# ==============================================================================
# init connection
# ==============================================================================

connector = MySQLConnector()
engine = connector.create_sql_engine()
connector.create_tables()

# ingest categories
categ_ingestor = Categories_Ingestor()
categ_ingestor.ingest_data_from_models() #read from models.categories.py


# ==============================================================================
# Streamlit Main
# ==============================================================================
st.set_page_config(layout="wide")
st.title("Money Map")

# init different tabs
tab_statistics, tab_labeling, tab_upload  = st.tabs(["View Statistics","Labeling", "Upload Data"])

# ==============================================================================
# TAB 1: Statistics
# ==============================================================================

with tab_statistics:
    labeled_transactions = get_labeled_transactions(_engine=engine)
    compute_tab_statistics(labeled_transactions=labeled_transactions)

# ==============================================================================
# TAB 2: Labeling
# ==============================================================================

with tab_labeling:

    # init available data
    categories_df = get_available_categories(_engine=engine)
    unlabeled_transactions = get_unlabeled_transactions(_engine=engine)
    number_labeled_transactions = get_number_labeled_transactions(_engine=engine)

    # compute tab
    compute_tab_labeling(unlabeled_transactions=unlabeled_transactions,
                         categories_df=categories_df,
                         number_labeled_transactions=number_labeled_transactions,
                         engine=engine)

# ==============================================================================
# TAB 3: Upload
# ==============================================================================

# TODO: Select Channels (Ingestion Mode)
#       Pop up File Upload file and after upload it should ingest it
