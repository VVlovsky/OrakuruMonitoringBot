# -*- coding: utf-8 -*-

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bot.config import DATABASE_NAME

Base = declarative_base()
engine = create_engine(r'sqlite:///%s' % DATABASE_NAME, echo=True)
session = sessionmaker(bind=engine)()