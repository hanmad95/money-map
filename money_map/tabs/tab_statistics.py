from typing import Tuple,List

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


# =============================================================================
# Tattistic Tab: Process Transactions Labeled DataFrame
# =============================================================================

def define_daily_balance(labeled_transactions:pd.DataFrame
                        ) -> pd.DataFrame:

    daily_balance_df = (labeled_transactions.groupby(["booking_date"])
                    .agg(min_balance_after_booking=("balance_after_booking","min"),
                        mean_balance_after_booking=("balance_after_booking","mean"),
                        max_balance_after_booking=("balance_after_booking","max"))
                    .reset_index())

    return daily_balance_df


def define_monthly_transactions(labeled_transactions:pd.DataFrame,
                                ignore_categories_3:List[str] = ["Umlagerungen"]
                                 ) -> Tuple[pd.DataFrame, pd.DataFrame]:

    # filter out certain categories 3rd level
    monthly_df = labeled_transactions.loc[~labeled_transactions["category_3"].isin(ignore_categories_3)]

    # define day, month, year based on booking_date
    monthly_df = monthly_df.sort_values(by="booking_date")
    monthly_df["booking_date"] = pd.to_datetime(monthly_df["booking_date"],format="%Y-%m-%d")
    monthly_df["value_date"] = pd.to_datetime(monthly_df["value_date"],format="%Y-%m-%d")
    monthly_df["day"] = monthly_df["booking_date"].dt.day
    monthly_df["month"] = monthly_df["booking_date"].dt.month
    monthly_df["year"] = monthly_df["booking_date"].dt.year

    # group by month and category id
    monthly_df = (monthly_df.groupby(["year","month","category_id"])
                            .agg({"amount":"sum",
                                  "balance_after_booking":"mean",
                                  "category_1":"first",
                                  "category_2":"first",
                                  "category_3":"first"})
                            .reset_index())

    # define year-month column for plots
    monthly_df["year-month"] = monthly_df["year"].astype(str) + "-" + monthly_df["month"].astype(str)
    monthly_df_total = monthly_df[["year-month","amount"]].groupby('year-month').sum()
    monthly_df_total["amount"] = monthly_df_total["amount"].astype(int)

    return monthly_df, monthly_df_total

# =============================================================================
# Statistic Tab: Plots
# =============================================================================

def plot_monthly_transactions(monthly_df:pd.DataFrame,
                              monthly_df_total:pd.DataFrame,
                              title:str="Monthly Transactions",
                              category_level:str="category_3"
                            ) ->go.Figure:

    fig = px.bar(monthly_df,x="year-month",y="amount",color=category_level,height=1000)
    fig.add_trace(go.Scatter(
        x=monthly_df_total .index,
        y=monthly_df_total['amount'],
        text=monthly_df_total ['amount'],
        mode='text',
        textposition='top center',
        textfont=dict(
            size=18,
        ),
        showlegend=False
    ))
    fig.update_layout(title=title,
                      xaxis_title='Year-Month',
                      yaxis_title='Amount [€]')

    return fig

def plot_daily_balance(daily_df:pd.DataFrame,
                       title:str="Balance"
                      ) ->go.Figure:

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_df["booking_date"],
                             y=daily_df["min_balance_after_booking"],
                             mode='lines+markers',
                             name="min_balance_after_booking"))
    fig.add_trace(go.Scatter(x=daily_df["booking_date"],
                             y=daily_df["max_balance_after_booking"],
                             mode='lines+markers',
                             name="max_balance_after_booking"))
    fig.update_layout(title=title,
                    xaxis_title='Booking Date',
                    yaxis_title='Balance [€]')
    return fig

# =============================================================================
# Statistics Tab Main
# =============================================================================

def compute_tab_statistics(labeled_transactions: pd.DataFrame,
                           tab_title:str = "Overview") -> None:

    #define title
    st.header(tab_title)

    # define multiselect (target account)
    unique_iban_sender = labeled_transactions["sender_iban"].unique().tolist()
    target_accounts = None
    target_accounts = st.multiselect("Select Target Accounts",unique_iban_sender)

    # loop over selection
    if target_accounts:
        for target_account in target_accounts:
            st.write("------")
            st.subheader((f":orange[Account: {target_account}]" ))
            current_labeled_transactions = (labeled_transactions.loc[
                                                labeled_transactions["sender_iban"]==target_account])

            # create monthly transactions chart
            monthly_df, monthly_df_total = define_monthly_transactions(
                                                labeled_transactions=current_labeled_transactions)
            fig_monthly = plot_monthly_transactions(monthly_df=monthly_df,
                                                    monthly_df_total=monthly_df_total,
                                                    title=f"Monthly Transactions: {target_account}")
            st.plotly_chart(fig_monthly, use_container_width=True)

            # create daily balance chart
            daily_balance = define_daily_balance(labeled_transactions=current_labeled_transactions)
            fig_daily_balance = plot_daily_balance(daily_df=daily_balance,title=f"Daily Balance: {target_account}")
            st.plotly_chart(fig_daily_balance, use_container_width=True)
            st.write("------")

    return
