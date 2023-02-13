from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()

class camuser(Base):
  __tablename__ = 'user'

  name = Column(String, primary_key=True, nullable=False)
  name_kor = Column(String, nullable=True)
  median = Column(String, nullable=True)
  mean = Column(String, nullable=True)
  central_median = Column(String, nullable=True)
  central_mean = Column(String, nullable=True)