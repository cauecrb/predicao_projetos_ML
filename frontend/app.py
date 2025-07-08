from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = 'frontend_secret_key_2024'

# Configuração da API backend
API_BASE_URL = 'http://localhost:5000/api'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/predict', methods=['POST'])
def predict_proxy():
    """Proxy para a API backend"""
    try:
        data = request.get_json()
        response = requests.post(f'{API_BASE_URL}/predict', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'erro': f'Erro de comunicação: {str(e)}'}), 500

@app.route('/api/users')
def users_proxy():
    """Proxy para listar usuários"""
    try:
        response = requests.get(f'{API_BASE_URL}/users')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'erro': f'Erro de comunicação: {str(e)}'}), 500

if __name__ == '__main__':
    print("🌐 Frontend iniciado na porta 3000")
    print("📡 Conectando com API em: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=3000)