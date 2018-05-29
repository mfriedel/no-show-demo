import time
import warnings
import pandas as pd
from helpers.logger import get_logger
from helpers.modeling import load_latest_model
from helpers.data import normalize_gender, batches
from helpers.schema import PREDICTION_SCHEMA, FEATURES, OUTPUT
from skafossdk import DataSourceType, Skafos
warnings.filterwarnings("ignore")


## Load the most recent noshow model that has been pre-trained and stored on s3
start = time.time()
log = get_logger('no-show-scoring')
ska = Skafos()
log.info("Loading latest pre-trained no-show predictor")
latest_model = load_latest_model(engine=ska.engine)


## Pull in upcoming appts from no_shows keyspace
log.info("Loading upcoming appointments")
ska.engine.create_view("upcoming_appointments",
    {"keyspace": "no_shows", "table": "upcoming"},
    DataSourceType.Cassandra).result()
upcoming = ska.engine.query("SELECT * FROM upcoming_appointments").result().get('data')
log.info("Loaded {} upcoming appointments to score".format(len(upcoming)))


## Load data to a pandas dataframe and perform some normalization steps
log.info("Prepping data for scoring")
df = normalize_gender(pd.DataFrame(upcoming))
X = df[FEATURES]


## Score the batch of appointments
log.info("Scoring all appointments")
df['no_show_likelihood'] = [p[1] for p in latest_model.predict_proba(X)]

## Create prediction records
predictions = df[OUTPUT]
predictions['appointment_day'] = predictions['appointment_day'].apply(lambda x: str(x)[:10])
predictions = predictions.to_dict(orient='records')
print(predictions[:3], flush=True)

## Write predictions to cassandra table - accessible via REST API
log.info("Writing batches of predictions out to the database")
for batch in batches(predictions, 50):
  res = ska.engine.save(PREDICTION_SCHEMA, batch).result()
  log.debug(res)

finish = time.time()
log.info(f"Done - loaded and scored appointments in {finish-start} seconds")
