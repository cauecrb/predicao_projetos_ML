import sys
import os
import pandas as pd
import joblib
from datetime import datetime

sys.path.append('../../ML/ml_model')
from model_forest import HybridProjectSuccessModel

class ProjectBot:
    def __init__(self):
        self.model = HybridProjectSuccessModel()
        self.users = None
        self.project = {}
        self.user = None
        self.history = []
        
        self.questions = [
            {'field': 'Duracao_meses', 'text': 'Duração (meses)?', 'type': 'int', 'min': 1, 'max': 60},
            {'field': 'Orcamento_R$', 'text': 'Orçamento (R$)?', 'type': 'float', 'min': 1000, 'max': 10000000},
            {'field': 'Tamanho_da_Equipe', 'text': 'Tamanho da equipe?', 'type': 'int', 'min': 1, 'max': 50},
            {'field': 'RecursosDisponiveis', 'text': 'Recursos (baixo/médio/alto)?', 'type': 'choice', 'options': ['baixo', 'médio', 'alto']}
        ]
        
        self.init()
    
    def init(self):
        try:
            loaded = self.model.load_model('../../ML/ml_model/trained_model.joblib')
            if not loaded:
                success = self.model.run_full_pipeline(
                    '../../ML/datas/projetos_fake_dataset.csv',
                    '../../ML/datas/usuarios_dataset.csv'
                )
                if not success:
                    return False
            
            self.users = pd.read_csv('../../ML/datas/usuarios_dataset.csv')
            return True
        except:
            return False
    
    def start(self):
        print("\n=== ANÁLISE DE PROJETOS ===")
        print("Vamos analisar seu projeto\n")
        
        self.collect_data()
    
    def collect_data(self):
        for q in self.questions:
            if not self.ask(q):
                print("Cancelado")
                return
        
        self.pick_user()
    
    def ask(self, q):
        while True:
            answer = input(f"{q['text']} ").strip()
            
            if answer.lower() in ['sair', 'quit']:
                return False
            
            valid, value = self.validate(answer, q)
            if valid:
                self.project[q['field']] = value
                return True
            else:
                print("Inválido, tente novamente")
    
    def validate(self, answer, q):
        try:
            if q['type'] == 'int':
                val = int(answer)
                return q['min'] <= val <= q['max'], val
            elif q['type'] == 'float':
                val = float(answer.replace('R$', '').replace(' ', ''))
                return q['min'] <= val <= q['max'], val
            elif q['type'] == 'choice':
                val = answer.lower()
                return val in q['options'], val
        except:
            pass
        return False, None
    
    def pick_user(self):
        cargos = self.users['Cargo'].unique()
        print("\nCargos:")
        for i, cargo in enumerate(cargos, 1):
            print(f"{i}. {cargo}")
        
        while True:
            choice = input("Seu cargo? ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(cargos):
                    cargo = cargos[idx]
                    break
            
            matches = [c for c in cargos if choice.lower() in c.lower()]
            if len(matches) == 1:
                cargo = matches[0]
                break
            
            print("Inválido")
        
        users_cargo = self.users[self.users['Cargo'] == cargo]
        
        if len(users_cargo) == 1:
            self.user = users_cargo.iloc[0]
        else:
            print(f"\nUsuários {cargo}:")
            for i, (_, user) in enumerate(users_cargo.iterrows(), 1):
                print(f"{i}. {user['Nome']} ({user['Experiencia(anos)']} anos)")
            
            while True:
                try:
                    choice = int(input("Escolha: ")) - 1
                    if 0 <= choice < len(users_cargo):
                        self.user = users_cargo.iloc[choice]
                        break
                except:
                    pass
                print("Inválido")
        
        self.analyze()
    
    def analyze(self):
        result = self.model.predict_single_project(self.project, self.user['Cargo'])
        
        if 'error' in result:
            print(f"Erro: {result['error']}")
            return
        
        prob = result['success_probability']
        pred = result['prediction']
        
        print(f"\n=== RESULTADO ===")
        print(f"Usuário: {self.user['Nome']} ({self.user['Cargo']})")
        print(f"Probabilidade: {prob}%")
        print(f"Predição: {pred}")
        
        if prob < 60:
            print("\nSugestões:")
            self.suggest()
        
        self.save_result(result)
    
    def suggest(self):
        if self.project['Duracao_meses'] > 12:
            print("- Reduzir duração (muito longo)")
        if self.project['Orcamento_R$'] < 50000:
            print("- Aumentar orçamento")
        if self.project['Tamanho_da_Equipe'] < 3:
            print("- Aumentar equipe")
        if self.project['RecursosDisponiveis'] == 'baixo':
            print("- Melhorar recursos")
    
    def save_result(self, result):
        self.history.append({
            'time': datetime.now(),
            'project': self.project.copy(),
            'user': self.user['Nome'],
            'result': result
        })
    
    def run(self):
        while True:
            print("\n1. Analisar projeto")
            print("2. Ver histórico")
            print("3. Sair")
            
            choice = input("Opção: ")
            
            if choice == '1':
                self.start()
            elif choice == '2':
                self.show_history()
            elif choice == '3':
                break
    
    def show_history(self):
        if not self.history:
            print("Sem histórico")
            return
        
        for i, h in enumerate(self.history, 1):
            print(f"{i}. {h['user']} - {h['result']['success_probability']}%")

if __name__ == "__main__":
    bot = ProjectBot()
    bot.run()