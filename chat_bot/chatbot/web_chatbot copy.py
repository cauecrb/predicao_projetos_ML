from flask import Flask, render_template, request, jsonify, session
import sys
import os
import pandas as pd
import joblib
from datetime import datetime
import uuid

sys.path.append('../../ML/ml_model')
from model_forest import HybridProjectSuccessModel

app = Flask(__name__)
app.secret_key = 'web_key'

model = None
users = None

def init():
    global model, users
    try:
        model = HybridProjectSuccessModel()
        
        if not model.load_data('../../ML/datas/projetos_dataset.csv', '../../ML/datas/usuarios_dataset.csv'):
            return False
        
        if not model.load_model('../../ML/ml_model/trained_model.joblib'):
            return False
        
        users = pd.read_csv('../../ML/datas/usuarios_dataset.csv')
        return True
    except:
        return False

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['history'] = []
    return render_template('chatbot.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    
    required = ['duracao', 'orcamento', 'tamanho_equipe', 'recursos', 'user_id']
    for field in required:
        if field not in data:
            return {'sucesso': False, 'erro': f'Campo obrigatório: {field}'}, 400
    
    user_id = int(data['user_id'])
    user = users[users['Usuario_ID'] == user_id]
    if user.empty:
        return {'sucesso': False, 'erro': 'Usuário não encontrado'}, 404
    
    user_data = user.iloc[0]
    
    project = {
        'Duracao_meses': float(data['duracao']),
        'Orcamento_R$': float(data['orcamento']),
        'Tamanho_da_Equipe': int(data['tamanho_equipe']),
        'RecursosDisponiveis': data['recursos'].lower()
    }
    
    result = model.predict_single_project(project, user_data['Cargo'])
    
    if 'error' in result:
        return {'sucesso': False, 'erro': result['error']}, 500
    
    response = {
        'usuario': {
            'id': int(user_data['Usuario_ID']),
            'nome': str(user_data['Nome']),
            'cargo': str(user_data['Cargo']),
            'experiencia': int(user_data['Experiencia(anos)']),
            'sucesso_historico': float(user_data['Sucesso_Medio(percentual)'])
        },
        'predicao_base': {
            'probabilidade_sucesso': result['success_probability']
        },
        'predicao_ajustada': {
            'probabilidade_sucesso': result['success_probability'],
            'ajuste_usuario': 0
        }
    }
    
    if result['success_probability'] < 60:
        response['sugestoes_melhoria'] = get_suggestions(project, user_data)
    
    if 'history' not in session:
        session['history'] = []
    
    session['history'].append({
        'timestamp': datetime.now().isoformat(),
        'projeto': project,
        'resultado': response
    })
    
    return {'sucesso': True, 'resultado': response}

def get_suggestions(project, user):
    suggestions = []
    
    if project['Duracao_meses'] > 12:
        suggestions.append({'type': 'Duration', 'text': 'Consider shorter phases'})
    
    if project['Orcamento_R$'] < 50000:
        suggestions.append({'type': 'Budget', 'text': 'Increase budget or reduce scope'})
    
    if project['Tamanho_da_Equipe'] < 3:
        suggestions.append({'type': 'Team', 'text': 'Add more team members'})
    
    if project['RecursosDisponiveis'] == 'baixo':
        suggestions.append({'type': 'Resources', 'text': 'Improve available resources'})
    
    return suggestions

@app.route('/api/users')
def get_users():
    return {'sucesso': True, 'usuarios': users.to_dict('records')}

@app.route('/api/history')
def get_history():
    history = session.get('history', [])
    return {'sucesso': True, 'historico': history}

if __name__ == '__main__':
    if init():
        print("Server started: http://localhost:5001")
        app.run(debug=True, port=5001)
    else:
        print("Failed to start")