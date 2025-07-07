### Execução e treinamento do modelo de ML

# 1. PRÉ-REQUISITOS
   - Python 3.8 ou superior
   - Instalar dependências: pip install -r requirements.txt
   - Bibliotecas principais: pandas, scikit-learn, joblib

# 2. ESTRUTURA DE DADOS NECESSÁRIA
   Os seguintes arquivos CSV devem estar em ML/datas/:
   - projetos_dataset.csv: dados dos projetos
   - usuarios_dataset.csv: dados dos usuários
   Para gerar os arquivos CSV, execute os scriptsdentro de factory_data (opcional)
    Com o ambiente virtual sendo executado (venv) e os requirements instalados, execute:
        - python generate_realistic_data.py
        - python balance_dataset.py


# 3. EXECUTAR TREINAMENTO
   com o ambiente virtual sendo executado (venv) execute:
   python train_model.py

# 4. SAÍDA ESPERADA
   - Modelo treinado salvo em: ML/ml_model/trained_model.joblib
   - Métricas de avaliação exibidas no terminal
   - Teste de predição de exemplo

# 5. ESTRUTURA DOS DADOS
   
   projetos_dataset.csv deve conter:
   - complexidade, duracao_estimada, orcamento, equipe_tamanho
   - tecnologia_principal, metodologia, setor_cliente
   - sucesso (0 ou 1)
   
   usuarios_dataset.csv deve conter:
   - nome, cargo, experiencia_anos, sucesso_medio
   - projetos_concluidos

# 6. PARÂMETROS DO MODELO
   - Algoritmo: Random Forest Classifier
   - Otimização: Grid Search CV
   - Balanceamento: class_weight='balanced'
   - Validação: 5-fold cross validation

# 7. POSSIVEIS ERROS
   - Erro de caminho: verifique se está na pasta correta
   - Dados faltando: execute os geradores de dados primeiro
   - Erro de memória: reduza o tamanho do dataset


# 8. PRÓXIMOS PASSOS
    - Para API: execute chat_bot/api_conection/app.py
    - Para chatbot: execute chat_bot/chatbot/web_chatbot.py
