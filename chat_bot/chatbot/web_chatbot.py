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
    
    # Análise de duração
    if project['Duracao_meses'] > 18:
        suggestions.append({
            'categoria': 'Duração do Projeto',
            'problema': f'Projeto muito longo ({project["Duracao_meses"]} meses). Projetos longos têm maior risco de falha.',
            'sugestao': 'Divida o projeto em fases menores de 6-12 meses cada. Implemente entregas incrementais.',
            'impacto': 'Crítico'
        })
    elif project['Duracao_meses'] > 12:
        suggestions.append({
            'categoria': 'Duração do Projeto',
            'problema': f'Projeto longo ({project["Duracao_meses"]} meses). Risco moderado de mudanças de escopo.',
            'sugestao': 'Considere marcos intermediários a cada 3-4 meses para validação e ajustes.',
            'impacto': 'Alto'
        })
    
    # Análise de orçamento
    if project['Orcamento_R$'] < 30000:
        suggestions.append({
            'categoria': 'Orçamento',
            'problema': f'Orçamento muito baixo (R$ {project["Orcamento_R$"]:,.2f}). Pode comprometer a qualidade.',
            'sugestao': 'Reavalie o escopo do projeto ou aumente o orçamento em pelo menos 50%. Considere terceirização de partes não críticas.',
            'impacto': 'Crítico'
        })
    elif project['Orcamento_R$'] < 50000:
        suggestions.append({
            'categoria': 'Orçamento',
            'problema': f'Orçamento limitado (R$ {project["Orcamento_R$"]:,.2f}). Pode gerar restrições técnicas.',
            'sugestao': 'Priorize funcionalidades essenciais. Considere desenvolvimento em fases com orçamento adicional.',
            'impacto': 'Alto'
        })
    elif project['Orcamento_R$'] < 100000:
        suggestions.append({
            'categoria': 'Orçamento',
            'problema': f'Orçamento moderado (R$ {project["Orcamento_R$"]:,.2f}). Planejamento cuidadoso necessário.',
            'sugestao': 'Mantenha reserva de contingência de 15-20% para imprevistos.',
            'impacto': 'Médio'
        })
    
    # Análise de equipe
    if project['Tamanho_da_Equipe'] == 1:
        suggestions.append({
            'categoria': 'Tamanho da Equipe',
            'problema': 'Equipe de apenas 1 pessoa. Alto risco de dependência única e sobrecarga.',
            'sugestao': 'Adicione pelo menos mais 1-2 membros. Considere mentoria ou suporte técnico externo.',
            'impacto': 'Crítico'
        })
    elif project['Tamanho_da_Equipe'] == 2:
        suggestions.append({
            'categoria': 'Tamanho da Equipe',
            'problema': 'Equipe pequena (2 pessoas). Risco de gargalos e falta de especialização.',
            'sugestao': 'Considere adicionar um terceiro membro com habilidades complementares.',
            'impacto': 'Alto'
        })
    elif project['Tamanho_da_Equipe'] > 10:
        suggestions.append({
            'categoria': 'Tamanho da Equipe',
            'problema': f'Equipe muito grande ({project["Tamanho_da_Equipe"]} pessoas). Pode gerar problemas de comunicação.',
            'sugestao': 'Divida em sub-equipes de 3-5 pessoas cada. Implemente estrutura de liderança clara.',
            'impacto': 'Alto'
        })
    
    # Análise de recursos
    if project['RecursosDisponiveis'] == 'baixo':
        suggestions.append({
            'categoria': 'Recursos Disponíveis',
            'problema': 'Recursos limitados podem impactar qualidade e prazos.',
            'sugestao': 'Negocie acesso a ferramentas essenciais. Considere parcerias ou aluguel de recursos temporários.',
            'impacto': 'Alto'
        })
    elif project['RecursosDisponiveis'] == 'médio':
        suggestions.append({
            'categoria': 'Recursos Disponíveis',
            'problema': 'Recursos moderados requerem planejamento cuidadoso.',
            'sugestao': 'Otimize o uso de recursos existentes. Planeje aquisições com antecedência.',
            'impacto': 'Médio'
        })
    
    # Análise baseada na experiência do usuário
    if user['Experiencia(anos)'] < 2:
        suggestions.append({
            'categoria': 'Experiência da Equipe',
            'problema': f'Líder com pouca experiência ({user["Experiencia(anos)"]} anos). Risco de decisões inadequadas.',
            'sugestao': 'Considere mentoria de profissional sênior. Implemente revisões técnicas regulares.',
            'impacto': 'Alto'
        })
    elif user['Experiencia(anos)'] < 5:
        suggestions.append({
            'categoria': 'Experiência da Equipe',
            'problema': f'Experiência moderada ({user["Experiencia(anos)"]} anos). Pode precisar de suporte em decisões complexas.',
            'sugestao': 'Mantenha canal de comunicação com especialistas sêniores para consultas.',
            'impacto': 'Médio'
        })
    
    # Análise do histórico de sucesso
    if user['Sucesso_Medio(percentual)'] < 60:
        suggestions.append({
            'categoria': 'Histórico de Performance',
            'problema': f'Histórico de sucesso baixo ({user["Sucesso_Medio(percentual)"]}%). Risco elevado.',
            'sugestao': 'Implemente acompanhamento semanal rigoroso. Considere co-liderança ou supervisão adicional.',
            'impacto': 'Crítico'
        })
    elif user['Sucesso_Medio(percentual)'] < 75:
        suggestions.append({
            'categoria': 'Histórico de Performance',
            'problema': f'Histórico de sucesso moderado ({user["Sucesso_Medio(percentual)"]}%). Margem para melhoria.',
            'sugestao': 'Analise projetos anteriores para identificar padrões de falha. Implemente lições aprendidas.',
            'impacto': 'Médio'
        })
    
    # Sugestões gerais baseadas na combinação de fatores
    risk_factors = 0
    if project['Duracao_meses'] > 12: risk_factors += 1
    if project['Orcamento_R$'] < 50000: risk_factors += 1
    if project['Tamanho_da_Equipe'] < 3: risk_factors += 1
    if project['RecursosDisponiveis'] == 'baixo': risk_factors += 1
    if user['Experiencia(anos)'] < 3: risk_factors += 1
    
    if risk_factors >= 3:
        suggestions.append({
            'categoria': 'Risco Geral do Projeto',
            'problema': f'Múltiplos fatores de risco identificados ({risk_factors} fatores). Probabilidade de falha elevada.',
            'sugestao': 'Considere reavaliar o projeto completamente. Implemente metodologia ágil com entregas frequentes.',
            'impacto': 'Crítico'
        })
    elif risk_factors >= 2:
        suggestions.append({
            'categoria': 'Risco Geral do Projeto',
            'problema': f'Alguns fatores de risco presentes ({risk_factors} fatores). Monitoramento necessário.',
            'sugestao': 'Implemente reuniões de status semanais e marcos de validação mensais.',
            'impacto': 'Alto'
        })
    
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