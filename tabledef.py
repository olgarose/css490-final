from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey, Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///tutorial.db', echo=True)
Base= declarative_base()

class User(Base):
	__tablename__ = "users"

	username = Column(String, primary_key=True)
	password = Column(String)
	email = Column(String)
	fname = Column(String)
	lname = Column(String)

	def __init__(self, username, password, email, fname, lname):
		self.username = username
		self.password = password
		self.email = email
		self.fname = fname
		self.lname = lname

Base.metadata.create_all(engine)