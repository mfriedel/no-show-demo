## Schema for no show model and predictions
## These get stored in the user's namespace (left blank so it defaults to namespace of project)

# Table to store trained no show models
MODEL_SCHEMA = {
    "table_name": "noshow_models",
    "options": {
        "primary_key": ["name", "date_created"],
        "order_by": ["date_created desc"]
    },
    "columns": {
        "date_created": "timestamp",
        "model_id": "uuid",
        "name": "text",
        "status": "text",
        "model_type": "text",
        "training_accuracy": "float"
    }
}

# Table to store predictions on upcoming appointments
PREDICTION_SCHEMA = {
  "table_name": "predictions",
  "options": {
    "primary_key": ["appointment_day", "no_show_likelihood", "appointment_id"],
    "order_by": ["no_show_likelihood desc"]
  },
  "columns": {
    "appointment_id": "string",
    "patient_id": "string",
    "appointment_day": "date",
    "no_show_likelihood": "float"
  }
}

## Other constants needed throughout the project

# Model features and y-label used for training the no-show model
FEATURES = ['age_group', 'alcoholism', 'hypertension', 'diabetes', 'handicap',
            'gender', 'dayofweek', 'month', 'scholarship', 'sms_received']

LABEL = 'no_show'

OUTPUT = list(PREDICTION_SCHEMA['columns'].keys())
