import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
engine = None
Session = sqlalchemy.orm.sessionmaker()
def setup(sopel):
    global engine
    global Session
    engine = sqlalchemy.create_engine('sqlite:////home/googol/dBucket/dBucket.sqlite')
    Session.configure(bind = engine)
    Base.metadata.create_all(engine)
