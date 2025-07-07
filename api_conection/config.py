import os

class Config:
    
    # Configurações do Flask
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    MODEL_PATH = os.path.join('..', 'ml_model', 'trained_model.joblib')
    
    # Configurações do modelo
    REQUIRED_FEATURES = [
        'Duração(meses)',
        'Orçamento(R$)', 
        'Tamanho daEquipe',
        'RecursosDisponíveis',
        'cargoFuncionario'
    ]
    
    RECURSOS_MAP = {
        'baixo': 0,
        'médio': 1, 
        'alto': 2
    }
    
    # Configurações de resposta
    CONFIDENCE_THRESHOLDS = {
        'alta': 0.7,
        'media': 0.6
    }