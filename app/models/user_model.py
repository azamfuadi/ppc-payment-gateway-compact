from enum import unique
# from sqlalchemy import MetaData, Table
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from app import engine, Base, app, session
import uuid
import random
from passlib.hash import sha256_crypt


class Admins(Base):
    __tablename__ = 'Admins'
    userid = Column(String(32), primary_key=True, nullable=False)
    fullname = Column(String(150), nullable=True)
    username = Column(String(100), nullable=True, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True, unique=True)
    role = Column(String(50), nullable=False)
    confirmed = Column(Boolean, nullable=False)
    confirmedAt = Column(DateTime(), nullable=True)
    loginAt = Column(DateTime(), nullable=True)

Base.metadata.create_all(engine, checkfirst=True)

not_exists = session.query(Admins).filter_by(role='Super Admin').first() is None

if not_exists :
    uid = uuid.uuid4().hex
    random_code = random.randint(100000,999999)
    admin_name = "S_Admin_"+str(random_code)
    superAdmin = Admins(
            userid=uid,
            fullname="Super Admin",
            username=admin_name,
            password=sha256_crypt.encrypt('superadmin123'),
            role="Super Admin",
            confirmed=True
        )
    session.add(superAdmin)
    session.commit()
