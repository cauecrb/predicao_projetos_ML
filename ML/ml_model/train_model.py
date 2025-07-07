from model_forest import HybridProjectSuccessModel
from sklearn.utils.class_weight import compute_class_weight
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np

project_data_path = '../datas/projetos_dataset.csv'
user_data_path = '../datas/usuarios_dataset.csv'

# CRiar e treinar modelo
model = HybridProjectSuccessModel()

if not model.load_data(project_data_path, user_data_path):
    print("Erro ao carregar dados. Verifique os caminhos dos arquivos.")
    exit(1)

X, y = model.prepare_features()

class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
weight_dict = {0: class_weights[0], 1: class_weights[1]}

print(f"Pesos das classes: {weight_dict}")
print(f"Sucessos: {np.mean(y)*100:.1f}%")

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

grid_search = GridSearchCV(rf_clf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1)
grid_search.fit(X_train, y_train)

model.model = grid_search.best_estimator_
model.is_trained = True

y_pred = model.model.predict(X_test)
probas = model.model.predict_proba(X_test)[:, 1]

auc_score = roc_auc_score(y_test, probas)

print(f"\nAUC score: {auc_score:.4f}")
print(f"Melhores parametros: {grid_search.best_params_}")

# Salvar modelo
model.save_model('trained_model.joblib')
print("\nModelo salvo")

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