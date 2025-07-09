import os

DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

MODEL_PATH = '../../ML/ml_model/trained_model.joblib'

REQUIRED_FIELDS = ['duracao', 'orcamento', 'equipe', 'recursos', 'cargo']

RESOURCES = {'baixo': 0, 'médio': 1, 'alto': 2}

CONFIDENCE_HIGH = 0.7
CONFIDENCE_MED = 0.6