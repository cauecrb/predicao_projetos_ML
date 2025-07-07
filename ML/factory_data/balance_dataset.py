import pandas as pd
import numpy as np
from sklearn.utils import resample

# Carregar dados
df = pd.read_csv('../datas/projetos_dataset.csv')

# Separar por classe
sucess_projects = df[df['sucesso'] == 1]
failed_projects = df[df['sucesso'] == 0]

print(f"Projetos de sucesso: {len(sucess_projects)}")
print(f"Projetos com falha: {len(failed_projects)}")
print(f"Proporção atual: {len(sucess_projects)/len(df)*100:.1f}% sucesso")

# Balancear usando undersampling do grupo majoritário
sucess_downsampled = resample(sucess_projects, 
                             replace=False,
                             n_samples=len(failed_projects),
                             random_state=42)

# Combinar datasets balanceados
balanced_df = pd.concat([sucess_downsampled, failed_projects])
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Salvar dataset balanceado
balanced_df.to_csv('../datas/projetos_dataset_balanced.csv', index=False)
print(f"\nDataset balanceado salvo com {len(balanced_df)} projetos")
print(f"Nova proporção: 50% sucesso, 50% falha")