import time
import warnings
import pandas as pd
from helpers.logger import get_logger
from helpers.modeling import load_latest_model
from helpers.data import normalize_gender, batches, fetch_upcoming, save_predictions
from helpers.schema import PREDICTION_SCHEMA, FEATURES, OUTPUT
from skafossdk import DataSourceType, Skafos
warnings.filterwarnings("ignore")


## Load the most recent noshow model that has been pre-trained and stored on s3
start = time.time()
log = get_logger('no-show-scoring')
ska = Skafos()
log.info("Loading latest pre-trained no-show predictor!")
latest_model = load_latest_model(engine=ska.engine, keyspace='4d5ba8393483f7a07a2ba4ca')


## Pull in upcoming appts from no_shows keyspace
log.info("Loading upcoming appointments")
upcoming = fetch_upcoming(engine=ska.engine, location="S3")
log.info("Loaded {} upcoming appointments to score".format(len(upcoming)))


## Load data to a pandas dataframe and perform some normalization steps
log.info("Prepping data for scoring")
df = normalize_gender(upcoming)
X = df[FEATURES]


## Score the batch of appointments
log.info("Scoring all appointments")
df['no_show_likelihood'] = [p[1] for p in latest_model.predict_proba(X)]

## Create prediction records
predictions = df[OUTPUT]
predictions['appointment_day'] = predictions['appointment_day'].apply(lambda x: str(x)[:10])

# Write predictions to S3 or Cassandra
save_predictions(ska.engine, location='S3', predictions=predictions, log=log)
log.info("Writing out predictions")


finish = time.time()
log.info(f"Done - loaded and scored appointments in {finish-start} seconds")
