import os
import psycopg2
from sqlalchemy import create_engine

# Specify database information -----------------------------------------------------------------------------------------
# path to postgresql bin folder
pgpath = r';C:/Program Files/PostgreSQL/9.5/bin'
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = 'cph_data'
# Database connections
engine = create_engine(f'postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}?gssencmode=disable')
import pandas as pd
df = pd.read_csv('C:/Users/NM12LQ/Downloads/adresse.csv')
df.columns = [c.lower() for c in df.columns] #postgres doesn't like capitals or spaces




df.to_sql("adres", engine)