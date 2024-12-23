import sqlalchemy as db
from app import engine, Base
from sqlalchemy import Column, String, Integer, LargeBinary


class credentials(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    Primary_Server_Address = Column(String(255), nullable=False)
    Payment_Gateway_Address = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    company_name = Column(String(100), nullable=True)
    company_email = Column(String(100), nullable=True)
    company_phone = Column(String(25), nullable=True)
    company_address = Column(String(255), nullable=True)
    company_logo = Column(String(255), nullable=True)
    logo_file = Column(LargeBinary, nullable=True)
    multiplier = Column(Integer, nullable=False)
    min_input = Column(Integer, nullable=False)
    max_input = Column(Integer, nullable=False)
    PayPay_API_KEY = Column(String(255), nullable=False)
    PayPay_API_SECRET = Column(String(255), nullable=False)
    PayPay_MERCHANT_ID = Column(String(255), nullable=False)
    BT_ENVIRONMENT = Column(String(255), nullable=False)
    BT_MERCHANT_ID = Column(String(255), nullable=False)
    BT_PUBLIC_KEY = Column(String(255), nullable=False)
    BT_PRIVATE_KEY = Column(String(255), nullable=False)
    BT_APP_SECRET_KEY = Column(String(255), nullable=False)
    PayPal_Client_Id = Column(String(255), nullable=False)
    PayPal_Secret = Column(String(255), nullable=False)
    mssg = Column(String(255))
    mssg_JP = Column(String(255))
    mssg2 = Column(String(255))
    mssg2_JP = Column(String(255))
    main_message = Column(String(255))
    colour = Column(String(255))


Base.metadata.create_all(engine, checkfirst=True)
