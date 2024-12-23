import sqlalchemy as db
from app import engine, Base
from sqlalchemy import Column, Float, String, Integer, TIMESTAMP

class transaction(Base):
    __tablename__ = 'Transaction'
    id = Column(Integer, primary_key=True)
    Time = Column(TIMESTAMP, nullable=False)
    MerchantPaymentID = Column(String(255),nullable=False)
    Account = Column(String(255),nullable=False)
    Method = Column(String(255), nullable=False)
    Amount = Column(Float, nullable=False)
    Point = Column(Float, nullable=False)

Base.metadata.create_all(engine, checkfirst=True)
