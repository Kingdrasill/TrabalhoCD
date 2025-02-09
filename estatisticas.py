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

# Função para calcular os placares mais comuns e estatísticas de vitória
def ranking_placares_por_campeonato(caminho):
    conn = sqlite3.connect(caminho)
    # Consulta para buscar os dados dos jogos com campeonatos
    query = '''
    SELECT c.nome AS campeonato, c.ano, c.tipo,
           j.faltas_mandante, j.posse_mandante, 
           j.finalizacoes_mandante, j.escanteios_mandante, 
           j.faltas_visitante, j.posse_visitante, 
           j.finalizacoes_visitante, j.escanteios_visitante,
           j.id_mandante, j.id_visitante,
           (SELECT COUNT(gols.id) FROM gols WHERE gols.id_jogo = j.id AND gols.id_time = j.id_mandante) AS gols_mandante,
           (SELECT COUNT(gols.id) FROM gols WHERE gols.id_jogo = j.id AND gols.id_time = j.id_visitante) AS gols_visitante
    FROM jogos j
    JOIN campeonatos c ON j.id_campeonato = c.id
    '''

    df_jogos = pd.read_sql_query(query, conn)

    # Agrupar por campeonato e calcular placares mais comuns
    campeonatos = df_jogos.groupby(['campeonato', 'ano', 'tipo'])
    resultados = {}
    geral_placares = []

    estatisticas_por_tipo = {1: {'Vitória Mandante': 0, 'Vitória Visitante': 0, 'Empate': 0, 'Total': 0},
                              2: {'Vitória Mandante': 0, 'Vitória Visitante': 0, 'Empate': 0, 'Total': 0}}

    for (nome_campeonato, ano, tipo), dados in campeonatos:
        # Criar uma coluna com o placar formatado
        dados['placar'] = dados.apply(lambda x: f"{x['gols_mandante']} x {x['gols_visitante']}", axis=1)
        placar_freq = dados['placar'].value_counts(normalize=True) * 100

        # Selecionar os 3 placares mais comuns
        top_3_placares = placar_freq.head(3)
        geral_placares.extend(dados['placar'].tolist())

        # Calcular estatísticas de vitória/empate
        total_jogos = len(dados)
        vitoria_mandante = dados[dados['gols_mandante'] > dados['gols_visitante']].shape[0] / total_jogos * 100
        vitoria_visitante = dados[dados['gols_mandante'] < dados['gols_visitante']].shape[0] / total_jogos * 100
        empates = dados[dados['gols_mandante'] == dados['gols_visitante']].shape[0] / total_jogos * 100

        # Acumular estatísticas por tipo
        estatisticas_por_tipo[tipo]['Vitória Mandante'] += vitoria_mandante * total_jogos
        estatisticas_por_tipo[tipo]['Vitória Visitante'] += vitoria_visitante * total_jogos
        estatisticas_por_tipo[tipo]['Empate'] += empates * total_jogos
        estatisticas_por_tipo[tipo]['Total'] += total_jogos

        resultados[f"{nome_campeonato} ({ano}) - Tipo {tipo}"] = {
            "placares": top_3_placares,
            "estatisticas": {
                "Vitória Mandante": vitoria_mandante,
                "Vitória Visitante": vitoria_visitante,
                "Empate": empates
            }
        }

    # Exibir resultados formatados por campeonato
    for campeonato, dados in resultados.items():
        print(f"\n{campeonato}:")
        for placar, percentual in dados["placares"].items():
            print(f"{placar} - {percentual:.2f}%")
        print("Estatísticas de resultados:")
        for estatistica, valor in dados["estatisticas"].items():
            print(f"{estatistica}: {valor:.2f}%")

    # Estatísticas gerais por tipo de campeonato
    print("\nMédias por Tipo de Campeonato:")
    for tipo, estatisticas in estatisticas_por_tipo.items():
        if estatisticas['Total'] > 0:
            print(f"\nTipo {tipo}:")
            print(f"Vitória Mandante: {estatisticas['Vitória Mandante'] / estatisticas['Total']:.2f}%")
            print(f"Vitória Visitante: {estatisticas['Vitória Visitante'] / estatisticas['Total']:.2f}%")
            print(f"Empate: {estatisticas['Empate'] / estatisticas['Total']:.2f}%")

    # Estatísticas gerais
    geral_df = pd.DataFrame(geral_placares, columns=['placar'])
    geral_freq = geral_df['placar'].value_counts(normalize=True) * 100

    print("\nGeral:")
    for placar, percentual in geral_freq.head(3).items():
        print(f"{placar} - {percentual:.2f}%")

def processar_campeonatos():
    df_campeonatos = banco.get_campeonatos()
    conn = sqlite3.connect("banco_geral.db")

    for index, row in df_campeonatos.iterrows():
        nome = row['nome']
        ano = row['ano']

        query_gols = '''
        SELECT gols.tempo
        FROM gols
        JOIN jogos ON gols.id_jogo = jogos.id
        JOIN campeonatos ON jogos.id_campeonato = campeonatos.id
        WHERE campeonatos.nome = ? AND campeonatos.ano = ?
        '''
        gols_campeonato = pd.read_sql_query(query_gols, conn, params=(nome, ano))

        print(f"Gols do campeonato {nome} ({ano}):")
        print(gols_campeonato)

    conn.close() 