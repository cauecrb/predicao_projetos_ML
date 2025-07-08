from flask import Flask
from flask_cors import CORS
from routes.predict import predict_bp
from routes.users import users_bp
from routes.health import health_bp
from services.model_service import ModelService

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Inicializar serviços
model_service = ModelService()
if not model_service.initialize():
    print("Erro: Não foi possível inicializar o modelo")
    exit(1)

# Registrar blueprints
app.register_blueprint(predict_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(health_bp, url_prefix='/api')

# Tornar serviços disponíveis globalmente
app.model_service = model_service

if __name__ == '__main__':
    print("🚀 API Backend iniciada na porta 5000")
    app.run(debug=True, host='0.0.0.0', port=5000)