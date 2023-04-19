import datetime
import random
import itertools

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, select, func, text
from sqlalchemy.ext.automap import automap_base
import getpass



USERNAME = getpass.getuser()




connection_string = f"postgresql+psycopg2://{USERNAME}:@localhost:5432/{USERNAME}"
engine = create_engine(connection_string)
Session = sessionmaker(engine)

creation_query = """CREATE table if not exists Books(
book_id SERIAL NOT NULL PRIMARY KEY,
title varchar(100) not null,
author varchar(100) NULL,
published int,
date_added date not null,
date_deleted date NULL
);


CREATE table if not exists Borrows(
borrow_id SERIAL NOT NULL PRIMARY KEY,
book_id int not null,
FOREIGN KEY (book_id) REFERENCES Books (book_id),
date_start date not null,
date_end date NULL,
user_id int not null
);
"""

with Session() as session:
    session.execute(text(creation_query))
    session.commit()