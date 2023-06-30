#################################################################################
#
#   Description : database base, engine, session connection
#
#################################################################################

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from sqlalchemy import MetaData


import urllib

Access_Params = ('postgresql://postgres:%s@localhost/vissim_db' %  urllib.parse.quote(r'a71m46', safe=''))

engine = create_engine(Access_Params, echo= True, max_overflow=10, pool_size=5)

Base = declarative_base()

metadata_obj = MetaData()


SessionLocal = sessionmaker(bind=engine)


