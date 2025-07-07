import requests
import json

def test_api():
    base_url = 'http://localhost:5000'
    
    print("Testando API de Predição de Projetos")
    
    # Teste 1: Health check
    try:
        response = requests.get(f'{base_url}/health')
        print(f"Health check: {response.json()}")
    except:
        print("Erro: API não está rodando")
        return
    
    # Teste 2: Predição completa
    project_data = {
        'duracao': 8,
        'orcamento': 300000,
        'equipe': 6,
        'recursos': 'alto',
        'cargo': 'Tech Lead'
    }
    
    try:
        response = requests.post(f'{base_url}/predict', json=project_data)
        print(f"Predição completa: {response.json()}")
    except Exception as e:
        print(f"Erro na predição: {e}")
    
    # Teste 3: Predição simples
    simple_data = {
        'duracao': 12,
        'orcamento': 500000,
        'equipe': 8,
        'recursos': 'medio',
        'cargo': 'Gerente de Projeto'
    }
    
    try:
        response = requests.post(f'{base_url}/predict-simple', json=simple_data)
        print(f"Predição simples: {response.json()}")
    except Exception as e:
        print(f"Erro na predição simples: {e}")

if __name__ == '__main__':
    test_api()