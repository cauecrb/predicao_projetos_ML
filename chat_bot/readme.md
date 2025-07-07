# Guia de Execução do Chatbot

### 1. PRÉ-REQUISITOS
   - Python 3.8 ou superior
   - Modelo treinado (execute primeiro o treinamento)
   - Instalar dependências: pip install -r requirements.txt
   - Bibliotecas principais: flask, pandas, scikit-learn, joblib

### 2. VERIFICAR MODELO TREINADO
   Certifique-se que existe o arquivo:
   ML/ml_model/trained_model.joblib
   
   Se não existir, execute primeiro:
   cd ML/ml_model
   python train_model.py

### 3. EXECUTAR CHATBOT WEB
   cd chat_bot/chatbot
   python web_chatbot.py
   
   O servidor será iniciado em: http://localhost:5001
   Acesse pelo navegador para usar a interface web

### 4. EXECUTAR CHATBOT TERMINAL (ALTERNATIVO)
   cd chat_bot/chatbot
   python chatbot.py
   
   Interação direta pelo terminal/console



### 5. INTERFACE WEB
   
   Funcionalidades disponíveis:
   - Chat interativo
   - Formulário de predição
   - Visualização de resultados
   - Visualização de usuários cadastrados
   
   Template localizado em:
   chat_bot/chatbot/templates/chatbot.html

    
   Para modificar respostas do chatbot:
    - Edite chat_bot/chatbot/chatbot.py
    - Modifique os templates em templates/
    