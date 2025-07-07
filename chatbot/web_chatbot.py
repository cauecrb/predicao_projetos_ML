from flask import Flask, render_template, request, jsonify, session
import sys
import os
from datetime import datetime
import uuid
import pandas as pd
import joblib

sys.path.append('../ml_model')
sys.path.append('../datas')

from model_forest import HybridProjectSuccessModel

app = Flask(__name__)
app.secret_key = 'chatbot_secret_key_2024'

model = None
users_df = None

def initialize_model():
    global model, users_df
    try:
        model = HybridProjectSuccessModel()
        
        users_path = '../datas/usuarios_dataset.csv'
        projects_path = '../datas/projetos_dataset.csv'
        
        if not os.path.exists(users_path) or not os.path.exists(projects_path):
            print(f"Dados não encontrados")
            return False
        
        if not model.load_data(projects_path, users_path):
            print("Erro ao carregar dados")
            return False
        
        model_path = '../ml_model/trained_model.joblib'
        if os.path.exists(model_path):
            if not model.load_model(model_path):
                print(f"Erro ao carregar modelo")
                return False
        else:
            print(f"Modelo não encontrado")
            return False
        
        users_df = pd.read_csv(users_path)
        print(f"Sistema inicializado: {len(users_df)} usuários")
            
        return True
    except Exception as e:
        print(f"Erro na inicialização: {e}")
        return False

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['conversation_history'] = []
    
    return render_template('chatbot.html')

@app.route('/api/predict', methods=['POST'])
def predict_project():
    try:
        data = request.get_json()
        
        required_fields = ['duracao', 'orcamento', 'tamanho_equipe', 'recursos', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'erro': f'Campo ausente: {field}'}), 400
        
        user_id = int(data['user_id'])
        user = users_df[users_df['Usuario_ID'] == user_id]
        if user.empty:
            return jsonify({'erro': f'Usuário {user_id} não encontrado'}), 404
        
        user_data = user.iloc[0]
        
        project_data = {
            'Duracao_meses': float(data['duracao']),
            'Orcamento_R$': float(data['orcamento']),
            'Tamanho_da_Equipe': int(data['tamanho_equipe']),
            'RecursosDisponiveis': data['recursos'].lower()
        }
        
        result = model.predict_single_project(project_data, user_data['Cargo'])
        
        if 'error' not in result:
            response_data = {
                'usuario': {
                    'id': int(user_data['Usuario_ID']),
                    'nome': str(user_data['Nome']),
                    'cargo': str(user_data['Cargo']),
                    'experiencia': int(user_data['Experiencia(anos)']),
                    'sucesso_historico': float(user_data['Sucesso_Medio(percentual)'])
                },
                'predicao_base': {
                    'resultado': result['prediction'],
                    'probabilidade_sucesso': result['success_probability']
                },
                'predicao_ajustada': {
                    'resultado': result['prediction'],
                    'probabilidade_sucesso': result['success_probability'],
                    'ajuste_usuario': 0
                }
            }
            
            if result['success_probability'] < 60:
                response_data['sugestoes_melhoria'] = generate_suggestions(
                    project_data, user_data, result['success_probability']
                )
            
            if 'conversation_history' not in session:
                session['conversation_history'] = []
            
            session['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'projeto': {
                    'Duração(meses)': int(data['duracao']),
                    'Orçamento(R$)': float(data['orcamento']),
                    'Tamanho daEquipe': int(data['tamanho_equipe']),
                    'RecursosDisponíveis': data['recursos']
                },
                'resultado': response_data
            })
            
            return jsonify({
                'sucesso': True,
                'resultado': response_data
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

def generate_suggestions(project_data, user_data, probability):
    suggestions = []
    
    duracao = project_data['Duracao_meses']
    if duracao > 12:
        suggestions.append({
            'categoria': 'Duração',
            'problema': 'Projeto muito longo ( maior que 12 meses)',
            'sugestao': 'Dividir em fases menores',
            'impacto': 'Alto'
        })
    elif duracao < 2:
        suggestions.append({
            'categoria': 'Duração',
            'problema': 'Projeto muito curto (meonr que 2 meses)',
            'sugestao': 'Verificar escopo e viabilidade',
            'impacto': 'Médio'
        })
    
    orcamento = project_data['Orcamento_R$']
    if orcamento < 50000:
        suggestions.append({
            'categoria': 'Orçamento',
            'problema': 'Orçamento limitado',
            'sugestao': 'Reavaliar escopo ou buscar recursos',
            'impacto': 'Alto'
        })
    
    tamanho_equipe = project_data['Tamanho_da_Equipe']
    if tamanho_equipe < 3:
        suggestions.append({
            'categoria': 'Equipe',
            'problema': 'Equipe pequena (menor que 3)',
            'sugestao': 'Aumentar equipe ou reduzir escopo',
            'impacto': 'Alto'
        })
    elif tamanho_equipe > 10:
        suggestions.append({
            'categoria': 'Equipe',
            'problema': 'Equipe grande (maior que 10)',
            'sugestao': 'Dividir em sub-equipes',
            'impacto': 'Médio'
        })
    
    recursos = project_data['RecursosDisponiveis']
    if recursos == 'limitado':
        suggestions.append({
            'categoria': 'Recursos',
            'problema': 'Recursos limitados',
            'sugestao': 'Priorizar funcionalidades essenciais',
            'impacto': 'Alto'
        })
    
    experiencia = int(user_data['Experiencia(anos)'])
    if experiencia < 2:
        suggestions.append({
            'categoria': 'Liderança',
            'problema': 'Pouca experiência',
            'sugestao': 'Considerar mentoria',
            'impacto': 'Alto'
        })
    
    sucesso_historico = float(user_data['Sucesso_Medio(percentual)'])
    if sucesso_historico < 70:
        suggestions.append({
            'categoria': 'Liderança',
            'problema': 'Baixa taxa de sucesso',
            'sugestao': 'Implementar revisões frequentes',
            'impacto': 'Alto'
        })
    
    if probability < 40:
        suggestions.append({
            'categoria': 'Geral',
            'problema': 'Probabilidade muito baixa',
            'sugestao': 'Reavaliar projeto completamente',
            'impacto': 'Crítico'
        })
    
    return suggestions

@app.route('/api/users')
def get_users():
    try:
        if users_df is not None:
            users = []
            for _, user in users_df.iterrows():
                users.append({
                    'Usuario_ID': int(user['Usuario_ID']),
                    'Nome': str(user['Nome']),
                    'Cargo': str(user['Cargo']),
                    'Experiencia(anos)': int(user['Experiencia(anos)']),
                    'Sucesso_Medio(percentual)': float(user['Sucesso_Medio(percentual)']),
                    'Historico_de_Projetos': str(user['Historico_de_Projetos'])
                })
            
            return jsonify({
                'sucesso': True,
                'usuarios': users
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Base de usuários indisponível'
            }), 500
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/users/cargo/<cargo>')
def get_users_by_cargo(cargo):
    try:
        if users_df is not None:
            users_filtered = users_df[users_df['Cargo'] == cargo]
            users = []
            for _, user in users_filtered.iterrows():
                users.append({
                    'Usuario_ID': int(user['Usuario_ID']),
                    'Nome': str(user['Nome']),
                    'Cargo': str(user['Cargo']),
                    'Experiencia(anos)': int(user['Experiencia(anos)']),
                    'Sucesso_Medio(percentual)': float(user['Sucesso_Medio(percentual)']),
                    'Historico_de_Projetos': str(user['Historico_de_Projetos'])
                })
            
            return jsonify({
                'sucesso': True,
                'usuarios': users
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Base de usuários indisponível'
            }), 500
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/recommend', methods=['POST'])
def recommend_users():
    try:
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
                    'usuario_id': int(user['Usuario_ID']),
                    'nome': str(user['Nome']),
                    'cargo': str(user['Cargo']),
                    'experiencia': int(user['Experiencia(anos)']),
                    'sucesso_historico': float(user['Sucesso_Medio(percentual)']),
                    'probabilidade_sucesso_projeto': float(result['success_probability'])
                })
        
        recommendations.sort(key=lambda x: x['probabilidade_sucesso_projeto'], reverse=True)
        
        return jsonify({
            'sucesso': True,
            'recomendacoes': recommendations[:10]
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/history')
def get_history():
    try:
        history = session.get('conversation_history', [])
        return jsonify({
            'sucesso': True,
            'historico': history
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

if __name__ == '__main__':
    if initialize_model():
        print("Sistema iniciado com sucesso!")
        print("Acesse: http://localhost:5001")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        print("Erro ao inicializar sistema.")