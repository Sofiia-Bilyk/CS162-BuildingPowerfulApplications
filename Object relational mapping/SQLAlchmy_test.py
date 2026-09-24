import sqlalchemy

from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:', echo = True)

engine.connect()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key = True)
	name = Column(String)
	insurance_id = Column(Integer)

	def __repr__(self):
		return "<User(id={0}, name={1}, insurance_id={2})>".format(self.id, self.name, self.insurance_id)


class Insurance(Base):
	__tablename__ = 'insurance'
	id = Column(Integer, ForeignKey('users.insurance_id'), primary_key = True)
	claim_id = Column(Integer)
	users = relationship(User)

Base.metadata.create_all(engine)

user = User(id = 1, name='sterne', insurance_id=1234)

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
session.add(user)
session.commit()

print(session.query(User).filter_by(name='sterne').first())

from sqlalchemy import Table, MetaData
metadata = MetaData()
users = Table('users', metadata, autoload=True, autoload_with=engine)

print(repr(users))