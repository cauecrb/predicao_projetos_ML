import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid

class UserDataGenerator:
    
    def __init__(self):
        self.nomes_masculinos = [
            'João', 'Pedro', 'Lucas', 'Gabriel', 'Rafael', 'Daniel', 'Matheus', 'Felipe', 'Bruno', 'André',
            'Carlos', 'Fernando', 'Ricardo', 'Rodrigo', 'Marcelo', 'Paulo', 'Thiago', 'Diego', 'Gustavo', 'Leonardo'
        ]
        
        self.nomes_femininos = [
            'Maria', 'Ana', 'Juliana', 'Fernanda', 'Carla', 'Patrícia', 'Mariana', 'Camila', 'Beatriz', 'Larissa',
            'Gabriela', 'Amanda', 'Priscila', 'Renata', 'Vanessa', 'Cristina', 'Débora', 'Luciana', 'Mônica', 'Tatiana'
        ]
        
        self.sobrenomes = [
            'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Gomes',
            'Costa', 'Ribeiro', 'Martins', 'Carvalho', 'Almeida', 'Lopes', 'Soares', 'Fernandes', 'Vieira', 'Barbosa',
            'Rocha', 'Dias', 'Monteiro', 'Mendes', 'Freitas', 'Cardoso', 'Ramos', 'Nascimento', 'Correia', 'Teixeira'
        ]
        
        self.cargos = [
            'Gerente de Projeto', 'Analista de Sistemas', 'Desenvolvedor Senior', 'Desenvolvedor Pleno',
            'Desenvolvedor Junior', 'Arquiteto de Software', 'Tech Lead', 'Product Owner', 'Scrum Master',
            'Analista de Negócios', 'Designer UX/UI', 'Analista de Qualidade', 'DevOps Engineer',
            'Coordenador de TI', 'Consultor Técnico', 'Especialista em Dados', 'Analista de Requisitos'
        ]
        
        self.cargo_profiles = {
            'Gerente de Projeto': {'exp_min': 5, 'exp_max': 20, 'sucesso_base': 75, 'variacao': 15},
            'Arquiteto de Software': {'exp_min': 7, 'exp_max': 25, 'sucesso_base': 80, 'variacao': 12},
            'Tech Lead': {'exp_min': 6, 'exp_max': 18, 'sucesso_base': 78, 'variacao': 13},
            'Product Owner': {'exp_min': 4, 'exp_max': 15, 'sucesso_base': 72, 'variacao': 16},
            'Scrum Master': {'exp_min': 3, 'exp_max': 12, 'sucesso_base': 70, 'variacao': 14},
            'Desenvolvedor Senior': {'exp_min': 5, 'exp_max': 15, 'sucesso_base': 73, 'variacao': 15},
            'Desenvolvedor Pleno': {'exp_min': 3, 'exp_max': 8, 'sucesso_base': 65, 'variacao': 18},
            'Desenvolvedor Junior': {'exp_min': 0, 'exp_max': 3, 'sucesso_base': 55, 'variacao': 20},
            'Analista de Sistemas': {'exp_min': 2, 'exp_max': 12, 'sucesso_base': 68, 'variacao': 17},
            'Analista de Negócios': {'exp_min': 2, 'exp_max': 10, 'sucesso_base': 67, 'variacao': 16},
            'Designer UX/UI': {'exp_min': 1, 'exp_max': 8, 'sucesso_base': 63, 'variacao': 18},
            'Analista de Qualidade': {'exp_min': 2, 'exp_max': 10, 'sucesso_base': 69, 'variacao': 15},
            'DevOps Engineer': {'exp_min': 3, 'exp_max': 12, 'sucesso_base': 71, 'variacao': 14},
            'Coordenador de TI': {'exp_min': 4, 'exp_max': 16, 'sucesso_base': 74, 'variacao': 13},
            'Consultor Técnico': {'exp_min': 6, 'exp_max': 20, 'sucesso_base': 76, 'variacao': 12},
            'Especialista em Dados': {'exp_min': 3, 'exp_max': 12, 'sucesso_base': 70, 'variacao': 15},
            'Analista de Requisitos': {'exp_min': 2, 'exp_max': 8, 'sucesso_base': 66, 'variacao': 17}
        }
        #gera ID sequencial
        self.user_counter = 0
    
    def _get_user_id(self):
        self.user_counter += 1
        return self.user_counter
    
    def _get_name(self):
        genero = random.choice(['M', 'F'])
        if genero == 'M':
            primeiro_nome = random.choice(self.nomes_masculinos)
        else:
            primeiro_nome = random.choice(self.nomes_femininos)
        
        sobrenome = random.choice(self.sobrenomes)
        
        # Às vezes adiciona um segundo nome
        if random.random() < 0.3:
            if genero == 'M':
                segundo_nome = random.choice(self.nomes_masculinos)
            else:
                segundo_nome = random.choice(self.nomes_femininos)
            return f"{primeiro_nome} {segundo_nome} {sobrenome}"
        
        return f"{primeiro_nome} {sobrenome}"
    
    def _get_cargo(self):
        weights = {
            'Desenvolvedor Junior': 0.15,
            'Desenvolvedor Pleno': 0.20,
            'Desenvolvedor Senior': 0.15,
            'Analista de Sistemas': 0.12,
            'Gerente de Projeto': 0.08,
            'Tech Lead': 0.06,
            'Arquiteto de Software': 0.04,
            'Product Owner': 0.05,
            'Scrum Master': 0.04,
            'Analista de Negócios': 0.03,
            'Designer UX/UI': 0.03,
            'Analista de Qualidade': 0.02,
            'DevOps Engineer': 0.02,
            'Coordenador de TI': 0.01
        }
        
        cargos = list(weights.keys())
        pesos = list(weights.values())
        
        return np.random.choice(cargos, p=pesos)
    
    def _get_exp_and_success(self, cargo):
        profile = self.cargo_profiles.get(cargo, {
            'exp_min': 1, 'exp_max': 10, 'sucesso_base': 60, 'variacao': 20
        })
        
        # Gera experiência
        experiencia = np.random.randint(profile['exp_min'], profile['exp_max'] + 1)
        
        # Gera sucesso médio baseado na experiência e cargo
        sucesso_base = profile['sucesso_base']
        variacao = profile['variacao']
        
        exp_factor = min(experiencia / 10, 1.0)
        sucesso_ajustado = sucesso_base + (exp_factor * 10)
        
        sucesso_final = np.random.normal(sucesso_ajustado, variacao/3)
        sucesso_final = max(20, min(95, sucesso_final))
        
        return experiencia, round(sucesso_final, 1)
    
    def _get_project_history(self, experiencia, sucesso_medio):
        if experiencia <= 1:
            num_projetos = np.random.randint(1, 4)
        elif experiencia <= 3:
            num_projetos = np.random.randint(3, 8)
        elif experiencia <= 5:
            num_projetos = np.random.randint(5, 15)
        elif experiencia <= 10:
            num_projetos = np.random.randint(10, 25)
        else:
            num_projetos = np.random.randint(15, 40)
        
        projetos_sucesso = int(num_projetos * (sucesso_medio / 100))
        projetos_falha = num_projetos - projetos_sucesso
        
        return f"{projetos_sucesso}/{num_projetos} (Sucessos/Total)"
    
    def generate_user_data(self, num_users=100):
        users_data = []
        self.user_counter = 0
        
        for _ in range(num_users):
            user_id = self._generate_user_id()
            nome = self._generate_name()
            cargo = self._generate_cargo()
            experiencia, sucesso_medio = self._generate_experience_and_success(cargo)
            historico_projetos = self._generate_project_history(experiencia, sucesso_medio)
            
            user_data = {
                'Usuario_ID': user_id,
                'Nome': nome,
                'Cargo': cargo,
                'Historico_de_Projetos': historico_projetos,
                'Experiencia(anos)': experiencia,
                'Sucesso_Medio(percentual)': sucesso_medio
            }
            
            users_data.append(user_data)
        
        return pd.DataFrame(users_data)
    
    def save_to_csv(self, df, filename='usuarios_dataset.csv'):
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Dataset salvo: {filename}")
        return filename
    
    def show_stats(self, df):
        print(f"\nTotal: {len(df)} usuários")
        print("\nCargos:")
        cargo_dist = df['Cargo'].value_counts()
        for cargo, count in cargo_dist.items():
            print(f"  {cargo}: {count} ({count/len(df)*100:.1f}%)")
        
        print(f"\nEstatísticas de experiência:")
        print(f"  Média: {df['Experiencia(anos)'].mean():.1f} anos")
        print(f"  Min/Max: {df['Experiencia(anos)'].min()}/{df['Experiencia(anos)'].max()} anos")
        
        print(f"\nEstatísticas de sucesso médio:")
        print(f"  Média: {df['Sucesso_Medio(percentual)'].mean():.1f}%")
        print(f"  Min/Max: {df['Sucesso_Medio(percentual)'].min():.1f}%/{df['Sucesso_Medio(percentual)'].max():.1f}%")
        
        print(f"\nTop 5 usuários com maior sucesso médio:")
        top_users = df.nlargest(5, 'Sucesso_Medio(percentual)')
        for _, user in top_users.iterrows():
            print(f"  {user['Nome']} ({user['Cargo']}) - {user['Sucesso_Medio(percentual)']}%")

if __name__ == "__main__":
    generator = UserDataGenerator()
    
    print("Gerando usuários...")
    users_df = generator.generate_user_data(num_users=50)
    
    filename = generator.save_to_csv(users_df, 'usuarios_dataset.csv')
    
    generator.show_stats(users_df)
    
    print("\nExemplos:")
    print(users_df.head(10).to_string(index=False))