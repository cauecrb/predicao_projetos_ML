from flask import Flask, request, jsonify, session
import sys
import os
import uuid
from datetime import datetime
import pandas as pd
import joblib

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_model'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'datas'))

from model_forest import HybridProjectSuccessModel

app = Flask(__name__)
app.secret_key = 'unified_api_secret_key_2024'

# Modelo global
model = None
users_df = None

def load_models():
    global model, users_df
    try:
        # Modelo híbrido
        model = HybridProjectSuccessModel()
        model_path = os.path.join('..', 'ml_model', 'trained_model.joblib')
        if os.path.exists(model_path):
            model.model = joblib.load(model_path)
            model.is_trained = True
            print("✅ Modelo híbrido carregado")
        else:
            print(f"❌ Modelo não encontrado: {model_path}")
            return False
        
        # Dados de usuários
        users_path = os.path.join('..', 'datas', 'usuarios_dataset.csv')
        if os.path.exists(users_path):
            users_df = pd.read_csv(users_path)
            print(f"✅ Dados de usuários carregados: {len(users_df)} usuários")
        else:
            print(f"❌ Dados de usuários não encontrados: {users_path}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar modelos: {e}")
        return False

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'API de Predição de Projetos',
        'status': 'ativa',
        'endpoints': {
            '/predict': 'Predição básica de projeto',
            '/predict-with-user': 'Predição com usuário específico',
            '/users': 'Listar usuários',
            '/users/cargo/<cargo>': 'Usuários por cargo',
            '/recommend': 'Recomendar usuários para projeto'
        },
        'modelo_carregado': model is not None and model.is_trained
    })

# Endpoint básico (mantém compatibilidade)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if model is None or not model.is_trained:
            return jsonify({'erro': 'Modelo não carregado'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        required_fields = ['duracao', 'orcamento', 'equipe', 'recursos', 'cargo']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({'erro': f'Campos obrigatórios: {missing}'}), 400
        
        project_data = {
            'Duracao_meses': float(data['duracao']),
            'Orcamento_R$': float(data['orcamento']),
            'Tamanho_da_Equipe': int(data['equipe']),
            'RecursosDisponiveis': data['recursos'].lower()
        }
        
        result = model.predict_single_project(project_data, data['cargo'])
        
        if 'error' not in result:
            return jsonify({
                'tipo': 'predicao_basica',
                'probabilidade_sucesso': f"{result['success_probability']}%",
                'predicao': result['prediction'],
                'confianca': result['confidence_level']
            })
        else:
            return jsonify({'erro': result['error']}), 500
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Endpoint com usuário específico
@app.route('/predict-with-user', methods=['POST'])
def predict_with_user():
    try:
        if model is None or not model.is_trained:
            return jsonify({'erro': 'Modelo não carregado'}), 500
        
        data = request.get_json()
        required_fields = ['duracao', 'orcamento', 'tamanho_equipe', 'recursos', 'user_id']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'erro': f'Campo obrigatório ausente: {field}'}), 400
        
        # Buscar usuário
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
                'tipo': 'predicao_personalizada',
                'sucesso': True,
                'usuario': {
                    'id': user_data['Usuario_ID'],
                    'nome': user_data['Nome'],
                    'cargo': user_data['Cargo']
                },
                'resultado': {
                    'probabilidade_sucesso': result['success_probability'],
                    'predicao': result['prediction'],
                    'confianca': result['confidence_level']
                }
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        if users_df is not None:
            users = users_df.to_dict('records')
            return jsonify({
                'sucesso': True,
                'total': len(users),
                'usuarios': users
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Base de usuários não disponível'
            }), 500
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/users/cargo/<cargo>', methods=['GET'])
def get_users_by_cargo(cargo):
    try:
        if users_df is not None:
            users = users_df[users_df['Cargo'] == cargo]
            return jsonify({
                'sucesso': True,
                'cargo': cargo,
                'total': len(users),
                'usuarios': users.to_dict('records')
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Base de usuários não disponível'
            }), 500
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/recommend', methods=['POST'])
def recommend_users():
    try:
        if model is None or not model.is_trained:
            return jsonify({'erro': 'Modelo não carregado'}), 500
            
        data = request.get_json()
        
        project_data = {
            'Duracao_meses': float(data['duracao']),
            'Orcamento_R$': float(data['orcamento']),
            'Tamanho_da_Equipe': int(data['tamanho_equipe']),
            'RecursosDisponiveis': data['recursos'].lower()
        }
        
        recommendations = []
        
        for _, user in users_df.iterrows():
            result = model.predict_single_project(project_data, user['Cargo'])
            
            if 'error' not in result:
                recommendations.append({
                    'usuario_id': user['Usuario_ID'],
                    'nome': user['Nome'],
                    'cargo': user['Cargo'],
                    'experiencia': user['Experiencia(anos)'],
                    'sucesso_historico': user['Sucesso_Medio(percentual)'],
                    'probabilidade_sucesso_projeto': result['success_probability']
                })
        
        recommendations.sort(key=lambda x: x['probabilidade_sucesso_projeto'], reverse=True)
        
        top_n = data.get('top_n', 10)
        return jsonify({
            'sucesso': True,
            'total_recomendacoes': len(recommendations),
            'recomendacoes': recommendations[:top_n]
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'modelo_carregado': model is not None and model.is_trained,
        'usuarios_carregados': users_df is not None,
        'total_usuarios': len(users_df) if users_df is not None else 0
    })

if __name__ == '__main__':
    if load_models():
        print("🚀 Iniciando API Unificada (porta 5000)")
        print("📊 Endpoints disponíveis:")
        print("   - GET  /              : Informações da API")
        print("   - POST /predict       : Predição básica")
        print("   - POST /predict-with-user : Predição personalizada")
        print("   - GET  /users         : Listar usuários")
        print("   - GET  /users/cargo/<cargo> : Usuários por cargo")
        print("   - POST /recommend     : Recomendar usuários")
        print("   - GET  /health        : Status da API")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Erro: Não foi possível carregar os modelos")