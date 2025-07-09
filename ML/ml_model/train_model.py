from model_forest import HybridProjectSuccessModel
from sklearn.utils.class_weight import compute_class_weight
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np
import os

# Detectar o diretório base do projeto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))

# Caminhos absolutos para os arquivos de dados
project_data_path = os.path.join(project_root, 'ML', 'datas', 'projetos_dataset.csv')
user_data_path = os.path.join(project_root, 'ML', 'datas', 'usuarios_dataset.csv')

# Verificar se os arquivos existem
if not os.path.exists(project_data_path):
    print(f"Arquivo não encontrado: {project_data_path}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Diretório do script: {script_dir}")
    print(f"Raiz do projeto: {project_root}")
    
    # Listar arquivos disponíveis
    datas_dir = os.path.join(project_root, 'ML', 'datas')
    print(f"Arquivos disponíveis em {datas_dir}:")
    if os.path.exists(datas_dir):
        for file in os.listdir(datas_dir):
            print(f"  - {file}")
    else:
        print(f"  Diretório {datas_dir} não existe")
    exit(1)

if not os.path.exists(user_data_path):
    print(f"Arquivo não encontrado: {user_data_path}")
    exit(1)

print(f"Arquivos encontrados:")
print(f"  - Projetos: {project_data_path}")
print(f"  - Usuários: {user_data_path}")

# Criar e treinar modelo
print("Iniciando treinamento do modelo...")
model = HybridProjectSuccessModel()

if not model.load_data(project_data_path, user_data_path):
    print("Erro ao carregar dados. Verifique os caminhos dos arquivos.")
    exit(1)

print("Dados carregados com sucesso")

X, y = model.prepare_features()
print(f"Features preparadas: {len(model.features)} features, {len(X)} registros")

class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
weight_dict = {0: class_weights[0], 1: class_weights[1]}

print(f"Pesos das classes: {weight_dict}")
print(f"Sucessos: {np.mean(y)*100:.1f}%")

print("Iniciando treinamento com Grid Search...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

rf_clf = RandomForestClassifier(random_state=42, class_weight='balanced')
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 15, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

grid_search = GridSearchCV(rf_clf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
grid_search.fit(X_train, y_train)

model.model = grid_search.best_estimator_
model.is_trained = True

y_pred = model.model.predict(X_test)
probas = model.model.predict_proba(X_test)[:, 1]

auc_score = roc_auc_score(y_test, probas)

print(f"\nAUC score: {auc_score:.4f}")
print(f"Melhores parametros: {grid_search.best_params_}")

# Salvar modelo no mesmo diretório do script
model_path = os.path.join(script_dir, 'trained_model.joblib')
print(f"Salvando modelo em: {model_path}")
model.save_model(model_path)
print(f"Modelo salvo: {model_path}")

print()

# Teste de predição
test_project = {
    'Duracao_meses': 6.0,
    'Orcamento_R$': 150000.0,
    'Tamanho_da_Equipe': 2,
    'RecursosDisponiveis': 'baixo'
}

result = model.predict_single_project(test_project, 'Tech Lead')
print(f"\nTeste de predição (projeto de baixo orçamento):")
print(f"Probabilidade de sucesso: {result['success_probability']}%")
print(f"Predição: {result['prediction']}")