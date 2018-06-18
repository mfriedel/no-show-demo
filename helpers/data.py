import os
import sys
import pandas as pd
from skafossdk import DataSourceType
from .schema import FEATURES, LABEL, PREDICTION_SCHEMA
from s3fs.core import S3FileSystem

# CONSTANTS
S3_BUCKET = "skafos.demo.healthcare"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
ACC_THRESHOLD = float(os.getenv("ACC_THRESHOLD", 0.6))


def normalize_gender(df):
    X = df.copy()
    X["gender"] = X.gender.apply(lambda x: 1 if x == "M" else 0)
    return X


def fetch_data(engine, location='Cassandra'):
    """Use the Skafos data engine to pull in historic appointment data."""

    if location == "S3":

        s3 = S3FileSystem(anon=False)
        key = f"s3://{S3_BUCKET}/data/past_appointments.csv"
        fetched_data = make_dataframe(data=pd.read_csv(s3.open(f'{key}',
                                                               mode='rb')))
    else:
        res = engine.create_view(
            'appt',
            {'keyspace': 'no_shows', 'table': 'appointments'},
            DataSourceType.Cassandra
        ).result()
        query = 'SELECT * FROM appt'
        fetched_data = make_dataframe(engine.query(query).result().get('data'))

    return fetched_data


def fetch_upcoming(engine, location='Cassandra'):
    """Use the Skafos data engine to pull in historic appointment data."""

    if location == "S3":

        s3 = S3FileSystem(anon=False)
        key = f"s3://{S3_BUCKET}/data/upcoming_appointments.csv"
        upcoming = pd.read_csv(s3.open(f'{key}', mode='rb'))

    else:
        ska.engine.create_view("upcoming_appointments",
                               {"keyspace": "no_shows", "table": "upcoming"},
                               DataSourceType.Cassandra).result()
        upcoming = pd.DataFrame(ska.engine.query("SELECT * FROM upcoming_appointments").result().get('data'))

    return upcoming


def save_predictions(engine, location='Cassandra', predictions=None, log=None):
    if location == 'S3':
        predictions = predictions[['appointment_id', 'patient_id', 'appointment_day', \
                                   'no_show_likelihood']].sort_values(by='no_show_likelihood', ascending=False)
        bytes_to_write = predictions.to_csv(None, index=False).encode()
        fs = S3FileSystem(key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY)
        with fs.open(f"s3://{S3_BUCKET}/scores/latest_scores.csv", 'wb') as f:
            f.write(bytes_to_write)
    else:
        predictions = predictions.to_dict(orient='records')
        print(predictions[:3], flush=True)
        for batch in batches(predictions, 200):
            res = engine.save(PREDICTION_SCHEMA, batch).result()
            log.debug(res)


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