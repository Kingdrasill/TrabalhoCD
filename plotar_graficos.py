import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

def plotar_gols_minuto(caminho_banco):
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

    # Plotando os gráficos
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Histograma dos gols do primeiro tempo
    axes[0].hist(gols_primeiro_tempo['tempo'].astype(int), bins=range(0, gols_primeiro_tempo['tempo'].astype(int).max()), edgecolor='black', color='skyblue')
    axes[0].set_title('Histograma de Gols do Primeiro Tempo')
    axes[0].set_xlabel('Minuto do Gol')
    axes[0].set_ylabel('Quantidade de Gols')

    # Histograma dos gols do segundo tempo
    axes[1].hist(gols_segundo_tempo['tempo'].astype(int), bins=range(46, gols_segundo_tempo['tempo'].astype(int).max()), edgecolor='black', color='salmon')
    axes[1].set_title('Histograma de Gols do Segundo Tempo')
    axes[1].set_xlabel('Minuto do Gol')
    axes[1].set_ylabel('Quantidade de Gols')

    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()
