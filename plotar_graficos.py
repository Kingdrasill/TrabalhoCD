import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

# Função para agrupar os gols por intervalo de minutos
def agrupar_por_intervalo(df, intervalo):
    # Cria os intervalos (bins)
    bins = range(df['tempo'].min(), df['tempo'].max() + intervalo, intervalo)
    labels = [f"{i}-{i+intervalo}" for i in bins[:-1]]  # Rótulos dos intervalos
    # Agrupa os gols por intervalo
    df['intervalo'] = pd.cut(df['tempo'], bins=bins, labels=labels, right=False)
    return df.groupby('intervalo', observed=False).size()

def plotar_gols_minuto(caminho_banco, intervalo_minutos=1):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco) 

    # Consulta para pegar os gols do primeiro tempo
    gols_primeiro_tempo_query = '''
    SELECT tempo
    FROM gols
    WHERE (CAST(tempo AS INTEGER) <= 45) OR (CAST(tempo AS INTEGER) > 45 AND CAST(tempo AS INTEGER) < 70 AND acrescimos = 1)
    '''
    gols_primeiro_tempo = pd.read_sql_query(gols_primeiro_tempo_query, conn)

    # Consulta para pegar os gols do segundo tempo
    gols_segundo_tempo_query = '''
    SELECT tempo
    FROM gols
    WHERE (CAST(tempo AS INTEGER) > 45 AND CAST(tempo AS INTEGER) <= 90) OR (CAST(tempo AS INTEGER) > 90 AND acrescimos = 1)
    '''
    gols_segundo_tempo = pd.read_sql_query(gols_segundo_tempo_query, conn)

    intervalos_primeiro_tempo = np.arange(0, gols_primeiro_tempo['tempo'].astype(int).max() + intervalo_minutos, intervalo_minutos)
    intervalos_segundo_tempo = np.arange(45, gols_segundo_tempo['tempo'].astype(int).max() + intervalo_minutos, intervalo_minutos)

    # Plotando os gráficos
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()

    # Separação das cores para gols fora do tempo normal
    primeiro_tempo_normal = gols_primeiro_tempo[gols_primeiro_tempo['tempo'].astype(int) <= 45]
    primeiro_tempo_acrescimos = gols_primeiro_tempo[gols_primeiro_tempo['tempo'].astype(int) > 45]

    segundo_tempo_normal = gols_segundo_tempo[gols_segundo_tempo['tempo'].astype(int) <= 90]
    segundo_tempo_acrescimos = gols_segundo_tempo[gols_segundo_tempo['tempo'].astype(int) > 90]

    # Histograma dos gols do primeiro tempo
    ax1.hist(primeiro_tempo_normal['tempo'].astype(int), bins=intervalos_primeiro_tempo, edgecolor='black', color='skyblue', label='Tempo Normal')
    ax1.hist(primeiro_tempo_acrescimos['tempo'].astype(int), bins=intervalos_primeiro_tempo, edgecolor='black', color='orange', label='Acréscimos')
    ax1.set_title('Histograma de Gols do Primeiro Tempo')
    ax1.set_xlabel('Intervalo de Minutos do Gol')
    ax1.set_ylabel('Quantidade de Gols')
    ax1.set_xticks(intervalos_primeiro_tempo)
    ax1.legend()

    # Histograma dos gols do segundo tempo
    ax2.hist(segundo_tempo_normal['tempo'].astype(int), bins=intervalos_segundo_tempo, edgecolor='black', color='salmon', label='Tempo Normal')
    ax2.hist(segundo_tempo_acrescimos['tempo'].astype(int), bins=intervalos_segundo_tempo, edgecolor='black', color='purple', label='Acréscimos')
    ax2.set_title('Histograma de Gols do Segundo Tempo')
    ax2.set_xlabel('Intervalo de Minutos do Gol')
    ax2.set_ylabel('Quantidade de Gols')
    ax2.set_xticks(intervalos_segundo_tempo)
    ax2.legend()

    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plot_gols_campeonatos(caminho_banco, competicoes, intervalo_minutos=1):
    conn = sqlite3.connect(caminho_banco) 

    cores = plt.cm.get_cmap('tab20', len(competicoes))  # Gera um mapa de cores dinâmico

    # Cria duas figuras separadas para os dois tempos
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()

    for i, (nome, ano) in enumerate(competicoes):
        cor = cores(i)

        # Consulta para pegar os gols do primeiro tempo
        gols_primeiro_tempo_query = '''
        SELECT gols.tempo
        FROM gols
        JOIN jogos ON gols.id_jogo = jogos.id
        JOIN campeonatos ON jogos.id_campeonato = campeonatos.id
        WHERE (campeonatos.nome = ? AND campeonatos.ano = ?)
          AND (
            (CAST(gols.tempo AS INTEGER) <= 45) 
            OR (CAST(gols.tempo AS INTEGER) > 45 AND CAST(gols.tempo AS INTEGER) < 70 AND gols.acrescimos = 1)
          )
        '''
        gols_primeiro_tempo = pd.read_sql_query(gols_primeiro_tempo_query, conn, params=(nome, ano))

        # Consulta para pegar os gols do segundo tempo
        gols_segundo_tempo_query = '''
        SELECT gols.tempo
        FROM gols
        JOIN jogos ON gols.id_jogo = jogos.id
        JOIN campeonatos ON jogos.id_campeonato = campeonatos.id
        WHERE (campeonatos.nome = ? AND campeonatos.ano = ?)
          AND (
            (CAST(gols.tempo AS INTEGER) > 45 AND CAST(gols.tempo AS INTEGER) <= 90) 
            OR (CAST(gols.tempo AS INTEGER) > 90 AND gols.acrescimos = 1)
          )
        '''
        gols_segundo_tempo = pd.read_sql_query(gols_segundo_tempo_query, conn, params=(nome, ano))

        # Converte a coluna 'tempo' para inteiro
        gols_primeiro_tempo['tempo'] = gols_primeiro_tempo['tempo'].astype(int)
        gols_segundo_tempo['tempo'] = gols_segundo_tempo['tempo'].astype(int)

        # Agrupa os gols por intervalo de minutos
        gols_por_intervalo_primeiro = agrupar_por_intervalo(gols_primeiro_tempo, intervalo_minutos)
        gols_por_intervalo_segundo = agrupar_por_intervalo(gols_segundo_tempo, intervalo_minutos)

        # Plot para o primeiro tempo
        ax1.plot(gols_por_intervalo_primeiro.index, gols_por_intervalo_primeiro, label=f'{nome} {ano}', color=cor)

        # Plot para o segundo tempo
        ax2.plot(gols_por_intervalo_segundo.index, gols_por_intervalo_segundo, label=f'{nome} {ano}', color=cor)

    # Configurações do gráfico do primeiro tempo
    ax1.set_title('Gols por Minuto - Primeiro Tempo')
    ax1.set_xlabel('Minutos')
    ax1.set_ylabel('Quantidade de Gols')
    ax1.legend()

    # Configurações do gráfico do segundo tempo
    ax2.set_title('Gols por Minuto - Segundo Tempo')
    ax2.set_xlabel('Minutos')
    ax2.set_ylabel('Quantidade de Gols')
    ax2.legend()

    # Exibe os gráficos em janelas separadas
    plt.show()

    conn.close()

def plotar_gols_minuto_jogo_inteiro(caminho_banco, intervalo_minutos=1):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco) 

    # Consulta para pegar os gols do primeiro tempo
    gols_query = '''SELECT tempo FROM gols'''
    gols = pd.read_sql_query(gols_query, conn)

    intervalos = np.arange(0, gols['tempo'].astype(int).max() + intervalo_minutos, intervalo_minutos)

    # Plotando os gráficos
    fig1, ax1 = plt.subplots()

    # Histograma dos gols do primeiro tempo
    ax1.hist(gols['tempo'].astype(int), bins=intervalos, edgecolor='black', color='skyblue', label='Tempo Normal')
    ax1.set_title('Histograma de Gols do Primeiro Tempo')
    ax1.set_xlabel('Intervalo de Minutos do Gol')
    ax1.set_ylabel('Quantidade de Gols')
    ax1.set_xticks(intervalos)
    ax1.legend()

    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plotar_matriz_correlacoes(matriz_correlacao):
    plt.figure(figsize=(10, 8))
    sns.heatmap(matriz_correlacao, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Matriz de Correlação entre Campeonatos")
    plt.show()