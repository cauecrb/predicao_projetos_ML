# Execução do chatbot e treinamento do modelo

## 1. PRÉ-REQUISITOS
   - Python 3.8 ou superior
   - Instalar dependências: pip install -r requirements.txt

## 2. ESTRUTURA DE DADOS NECESSÁRIA
   Os seguintes arquivos CSV devem estar em ML/datas/:
   - projetos_dataset.csv: dados dos projetos
   - usuarios_dataset.csv: dados dos usuários
   Para gerar os arquivos CSV, execute os scriptsdentro de factory_data (opcional)
    Com o ambiente virtual sendo executado (venv) e os requirements instalados, execute:
        - python generate_realistic_data.py


## 3. EXECUTAR TREINAMENTO
   com o ambiente virtual sendo executado (venv) execute:
   python train_model.py

## 4. SAÍDA ESPERADA
   - Modelo treinado salvo em: ML/ml_model/trained_model.joblib
   - Métricas de avaliação exibidas no terminal
   - Teste de predição de exemplo

## 5. ESTRUTURA DOS DADOS
   
   projetos_dataset.csv deve conter:
   - complexidade, duracao_estimada, orcamento, equipe_tamanho
   - tecnologia_principal, metodologia, setor_cliente
   - sucesso (0 ou 1)
   
   usuarios_dataset.csv deve conter:
   - nome, cargo, experiencia_anos, sucesso_medio
   - projetos_concluidos

## 6. EXECUÇÃO DO CHATBOT
   - execute o venv para ativar o ambiente virtual 
   - Execute o arquivo web_chatbot.py para iniciar o chatbot web em cha_bot/chatbot
   - acesse no naveafor em localhost:5001 e de as informçoes para o novo projeto


### Considerações sobre o projeto
Inicialmente, a intenção era utilizar as bases de dados sugeridas para o desenvolvimento do modelo. No entanto, como a base de funcionários não estava disponível, decidi criar scripts personalizados para gerar meus próprios dados, que podem ser encontrados no diretório factory_data.
Durante a primeira etapa do treinamento, utilizei apenas os dados de projetos existentes. Logo percebi que os resultados do modelo apresentavam um comportamento aleatório, sem variações relevantes de acordo com os funcionários utilizados. Para resolver isso, refinei o processo de treinamento incluindo uma base de dados de usuários, também gerada por meio de um factory. Isso trouxe certa melhora, mas o modelo ainda apresentava previsões excessivamente otimistas.
A seguir, fiz ajustes na base de dados, incorporando falhas realistas e variabilidade nos projetos, o que contribuiu para um comportamento mais coerente e preciso do modelo. Também ajustei o script de treinamento para refletir melhor os cenários esperados. Após essas modificações, observei uma melhoria significativa na performance do modelo. Por fim, adicionei uma variável referente à complexidade dos projetos, que considero uma informação essencial para prever com mais precisão o sucesso ou fracasso de cada iniciativa.

### Treinamento do modelo
Os scripts de treinamento estão localizados no diretório ml_model. Para o modelo, foi escolhida a abordagem Random Forest, sendo o resultado salvo no arquivo trained_model.joblib.

### API de Conexão
A API encontra-se no diretório api_conection e foi construída com Flask, uma escolha motivada pela familiaridade com o framework e sua simplicidade para implementação. Para executá-la, é necessário ativar o ambiente virtual (venv) e rodar o comando:
python3 app.py ao usar a versão web executando python3 web_chatbot.py, não é necessario rodar a api pois a execuçao do modelo ja esta integrada ao arquivo web_chatbot, para acessar pelo navegador acesse localhost:5001.

### Chatbot
O chatbot foi inicialmente concebido para execução via terminal, mas posteriormente foi adicionado um módulo com visualização em navegador, com o objetivo de tornar a interface mais amigável.

### Scripts auxiliares
Todos os arquivos necessários para executar a API e o chatbot acompanham o projeto. Entretanto, caso deseje gerar um novo conjunto de dados:
- A geração de usuários pode ser feita com o script user_data_generator.py.
- A geração de projetos realistas pode ser feita com generate_realistic_data.py.

### Observação final
Apesar de o processo de treinamento e os dados utilizados terem sido testados repetidamente, eles ainda necessitam de refinamento adicional e validação por especialistas na área. Esta ferramenta é apenas uma demonstração e suas análises devem sempre passar pela aprovação de um ser humano.