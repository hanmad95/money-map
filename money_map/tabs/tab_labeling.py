from typing import Dict, Any

import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session

from money_map.models.orm_models import Participants_Labeled_Table

# ==============================================================================
# Labeling Tab: Add Data
# ==============================================================================

def add_labeled_transactions(_engine: Any,
                            current_unlabeled_transactions:Dict[str,str],
                            category_id:int,
                            category_1:str,
                            category_2:str,
                            category_3:str
                            ) -> None:
    # add new entry
    with Session(_engine) as session:
        new_entry = Participants_Labeled_Table(
                    sender_bank_name=current_unlabeled_transactions["sender_bank_name"],
                    sender_iban=current_unlabeled_transactions["sender_iban"],
                    receiver_name=current_unlabeled_transactions["receiver_name"],
                    receiver_iban=current_unlabeled_transactions["receiver_iban"],
                    booking_text=current_unlabeled_transactions["booking_text"],
                    purpose_char=current_unlabeled_transactions["purpose_char"],
                    category_id=category_id,
                    category_1=category_1,
                    category_2=category_2,
                    category_3=category_3)
        session.add(new_entry)
        session.commit()
    return


# =============================================================================
# Labeling Tab: Main
# =============================================================================

def compute_tab_labeling(unlabeled_transactions:pd.DataFrame,
                         categories_df:pd.DataFrame,
                         number_labeled_transactions:int,
                         engine:Any,
                         tab_title:str = "Assign Categories to Unique Transactions: "
                         ) -> None:

    st.header(tab_title)

    # add metrics
    col1, col2 = st.columns(2)
    col1.metric("Remaining Transactions", unlabeled_transactions.shape[0])
    col2.metric("Labeled Transactions", number_labeled_transactions)

    # case we have unlabeled data
    if unlabeled_transactions.shape[0] > 0:

        st.write("------")
        st.subheader("Please assign Categories to: ")
        current_unlabeled_transactions = unlabeled_transactions.iloc[0,:].to_dict()
        st.dataframe(unlabeled_transactions.iloc[0,:],use_container_width=True)


        # select category 1
        selected_category_1 = st.selectbox("Category 1", categories_df["category_1"].unique().tolist()
                                           ,placeholder="Choose an option")
        # select category 2
        temp_cat2_df = categories_df.loc[categories_df["category_1"]==selected_category_1]
        selected_category_2= st.selectbox("Category 2", temp_cat2_df["category_2"].unique().tolist()
                                          ,placeholder="Choose an option")

        # select category 3
        temp_cat3_df = temp_cat2_df.loc[temp_cat2_df["category_2"]==selected_category_2]
        selected_category_3 = st.selectbox("Category 3", temp_cat3_df["category_3"].unique().tolist()
                                           ,placeholder="Choose an option")

        # get selected category id
        temp_cat4_df = temp_cat3_df.loc[temp_cat3_df["category_3"]==selected_category_3]
        selected_category_id = temp_cat4_df["category_id"].tolist()
        assert len(selected_category_id) == 1
        selected_category_id = selected_category_id[0]


        if st.button("Submit"):
            add_labeled_transactions(_engine=engine,
                                    current_unlabeled_transactions=current_unlabeled_transactions,
                                    category_id=selected_category_id,
                                    category_1=selected_category_1,
                                    category_2=selected_category_2,
                                    category_3=selected_category_3)
            st.rerun()
