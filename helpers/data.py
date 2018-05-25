import sys
import pandas as pd
from skafossdk import DataSourceType
from .schema import FEATURES, LABEL


def normalize_gender(df):
  X = df.copy()
  X["gender"] = X.gender.apply(lambda x: 1 if x == "M" else 0)
  return X


def fetch_data(engine):
  """Use the Skafos data engine to pull in historic appointment data."""
  res = engine.create_view(
      'appt',
      {'keyspace': 'no_shows', 'table': 'appointments'},
      DataSourceType.Cassandra
  ).result()
  query = 'SELECT * FROM appt'
  return make_dataframe(engine.query(query).result().get('data'))


def make_dataframe(data):
  """Generate a pandas dataframe from the Skafos dataengine result"""
  if data is not None:
    df = normalize_gender(pd.DataFrame(data))
    return clean_and_split(df)
  else:
    print("No data returned from data engine - killing job!", flush=True)
    sys.exit(0)


def clean_and_split(df: pd.DataFrame):
  """Take a pandas dataframe clean and split into X and y."""
  X = df[FEATURES]
  y = df[LABEL]
  return X, y


def batches(iterable, n=10):
  """divide a single list into a list of lists of size n"""
  batchLen = len(iterable)
  for ndx in range(0, batchLen, n):
    yield list(iterable[ndx:min(ndx + n, batchLen)])