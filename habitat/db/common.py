#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/15 13:06:31

u"""
... Put description here ...
"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

from _utils.cfg_utility import CfgUtility

cfg = CfgUtility(r"D:\pgsql_pinguicula.cfg")

db_engine = cfg.get_value('db_engine')
user      = cfg.get_value('user')
password  = cfg.get_value('password')
host      = cfg.get_value('host')
port      = int(cfg.get_value('port'))
database  = cfg.get_value('database')

conn_string = "%s://%s:%s@%s:%d/%s" % (db_engine, user, password, host, port, database)

Engine = create_engine(conn_string, echo = False)
Session = sessionmaker(bind = Engine)
Base = declarative_base()
