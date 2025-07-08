import sys
import os
import pandas as pd
import joblib

sys.path.append('../../ML/ml_model')
from model_forest import HybridProjectSuccessModel

class ModelService:
    def __init__(self):
        self.model = None
        self.users_df = None
        self.is_initialized = False
    
    def initialize(self):
        try:
            self.model = HybridProjectSuccessModel()
            
            # Carregar modelo
            model_path = '../../ML/ml_model/trained_model.joblib'
            if os.path.exists(model_path):
                self.model.model = joblib.load(model_path)
                self.model.is_trained = True
            else:
                print(f"Modelo não encontrado: {model_path}")
                return False
            
            # Carregar dados de usuários
            users_path = '../../ML/datas/usuarios_dataset.csv'
            if os.path.exists(users_path):
                self.users_df = pd.read_csv(users_path)
            else:
                print(f"Dados não encontrados: {users_path}")
                return False
            
            self.is_initialized = True
            print(f"Modelo inicializado: {len(self.users_df)} usuários")
            return True
            
        except Exception as e:
            print(f"Erro ao inicializar: {e}")
            return False
    
    def predict_project(self, project_data, cargo):
        if not self.is_initialized:
            return {'error': 'Modelo não inicializado'}
        
        return self.model.predict_single_project(project_data, cargo)
    
    def get_users(self):
        if not self.is_initialized:
            return None
        return self.users_df
    
    def get_user_by_id(self, user_id):
        if not self.is_initialized:
            return None
        
        user = self.users_df[self.users_df['Usuario_ID'] == user_id]
        return user.iloc[0] if not user.empty else None