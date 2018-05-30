import os
import pickle
from datetime import datetime
from s3fs.core import S3FileSystem
from skafossdk import DataSourceType

# CONSTANTS
S3_BUCKET = "skafos.demo.healthcare"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
ACC_THRESHOLD = float(os.getenv("ACC_THRESHOLD", 0.6))


def build_model_path(model_id, name):
  return f"s3://{S3_BUCKET}/no_show_models/{model_id}/{name}.pkl"


def load_model(model_id, name):
  model_path = build_model_path(model_id, name)
  s3 = S3FileSystem(anon=False)
  with s3.open(model_path, mode="rb") as f:
    return pickle.loads(f.read())


def load_latest_model(engine):
  """Retrieve the most recent noshow model and load from s3 Storage"""
  engine.create_view("models", {"table": "noshow_models"}, DataSourceType.Cassandra).result()
  record = engine.query("SELECT * FROM models ORDER BY date_created DESC LIMIT 1").result().get('data')
  if record is not None:
    latest_model = record[0]
    return load_model(latest_model["model_id"], latest_model["name"])
  else:
    raise ValueError("No model found in your user's noshow_models table. Have you run the training job yet?")


def model_record(model_id, acc, model_type, name):
  """Generate a model version record from model info"""
  return {
      "date_created": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]),
      "model_id": model_id,
      "name": name,
      "status": "production" if acc > ACC_THRESHOLD else "weak",
      "model_type": model_type,
      "training_accuracy": acc
  }


# Functions for saving out model
def save_model(model, model_id, acc, model_type="RandomForestClassifier", name="no_show_model"):
  """Take an sklearn model, serialize it and store on s3 for later use"""
  model_path = build_model_path(model_id, name)
  s3 = S3FileSystem(anon=False)
  with s3.open(model_path, mode="wb") as f:
    f.write(pickle.dumps(model))

  # Return a model record:
  return model_record(
      model_id=model_id, acc=acc, model_type=model_type, name=name
  )
