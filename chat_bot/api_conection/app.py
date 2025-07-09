from flask import Flask, request, jsonify
import sys
import os
import pandas as pd
import joblib

sys.path.append('../../ML/ml_model')
from model_forest import HybridProjectSuccessModel

app = Flask(__name__)
app.secret_key = 'api_key_123'

model = None
users = None

def load_stuff():
    global model, users
    try:
        model = HybridProjectSuccessModel()
        model_file = '../../ML/ml_model/trained_model.joblib'
        if os.path.exists(model_file):
            model.model = joblib.load(model_file)
            model.is_trained = True
        else:
            return False
        
        users_file = '../../ML/datas/usuarios_dataset.csv'
        if os.path.exists(users_file):
            users = pd.read_csv(users_file)
        else:
            return False
        
        return True
    except:
        return False

@app.route('/')
def home():
    return {'status': 'ok', 'model_loaded': model is not None}

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return {'error': 'model not loaded'}, 500
    
    data = request.json
    if not data:
        return {'error': 'no data'}, 400
    
    required = ['duracao', 'orcamento', 'equipe', 'recursos', 'cargo']
    for field in required:
        if field not in data:
            return {'error': f'missing {field}'}, 400
    
    project = {
        'Duracao_meses': float(data['duracao']),
        'Orcamento_R$': float(data['orcamento']),
        'Tamanho_da_Equipe': int(data['equipe']),
        'RecursosDisponiveis': data['recursos'].lower()
    }
    
    result = model.predict_single_project(project, data['cargo'])
    
    if 'error' in result:
        return {'error': result['error']}, 500
    
    return {
        'probability': f"{result['success_probability']}%",
        'prediction': result['prediction'],
        'confidence': result['confidence_level']
    }

@app.route('/users')
def get_users():
    if users is not None:
        return {'users': users.to_dict('records')}
    return {'error': 'no users'}, 500

@app.route('/users/cargo/<cargo>')
def users_by_cargo(cargo):
    if users is not None:
        filtered = users[users['Cargo'] == cargo]
        return {'users': filtered.to_dict('records')}
    return {'error': 'no users'}, 500

if __name__ == '__main__':
    if load_stuff():
        app.run(debug=True, port=5000)
    else:
        print("Failed to load")