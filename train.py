import os
import uuid
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from skafossdk import *
from helpers.logger import get_logger
from helpers.schema import MODEL_SCHEMA
from helpers.modeling import save_model
from helpers.data import fetch_data
warnings.filterwarnings("ignore")


TEST_SIZE = float(os.getenv('TEST_SIZE', 0.2))
log = get_logger('no-show-training')
ska = Skafos()

## Grab data using the Skafos data engine
log.info("Fetching historical appointment data over a 3 month range!")
X, y = fetch_data(engine=ska.engine, location="S3")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=42)


## Build model on training data
# NOTE: Perform more feature and hyperparameter tuning
log.info("Building a basic random forest classifier with balanced classes")
rf = RandomForestClassifier(class_weight='balanced')
rf.fit(X_train, y_train)


## Evaluate basic model performance
log.info("Checking basic model performance on some test data")
y_preds = rf.predict(X_test)
y_scores = [p[1] for p in rf.predict_proba(X_test)]
model_accuracy = accuracy_score(y_test, y_preds)
model_auc = roc_auc_score(y_test, y_scores)
log.info(f"Accuracy: {model_accuracy} \n ROC_AUC: {model_auc}")


## Refit final model
log.info("Training final model")
rf_final = RandomForestClassifier(class_weight='balanced')
rf_final.fit(X, y)


## Save Model to s3 and store a record in the database to access most recent model
log.info("Dumping trained model to s3 and saving a model version record in cassandra")
model_id = str(uuid.uuid4())
record = save_model(model=rf_final, model_id=model_id, acc=model_accuracy,
    model_type="RandomForestClassifier", name="no_show_model")

ska.engine.save(MODEL_SCHEMA, [record]).result()

log.info(f"Done - saved out trained no-show model '{model_id}'")
