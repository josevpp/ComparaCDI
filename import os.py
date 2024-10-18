import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json

# Função para carregar as posições diárias de todos os arquivos JSON em uma pasta
def carregar_posicoes_diarias(pasta_json):
    posicoes = []
    for file_name in os.listdir(pasta_json):
        if file_name.endswith('.json'):
            file_path = os.path.join(pasta_json, file_name)
            with open(file_path, 'r') as f:
                data = json.load(f)
                total_amount = float(data['TotalAmmount'])
                posicoes.append({
                    'date': datetime.strptime(data['PositionDate'], '%Y-%m-%dT%H:%M:%S'),
                    'total_amount': total_amount
                })
    return pd.DataFrame(posicoes)

# Função para calcular a evolução da carteira e CDI
def calcular_evolucao_carteira(posicoes_df, aportes_retiradas_df, taxa_cdi_fixa):
    dates = posicoes_df['date']
    valor_carteira = posicoes_df['total_amount'].values
    
    cdi_evolucao = [valor_carteira[0]]  # Começando com o primeiro valor da carteira
    cdi_plus_evolucao = [valor_carteira[0]]  # Começando com o primeiro valor da carteira
    
    for i in range(len(dates) - 1):
        # Ajustando aportes/retiradas
        aporte_retirada = aportes_retiradas_df.loc[aportes_retiradas_df['Data'] == dates[i], 'Aporte/Retirada'].sum()
        
        # Atualiza o valor da carteira
        valor_carteira[i] += aporte_retirada
        
        # Calculando a evolução da carteira com CDI fixo
        cdi_evolucao.append(cdi_evolucao[-1] * (1 + taxa_cdi_fixa))
        cdi_plus_evolucao.append(cdi_plus_evolucao[-1] * (1 + (taxa_cdi_fixa + 0.015 / 252)))
    
    # Garantir que todos os arrays tenham o mesmo comprimento
    while len(cdi_evolucao) < len(dates):
        cdi_evolucao.append(cdi_evolucao[-1])
        
    while len(cdi_plus_evolucao) < len(dates):
        cdi_plus_evolucao.append(cdi_plus_evolucao[-1])
    
    return dates, valor_carteira, cdi_evolucao, cdi_plus_evolucao

# Caminho da pasta contendo os arquivos JSON
pasta_json = 'D:\\josev\\dataset 2\\data'

# Carregar os arquivos JSON da pasta
posicoes_df = carregar_posicoes_diarias(pasta_json)

# Carregar os aportes e retiradas
aportes_retiradas_df = pd.read_excel('D:\\josev\\dataset 2\\Aporte_Retirada 2.xlsm', sheet_name='Planilha1')
aportes_retiradas_df['Data'] = pd.to_datetime(aportes_retiradas_df['Data'])

# Defina a taxa CDI fixa (última taxa conhecida, por exemplo, 0.00053)
taxa_cdi_fixa = 0.00053  # Ajuste conforme necessário

# Gerar a evolução da carteira e CDI real
dates, valor_carteira, cdi_evolucao, cdi_plus_evolucao = calcular_evolucao_carteira(posicoes_df, aportes_retiradas_df, taxa_cdi_fixa)

# Plotar os resultados
plt.figure(figsize=(10, 6))
plt.plot(dates, valor_carteira, label='Evolução Carteira', marker='o')
plt.plot(dates, cdi_evolucao, label='CDI Fixo', linestyle='--')
plt.plot(dates, cdi_plus_evolucao, label='CDI Fixo + 1.5%', linestyle='--')
plt.title('Evolução da Carteira vs CDI Fixo')
plt.xlabel('Data')
plt.ylabel('Valor (R$)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
