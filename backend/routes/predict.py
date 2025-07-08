from flask import Blueprint, request, jsonify, current_app

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['POST'])
def predict():
    try:
        model_service = current_app.model_service
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
        
        result = model_service.predict_project(project_data, data['cargo'])
        
        if 'error' not in result:
            return jsonify({
                'sucesso': True,
                'probabilidade': result['success_probability'],
                'predicao': result['prediction'],
                'confianca': result['confidence_level']
            })
        else:
            return jsonify({'erro': result['error']}), 500
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@predict_bp.route('/predict-with-user', methods=['POST'])
def predict_with_user():
    try:
        model_service = current_app.model_service
        data = request.get_json()
        
        required = ['duracao', 'orcamento', 'tamanho_equipe', 'recursos', 'user_id']
        for field in required:
            if field not in data:
                return jsonify({'erro': f'Faltando: {field}'}), 400
        
        user_data = model_service.get_user_by_id(data['user_id'])
        if user_data is None:
            return jsonify({'erro': f'Usuário {data["user_id"]} não encontrado'}), 404
        
        project_data = {
            'Duracao_meses': float(data['duracao']),
            'Orcamento_R$': float(data['orcamento']),
            'Tamanho_da_Equipe': int(data['tamanho_equipe']),
            'RecursosDisponiveis': data['recursos'].lower()
        }
        
        result = model_service.predict_project(project_data, user_data['Cargo'])
        
        if 'error' not in result:
            return jsonify({
                'sucesso': True,
                'usuario': {
                    'id': int(user_data['Usuario_ID']),
                    'nome': str(user_data['Nome']),
                    'cargo': str(user_data['Cargo'])
                },
                'resultado': {
                    'probabilidade': result['success_probability'],
                    'predicao': result['prediction'],
                    'confianca': result['confidence_level']
                }
            })
        else:
            return jsonify({'erro': result['error']}), 500
            
    except Exception as e:
        return jsonify({'erro': str(e)}), 500