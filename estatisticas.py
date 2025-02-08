import banco
import sqlite3
import pandas as pd
from scipy.stats import pearsonr
import numpy as np 

def correlacao(gols_A, gols_B):
    if len(gols_A) > len(gols_B):
        gols_A = gols_A[0:len(gols_B)]
    if len(gols_B) > len(gols_A):
        gols_B = gols_B[0:len(gols_A)]
    # Calcula a correlação de Pearson
    correlacao, p_value = pearsonr(gols_A, gols_B)

    print(f"Correlação de Pearson: {correlacao}")
    print(f"Valor-p: {p_value}")

def agrupar_por_intervalo(df, intervalo):
    # Converte a coluna 'tempo' para inteiro
    df['tempo'] = df['tempo'].astype(int)

    # Cria os intervalos (bins)
    bins = range(0, df['tempo'].max() + intervalo, intervalo)
    labels = [f"{i}-{i+intervalo}" for i in bins[:-1]]  # Rótulos dos intervalos

    # Agrupa os gols por intervalo
    df['intervalo'] = pd.cut(df['tempo'], bins=bins, labels=labels, right=False)
    return df.groupby('intervalo', observed=False).size()

# Função para processar os campeonatos e calcular correlações
def calcular_correlacoes(intervalo):
    # Obtém os campeonatos
    df_campeonatos = banco.get_campeonatos()

    # Dicionário para armazenar os gols agrupados de cada campeonato
    gols_agrupados = {}

    # Conecta ao banco de dados
    conn = sqlite3.connect("banco_geral.db")

    # Itera sobre os campeonatos
    for index, row in df_campeonatos.iterrows():
        nome = row['nome']
        ano = row['ano']

        # Consulta os gols do campeonato
        query_gols = '''
        SELECT gols.tempo
        FROM gols
        JOIN jogos ON gols.id_jogo = jogos.id
        JOIN campeonatos ON jogos.id_campeonato = campeonatos.id
        WHERE campeonatos.nome = ? AND campeonatos.ano = ?
        '''
        gols_campeonato = pd.read_sql_query(query_gols, conn, params=(nome, ano))

        # Agrupa os gols por intervalo de tempo
        gols_agrupados[f"{nome} {ano}"] = agrupar_por_intervalo(gols_campeonato, intervalo)

    # Fecha a conexão com o banco de dados
    conn.close()

    # Cria um DataFrame com os gols agrupados
    df_gols = pd.DataFrame(gols_agrupados).fillna(0)  # Preenche valores faltantes com 0

    # Calcula a matriz de correlação
    matriz_correlacao = df_gols.corr()

    # Encontra a média das correlações
    mean_correlacao = np.mean(matriz_correlacao)

    return matriz_correlacao, mean_correlacao