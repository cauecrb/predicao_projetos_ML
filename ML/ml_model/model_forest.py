import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import joblib
from datetime import datetime
import numpy as np

class HybridProjectSuccessModel:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.scaler = StandardScaler()
        self.features = []
        self.is_trained = False
        self.user_data = None
        
    def load_data(self, projects_path, users_path):
        try:
            # Carregar dados
            self.projects_df = pd.read_csv(projects_path)
            self.users_df = pd.read_csv(users_path)
            
            # Mapear nomes das colunas do CSV para nomes esperados pelo modelo
            column_mapping = {
                'duracao_meses': 'Duracao_meses',
                'orcamento': 'Orcamento_R$',
                'tamanho_equipe': 'Tamanho_da_Equipe',
                'recursos_disponiveis': 'RecursosDisponiveis',
                'cargo_responsavel': 'cargoFuncionario',
                'sucesso': 'Sucesso'
            }
            
            self.projects_df = self.projects_df.rename(columns=column_mapping)
            self._process_user_data()
            self.combined_df = self._combine_datasets()
            
            print(f"Dados carregados: {len(self.combined_df)} registros")
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def _process_user_data(self):
        users_processed = self.users_df.copy()
        
        # Extrair número de projetos e sucessos do histórico
        users_processed[['Sucessos', 'Total_Projetos']] = users_processed['Historico_de_Projetos'].str.extract(r'(\d+)/(\d+)')
        users_processed['Sucessos'] = users_processed['Sucessos'].astype(int)
        users_processed['Total_Projetos'] = users_processed['Total_Projetos'].astype(int)
        
        # Calcular taxa de sucesso real
        users_processed['Taxa_Sucesso_Real'] = users_processed['Sucessos'] / users_processed['Total_Projetos']
        
        # Criar mapeamento cargo -> dados do usuário
        self.user_data = {}
        for _, row in users_processed.iterrows():
            cargo = row['Cargo']
            if cargo not in self.user_data:
                self.user_data[cargo] = []
            
            self.user_data[cargo].append({
                'experiencia': row['Experiencia(anos)'],
                'total_projetos': row['Total_Projetos'],
                'taxa_sucesso': row['Taxa_Sucesso_Real'],
                'sucesso_medio': row['Sucesso_Medio(percentual)'] / 100
            })
    
    def _combine_datasets(self):
        combined = self.projects_df.copy()
        
        combined['Experiencia_Media_Cargo'] = 0.0
        combined['Projetos_Medios_Cargo'] = 0.0
        combined['Taxa_Sucesso_Cargo'] = 0.0
        combined['Sucesso_Medio_Cargo'] = 0.0
        
        for idx, row in combined.iterrows():
            cargo = row['cargoFuncionario']
            if cargo in self.user_data:
                users_cargo = self.user_data[cargo]
                
                combined.at[idx, 'Experiencia_Media_Cargo'] = np.mean([u['experiencia'] for u in users_cargo])
                combined.at[idx, 'Projetos_Medios_Cargo'] = np.mean([u['total_projetos'] for u in users_cargo])
                combined.at[idx, 'Taxa_Sucesso_Cargo'] = np.mean([u['taxa_sucesso'] for u in users_cargo])
                combined.at[idx, 'Sucesso_Medio_Cargo'] = np.mean([u['sucesso_medio'] for u in users_cargo])
        
        return combined
    
    def prepare_features(self):
        df = self.combined_df.copy()
        
        numeric_project_cols = ["Duracao_meses", "Orcamento_R$", "Tamanho_da_Equipe"]
        numeric_user_cols = ["Experiencia_Media_Cargo", "Projetos_Medios_Cargo", 
                           "Taxa_Sucesso_Cargo", "Sucesso_Medio_Cargo"]
        categorical_cols = ["RecursosDisponiveis", "cargoFuncionario"]
        
        for col in categorical_cols:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
            self.encoders[col] = le
        
        self.features = (numeric_project_cols + numeric_user_cols + 
                        [f'{c}_encoded' for c in categorical_cols])
        
        X = df[self.features]
        y = df["Sucesso"]
        
        X_scaled = X.copy()
        numeric_features = numeric_project_cols + numeric_user_cols
        X_scaled[numeric_features] = self.scaler.fit_transform(X[numeric_features])
        
        return X_scaled, y
    
    
    #treinamento do modelo
    def train_model(self, X, y):

        print("Iniciando treinamento do modelo híbrido...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        
        rf_clf = RandomForestClassifier(random_state=42)
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 15, None],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        }
        
        grid_search = GridSearchCV(rf_clf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1)
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        self.is_trained = True
        
        y_pred = self.model.predict(X_test)
        probas = self.model.predict_proba(X_test)[:, 1]
        
        auc_score = roc_auc_score(y_test, probas)
        print(f"Treinamento concluído - AUC: {auc_score:.4f}")
        
        return {
            'auc': auc_score,
            'best_params': grid_search.best_params_
        }
    
    def predict_single_project(self, project_data, user_cargo=None):
        if not self.is_trained:
            return {'error': 'Modelo não treinado', 'success_probability': 0}
        
        try:
            processed_data = self._preprocess_input(project_data, user_cargo)
            
            # Criar DataFrame com nomes de features para evitar warnings
            import pandas as pd
            input_df = pd.DataFrame([processed_data], columns=self.features)
            
            prediction = self.model.predict(input_df)[0]
            probability = self.model.predict_proba(input_df)[0]
            
            success_percentage = round(probability[1] * 100, 2)
            
            result = {
                'prediction': 'Sucesso' if prediction == 1 else 'Fracasso',
                'success_probability': success_percentage,
                'confidence_level': self._get_confidence(probability[1]),
                'raw_probabilities': {
                    'fracasso': round(probability[0], 4),
                    'sucesso': round(probability[1], 4)
                }
            }
            
            return result
            
        except Exception as e:
            return {'error': f'Erro: {str(e)}', 'success_probability': 0}
    
    def _preprocess_input(self, project_data, user_cargo=None):
        # Criar um dicionário para armazenar os valores processados
        processed_dict = {}
        
        # Features numéricas do projeto
        project_features = ['Duracao_meses', 'Orcamento_R$', 'Tamanho_da_Equipe']
        project_values = []
        for feature in project_features:
            try:
                value = float(project_data.get(feature, 0))
                project_values.append(value)
            except (ValueError, TypeError):
                project_values.append(0.0)
        
        # Features do usuário
        cargo = user_cargo or project_data.get('cargoFuncionario', 'Desenvolvedor Senior')
        user_values = self._get_user_features(cargo)
        
        # Normalizar features numéricas
        all_numeric = project_values + user_values
        numeric_features = ['Duracao_meses', 'Orcamento_R$', 'Tamanho_da_Equipe', 
                           'Experiencia_Media_Cargo', 'Projetos_Medios_Cargo', 
                           'Taxa_Sucesso_Cargo', 'Sucesso_Medio_Cargo']
        
        # Aplicar normalização apenas nas features numéricas
        import pandas as pd
        temp_df = pd.DataFrame([all_numeric], columns=numeric_features)
        normalized_values = self.scaler.transform(temp_df)[0]
        
        # Adicionar features numéricas normalizadas
        for i, feature in enumerate(numeric_features):
            processed_dict[feature] = normalized_values[i]
        
        # Features categóricas
        categorical_features = ['RecursosDisponiveis', 'cargoFuncionario']
        for feature in categorical_features:
            if feature in self.encoders:
                try:
                    value = project_data.get(feature) if feature != 'cargoFuncionario' else cargo
                    encoded_value = self.encoders[feature].transform([str(value)])[0]
                    processed_dict[f'{feature}_encoded'] = encoded_value
                except (ValueError, KeyError):
                    processed_dict[f'{feature}_encoded'] = 0
            else:
                processed_dict[f'{feature}_encoded'] = 0
        
        # Retornar valores na ordem correta das features
        return [processed_dict[feature] for feature in self.features]
    
    def _get_user_features(self, cargo):
        if cargo in self.user_data:
            users_cargo = self.user_data[cargo]
            return [
                np.mean([u['experiencia'] for u in users_cargo]),
                np.mean([u['total_projetos'] for u in users_cargo]),
                np.mean([u['taxa_sucesso'] for u in users_cargo]),
                np.mean([u['sucesso_medio'] for u in users_cargo])
            ]
        else:
            # Valores padrão se cargo não encontrado
            return [5.0, 10.0, 0.7, 0.75]
    
    def _get_confidence(self, probability):
        if probability > 0.8:
            return 'Muito Alta'
        elif probability > 0.7:
            return 'Alta'
        elif probability > 0.6:
            return 'Média'
        elif probability > 0.5:
            return 'Baixa'
        else:
            return 'Muito Baixa'
    
    def get_feature_importance(self):
        if not self.is_trained:
            return None
        
        importance_dict = dict(zip(self.features, self.model.feature_importances_))
        
        # Separar por categoria
        project_importance = {k: v for k, v in importance_dict.items() 
                            if any(x in k for x in ['Duracao', 'Orcamento', 'Tamanho', 'Recursos'])}
        user_importance = {k: v for k, v in importance_dict.items() 
                         if any(x in k for x in ['Experiencia', 'Projetos', 'Taxa', 'Sucesso', 'cargo'])}
        
        return {
            'all_features': importance_dict,
            'project_features': project_importance,
            'user_features': user_importance
        }
    
    def save_model(self, filename='model_func_proj.joblib'):
        if not self.is_trained:
            print("Modelo não treinado")
            return False
        
        joblib.dump({
            'model': self.model,
            'encoders': self.encoders,
            'scaler': self.scaler,
            'features': self.features,
            'user_data': self.user_data,
            'training_date': datetime.now().isoformat(),
            'model_type': 'hybrid'
        }, filename)
        
        print(f"Modelo salvo: {filename}")
        return True
    
    def load_model(self, filename='model_func_proj.joblib'):
        try:
            data = joblib.load(filename)
            self.model = data['model']
            self.encoders = data['encoders']
            self.scaler = data['scaler']
            self.features = data['features']
            self.user_data = data['user_data']
            self.is_trained = True
            print(f"Modelo carregado: {filename}")
            return True
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False
    

    # método para treinar o modelo completo
    def run_full_pipeline(self, projects_path, users_path):
        if not self.load_data(projects_path, users_path):
            return False
        
        X, y = self.prepare_features()
        results = self.train_model(X, y)
        
        print("\nImportância das features:")
        importance = self.get_feature_importance()
        for category, features in importance.items():
            if category != 'all_features':
                print(f"\n{category.replace('_', ' ').title()}:")
                sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
                for feature, imp in sorted_features[:3]:
                    print(f"  {feature}: {imp:.4f}")
        
        return results