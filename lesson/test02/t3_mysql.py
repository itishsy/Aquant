import pandas as pd
import sqlalchemy
from t2_pandas import data_k_gen

engine = sqlalchemy.create_engine('mysql+pymysql://root:root@127.0.0.1:3306/pandas')
data = data_k_gen()
data.to_sql(name='test', con=engine, if_exists='replace')

df = pd.read_sql_table('test', engine.connect())
print(df)

def save_to_table(df, table_name):
    df.to_sql(name=table_name, con=engine, if_exists='replace')