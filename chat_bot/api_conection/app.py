from flask import Flask, request, jsonify, session
import sys
import os
import uuid
from datetime import datetime
import pandas as pd
import joblib

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ML', 'ml_model'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ML', 'datas'))

from model_forest import HybridProjectSuccessModel

app = Flask(__name__)
app.secret_key = 'unified_api_secret_key_2024'

model = None
users_df = None

def load_models():
    global model, users_df
    try:
        model = HybridProjectSuccessModel()
        model_path = os.path.join('..', '..', 'ML', 'ml_model', 'trained_model.joblib')
        if os.path.exists(model_path):
            model.model = joblib.load(model_path)
            model.is_trained = True
            print("Modelo carregado")
        else:
            print(f"Modelo não encontrado: {model_path}")
            return False
        
        users_path = os.path.join('..', '..', 'ML', 'datas', 'usuarios_dataset.csv')
        if os.path.exists(users_path):
            users_df = pd.read_csv(users_path)
            print(f"Usuários carregados: {len(users_df)}")
        else:
            print(f"Dados não encontrados: {users_path}")
            return False
        
        return True
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        return False

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'API de Predição de Projetos',
        'status': 'ativa',
        'endpoints': {
            '/predict': 'Predição básica',
            '/predict-with-user': 'Predição personalizada',
            '/users': 'Listar usuários',
            '/users/cargo/<cargo>': 'Por cargo',
            '/recommend': 'Recomendações'
        },
        'modelo_ok': model is not None and model.is_trained
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if not model or not model.is_trained:
            return jsonify({'erro': 'Modelo não carregado'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        required = ['duracao', 'orcamento', 'equipe', 'recursos', 'cargo']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'erro': f'Faltando: {missing}'}), 400
        
        project_data = {
            'Duracao_meses': float(data['duracao']),
            'Orcamento_R$': float(data['orcamento']),
            'Tamanho_da_Equipe': int(data['equipe']),
            'RecursosDisponiveis': data['recursos'].lower()
        }
        
        result = model.predict_single_project(project_data, data['cargo'])
        
        if 'error' not in result:
            return jsonify({
                'tipo': 'basica',
                'probabilidade': f"{result['success_probability']}%",
                'predicao': result['prediction'],
                'confianca': result['confidence_level']
            })
        else:
            return jsonify({'erro': result['error']}), 500
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/predict-with-user', methods=['POST'])
def predict_with_user():
    try:
        if not model or not model.is_trained:
            return jsonify({'erro': 'Modelo não carregado'}), 500
        
        data = request.get_json()
        required = ['duracao', 'orcamento', 'tamanho_equipe', 'recursos', 'user_id']
        
        for field in required:
            if field not in data:
                return jsonify({'erro': f'Faltando: {field}'}), 400
        
        user = users_df[users_df['Usuario_ID'] == data['user_id']]
        if user.empty:
            return jsonify({'erro': f'Usuário {data["user_id"]} não encontrado'}), 404
        
        user_data = user.iloc[0]
        
        project_data = {
            'Duracao_meses': float(data['duracao']),
            'Orcamento_R$': float(data['orcamento']),
            'Tamanho_da_Equipe': int(data['tamanho_equipe']),
            'RecursosDisponiveis': data['recursos'].lower()
        }
        
        result = model.predict_single_project(project_data, user_data['Cargo'])
        
        if 'error' not in result:
            return jsonify({
                'tipo': 'personalizada',
                'ok': True,
                'usuario': {
                    'id': user_data['Usuario_ID'],
                    'nome': user_data['Nome'],
                    'cargo': user_data['Cargo']
                },
                'resultado': {
                    'probabilidade': result['success_probability'],
                    'predicao': result['prediction'],
                    'confianca': result['confidence_level']
                }
            })
        else:
            return jsonify({'ok': False, 'erro': result['error']}), 500
            
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        if users_df is not None:
            users = users_df.to_dict('records')
            return jsonify({
                'ok': True,
                'total': len(users),
                'usuarios': users
            })
        else:
            return jsonify({'ok': False, 'erro': 'Dados não disponíveis'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

@app.route('/users/cargo/<cargo>', methods=['GET'])
def get_users_by_cargo(cargo):
    try:
        if users_df is not None:
            users = users_df[users_df['Cargo'] == cargo]
            return jsonify({
                'ok': True,
                'cargo': cargo,
                'total': len(users),
                'usuarios': users.to_dict('records')
            })
        else:
            return jsonify({'ok': False, 'erro': 'Dados não disponíveis'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

@app.route('/recommend', methods=['POST'])
def recommend_users():
    try:
        if not model or not model.is_trained:
            return jsonify({'erro': 'Modelo não carregado'}), 500
            
        data = request.get_json()
        
        project_data = {
            'Duracao_meses': float(data['duracao']),
            'Orcamento_R$': float(data['orcamento']),
            'Tamanho_da_Equipe': int(data['tamanho_equipe']),
            'RecursosDisponiveis': data['recursos'].lower()
        }
        
        recs = []
        
        for _, user in users_df.iterrows():
            result = model.predict_single_project(project_data, user['Cargo'])
            
            if 'error' not in result:
                recs.append({
                    'id': user['Usuario_ID'],
                    'nome': user['Nome'],
                    'cargo': user['Cargo'],
                    'exp': user['Experiencia(anos)'],
                    'sucesso_hist': user['Sucesso_Medio(percentual)'],
                    'prob_projeto': result['success_probability']
                })
        
        recs.sort(key=lambda x: x['prob_projeto'], reverse=True)
        
        top_n = data.get('top_n', 10)
        return jsonify({
            'ok': True,
            'total': len(recs),
            'recomendacoes': recs[:top_n]
        })
        
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'modelo': model is not None and model.is_trained,
        'usuarios': users_df is not None
    })

if __name__ == '__main__':
    if load_models():
        print("API iniciada na porta 5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Erro: não foi possível carregar os modelos")