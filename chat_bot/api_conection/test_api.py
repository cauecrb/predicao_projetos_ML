import requests

def test():
    url = 'http://localhost:5000'
    
    # Test health
    try:
        r = requests.get(f'{url}/')
        print(f"Health: {r.json()}")
    except:
        print("API not running")
        return
    
    # Test prediction
    data = {
        'duracao': 8,
        'orcamento': 300000,
        'equipe': 6,
        'recursos': 'alto',
        'cargo': 'Tech Lead'
    }
    
    try:
        r = requests.post(f'{url}/predict', json=data)
        print(f"Prediction: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()