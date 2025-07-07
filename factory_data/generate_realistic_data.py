import pandas as pd
import numpy as np
import random

def calculate_failure_probability(duracao, orcamento, equipe, recursos):
    risk = 0
    
    # Duração muito longa ou muito curta aumenta risco
    if duracao > 12 or duracao < 1:
        risk += 0.3
    elif duracao > 8:
        risk += 0.1
    
    # Orçamento baixo aumenta risco
    if orcamento < 100000:
        risk += 0.4
    elif orcamento < 200000:
        risk += 0.2
    
    # Equipe pequena aumenta risco
    if equipe < 3:
        risk += 0.3
    elif equipe < 5:
        risk += 0.1
    
    # Recursos baixos aumentam risco
    if recursos == 'baixo':
        risk += 0.4
    elif recursos == 'médio':
        risk += 0.1
    
    # Adicionar variabilidade aleatória
    risk_score += random.uniform(-0.1, 0.1)
    
    return min(max(risk_score, 0), 0.9)

def generate_realistic_projects(n_projects=1000):
    projects = []
    cargos = ['Arquiteto de Software', 'Gerente de Projetos', 'Tech Lead', 
              'Scrum Master', 'Product Owner', 'Desenvolvedor Senior']
    
    # Gerar características do projeto
    for i in range(n_projects):
        duracao = round(random.uniform(1, 18), 1)
        orcamento = round(random.uniform(50000, 2000000), 2)
        equipe = random.randint(2, 8)
        recursos = random.choice(['baixo', 'médio', 'alto'])
        cargo = random.choice(cargos)
        
        # Calcular probabilidade de falha
        failure_prob = calculate_failure_probability(duracao, orcamento, equipe, recursos)        
        sucesso = 1 if random.random() > failure_prob else 0
        
        projects.append({
            'projeto_id': f'PROJ_{i+1:04d}',
            'nome': f'Projeto {i+1}',
            'duracao_meses': duracao,
            'orcamento': orcamento,
            'tamanho_equipe': equipe,
            'recursos_disponiveis': recursos,
            'cargo_responsavel': cargo,
            'sucesso': sucesso
        })
    
    return pd.DataFrame(projects)

if __name__ == '__main__':
    df = generate_realistic_projects(1000)
    
    sucessos = len(df[df['sucesso'] == 1])
    total = len(df)
    print(f"Sucessos: {sucessos} ({sucessos/total*100:.1f}%)")
    print(f"Falhas: {total-sucessos} ({(total-sucessos)/total*100:.1f}%)")
    
    df.to_csv('../datas/projetos_dataset.csv', index=False)
    print("Dataset salvo!")