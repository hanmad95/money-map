import datetime

from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy.types import Date,String,Float,Integer


class Base(DeclarativeBase):
    pass

# =============================================================================
# Transaction Categories
# =============================================================================

class Transaction_Categories_Table(Base):
    '''Available Categories for labeling the transactions based on participants.

    Parameters
    ----------
    Base : sqlalchemy.orm.Base
        sqlalchemy.orm.Base
    '''
    __tablename__ = "transaction_categories"

    category_id: Mapped[int] = mapped_column(Integer(), nullable=False, primary_key=True)
    category_1: Mapped[str] = mapped_column(String(100), nullable=False)
    category_2: Mapped[str] = mapped_column(String(100), nullable=False)
    category_3: Mapped[str] = mapped_column(String(100), nullable=False)

# =============================================================================
# Transactions
# =============================================================================

class Participants_Labeled_Table(Base):
    '''Unique participants (sender & receiver & purpose) which are labeled.
       Used for assigning categories to similar transactions.

    Parameters
    ----------
    Base : sqlalchemy.orm.Base
        sqlalchemy.orm.Base
    '''
    __tablename__ = "participants_labeled"

    row_number: Mapped[int] = mapped_column(Integer(),nullable=False,primary_key=True,autoincrement=True)
    sender_bank_name: Mapped[str] = mapped_column(String(80),nullable=False)
    sender_iban: Mapped[str] = mapped_column(String(40),nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(80),nullable=False)
    receiver_iban: Mapped[str] = mapped_column(String(40),nullable=False)
    booking_text: Mapped[str] = mapped_column(String(40),nullable=False)
    purpose_char: Mapped[str] = mapped_column(String(140),nullable=False)
    category_id: Mapped[int] = mapped_column(Integer(),nullable=False)
    category_1: Mapped[str] = mapped_column(String(100), nullable=False)
    category_2: Mapped[str] = mapped_column(String(100), nullable=False)
    category_3: Mapped[str] = mapped_column(String(100), nullable=False)

# =============================================================================
# Transactions
# =============================================================================

class Transactions_Table(Base):
    '''Contains raw transaction data.

    Parameters
    ----------
    Base : sqlalchemy.orm.Base
       sqlalchemy.orm.Base
    '''
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(40),nullable=False,primary_key=True)
    sender_account_type: Mapped[str] = mapped_column(String(40),nullable=False)
    sender_iban: Mapped[str] = mapped_column(String(40),nullable=False)
    sender_bic: Mapped[str] = mapped_column(String(40),nullable=True)
    sender_bank_name: Mapped[str] = mapped_column(String(80),nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(80),nullable=False)
    receiver_iban: Mapped[str] = mapped_column(String(40),nullable=False)
    receiver_bic: Mapped[str] = mapped_column(String(40),nullable=True)
    booking_date: Mapped[datetime.date] = mapped_column(Date(),nullable=False)
    value_date: Mapped[datetime.date] = mapped_column(Date(),nullable=False)
    amount: Mapped[float] = mapped_column(Float(),nullable=False)
    currency: Mapped[str] = mapped_column(String(20),nullable=False)
    booking_text: Mapped[str] = mapped_column(String(40),nullable=False)
    purpose: Mapped[str] = mapped_column(String(140),nullable=False)
    balance_after_booking: Mapped[float] = mapped_column(Float(),nullable=False)
    notes: Mapped[str] = mapped_column(String(40),nullable=True)
    default_category: Mapped[str] = mapped_column(String(80),nullable=True)
    tax_relevant: Mapped[str] = mapped_column(String(40),nullable=True)
    creditor_id: Mapped[str] = mapped_column(String(40),nullable=True)
    mandate_reference: Mapped[str] = mapped_column(String(40),nullable=True)
    purpose_char: Mapped[str] = mapped_column(String(140),nullable=False)

# =============================================================================
# Transactions Labeled
# =============================================================================

class Transactions_Labeled_Table(Base):
    '''Contains labeled transactions, based on Transactions_Table &
       Participants_Labeled_Table.

    Parameters
    ----------
    Base : sqlalchemy.orm.Base
        sqlalchemy.orm.Base
    '''
    __tablename__ = "transactions_labeled"

    transaction_id: Mapped[str] = mapped_column(String(40),nullable=False,primary_key=True)
    sender_account_type: Mapped[str] = mapped_column(String(40),nullable=False)
    sender_iban: Mapped[str] = mapped_column(String(40),nullable=False)
    sender_bic: Mapped[str] = mapped_column(String(40),nullable=True)
    sender_bank_name: Mapped[str] = mapped_column(String(80),nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(80),nullable=False)
    receiver_iban: Mapped[str] = mapped_column(String(40),nullable=False)
    receiver_bic: Mapped[str] = mapped_column(String(40),nullable=True)
    booking_date: Mapped[datetime.date] = mapped_column(Date(),nullable=False)
    value_date: Mapped[datetime.date] = mapped_column(Date(),nullable=False)
    amount: Mapped[float] = mapped_column(Float(),nullable=False)
    currency: Mapped[str] = mapped_column(String(20),nullable=False)
    booking_text: Mapped[str] = mapped_column(String(40),nullable=False)
    purpose: Mapped[str] = mapped_column(String(140),nullable=False)
    balance_after_booking: Mapped[float] = mapped_column(Float(),nullable=False)
    notes: Mapped[str] = mapped_column(String(40),nullable=True)
    default_category: Mapped[str] = mapped_column(String(80),nullable=True)
    tax_relevant: Mapped[str] = mapped_column(String(40),nullable=True)
    creditor_id: Mapped[str] = mapped_column(String(40),nullable=True)
    mandate_reference: Mapped[str] = mapped_column(String(40),nullable=True)
    purpose_char: Mapped[str] = mapped_column(String(140),nullable=False)
    category_id: Mapped[int] = mapped_column(Integer(),nullable=False)
    category_1: Mapped[str] = mapped_column(String(100), nullable=False)
    category_2: Mapped[str] = mapped_column(String(100), nullable=False)
    category_3: Mapped[str] = mapped_column(String(100), nullable=False)
