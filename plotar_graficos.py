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

def plotar_gols_minuto_jogo_todo(caminho_banco, intervalo_minutos=1):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para pegar os gols
    gols_query = '''
    SELECT tempo, acrescimos
    FROM gols
    '''
    gols = pd.read_sql_query(gols_query, conn)

    # Separação das cores para gols fora do tempo normal
    gols['tempo'] = gols['tempo'].astype(int)
    gols['acrescimos'] = gols['acrescimos'].astype(int)

    # Organizar dados para exibição
    intervalos = np.arange(0, gols['tempo'].max() + intervalo_minutos, intervalo_minutos)

    # Contar gols por intervalo
    contagem_normais = np.histogram(gols[gols['acrescimos'] == 0]['tempo'], bins=intervalos)[0]
    contagem_acrescimos = np.histogram(gols[gols['acrescimos'] == 1]['tempo'], bins=intervalos)[0]

    # Plotando os gráficos empilhados
    fig, ax = plt.subplots()

    # Barras empilhadas
    ax.bar(intervalos[:-1], contagem_normais, width=intervalo_minutos, color='skyblue', edgecolor='black', label='Tempo Normal')
    ax.bar(intervalos[:-1], contagem_acrescimos, width=intervalo_minutos, bottom=contagem_normais, color='orange', edgecolor='black', label='Acréscimos')

    ax.set_title('Histograma de Gols por Minuto')
    ax.set_xlabel('Minuto do Gol')
    ax.set_ylabel('Quantidade de Gols')
    ax.set_xticks(intervalos)
    ax.legend()

    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plotar_gols_tipo2_3(caminho_banco, intervalo_minutos=1):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para pegar apenas os gols de tipo 2 e tipo 3
    gols_query = '''
    SELECT tempo, tipo
    FROM gols
    WHERE tipo IN (2, 3)
    '''
    gols = pd.read_sql_query(gols_query, conn)

    # Organizar dados para exibição
    gols['tempo'] = gols['tempo'].astype(int)
    intervalos = np.arange(0, gols['tempo'].max() + intervalo_minutos, intervalo_minutos)

    # Contar gols por tipo
    contagem_tipo2 = np.histogram(gols[gols['tipo'] == 2]['tempo'], bins=intervalos)[0]
    contagem_tipo3 = np.histogram(gols[gols['tipo'] == 3]['tempo'], bins=intervalos)[0]

    # Plotando os gráficos empilhados
    fig, ax = plt.subplots()

    # Barras empilhadas
    ax.bar(intervalos[:-1], contagem_tipo2, width=intervalo_minutos, color='royalblue', edgecolor='black', label='Pênalti')
    ax.bar(intervalos[:-1], contagem_tipo3, width=intervalo_minutos, bottom=contagem_tipo2, color='firebrick', edgecolor='black', label='Gol Contra')

    ax.set_title('Gols por Minuto (Pênalti e Gol Contra)')
    ax.set_xlabel('Minuto do Gol')
    ax.set_ylabel('Quantidade de Gols')
    ax.set_xticks(intervalos)
    ax.legend()

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

def plotar_hist_gols_posse_bola(caminho_banco):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para obter jogos com posse de bola > 0 e gols
    query_jogos = '''
    SELECT id, id_mandante, id_visitante, posse_mandante, posse_visitante
    FROM jogos
    WHERE posse_mandante > 0 AND posse_visitante > 0
    '''
    jogos_df = pd.read_sql_query(query_jogos, conn)

    # Consulta para obter os gols
    query_gols = '''
    SELECT id_jogo, id_time
    FROM gols
    '''
    gols_df = pd.read_sql_query(query_gols, conn)

    # Contar os gols por mandante e visitante
    gols_contagem = gols_df.groupby(['id_jogo', 'id_time']).size().reset_index(name='gols')

    # Agregar os gols aos dados de jogos
    mandante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_mandante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)
    visitante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_visitante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)

    mandante_gols['gols'] = mandante_gols['gols'].astype(int)
    visitante_gols['gols'] = visitante_gols['gols'].astype(int)

    # Organizar os dados para o gráfico
    posicao_gols = []

    for _, row in mandante_gols.iterrows():
        posicao_gols.append((row['posse_mandante'], row['gols']))

    for _, row in visitante_gols.iterrows():
        posicao_gols.append((row['posse_visitante'], row['gols']))

    # Criar DataFrame com os dados
    posicao_gols_df = pd.DataFrame(posicao_gols, columns=['posse_de_bola', 'gols'])

    min_posse = min(posicao_gols_df['posse_de_bola'])
    max_posse = max(posicao_gols_df['posse_de_bola'])

    plt.figure(figsize=(10, 6))
    plt.hist(posicao_gols_df['posse_de_bola'], bins=int(max_posse - min_posse), weights=posicao_gols_df['gols'], edgecolor='black')
    plt.title('Número de Gols x Posse de Bola')
    plt.xlabel('Posse de Bola (%)')
    plt.ylabel('Número de Gols')
    plt.tight_layout()
    plt.show()

    # Plotar o histograma 2d
    # plt.figure(figsize=(10, 6))
    # plt.hist2d(posicao_gols_df['posse_de_bola'], posicao_gols_df['gols'], bins=[10, 5], cmap='Blues')
    # plt.colorbar(label='Frequência')
    # plt.title('Número de Gols x Posse de Bola')
    # plt.xlabel('Posse de Bola (%)')
    # plt.ylabel('Número de Gols')
    # plt.tight_layout()
    # plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plotar_hist_gols_finalizacoes(caminho_banco):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para obter jogos com posse de bola > 0 e gols
    query_jogos = '''
    SELECT id, id_mandante, id_visitante, finalizacoes_mandante, finalizacoes_visitante
    FROM jogos
    WHERE finalizacoes_mandante > 0 AND finalizacoes_visitante > 0
    '''
    jogos_df = pd.read_sql_query(query_jogos, conn)

    # Consulta para obter os gols
    query_gols = '''
    SELECT id_jogo, id_time
    FROM gols
    '''
    gols_df = pd.read_sql_query(query_gols, conn)

    # Contar os gols por mandante e visitante
    gols_contagem = gols_df.groupby(['id_jogo', 'id_time']).size().reset_index(name='gols')

    # Agregar os gols aos dados de jogos
    mandante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_mandante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)
    visitante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_visitante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)

    mandante_gols['gols'] = mandante_gols['gols'].astype(int)
    visitante_gols['gols'] = visitante_gols['gols'].astype(int)

    # Organizar os dados para o gráfico
    posicao_gols = []

    for _, row in mandante_gols.iterrows():
        posicao_gols.append((row['finalizacoes_mandante'], row['gols']))

    for _, row in visitante_gols.iterrows():
        posicao_gols.append((row['finalizacoes_visitante'], row['gols']))

    # Criar DataFrame com os dados
    posicao_gols_df = pd.DataFrame(posicao_gols, columns=['finalizacoes', 'gols'])

    min_fin = min(posicao_gols_df['finalizacoes'])
    max_fin = max(posicao_gols_df['finalizacoes'])

    plt.figure(figsize=(10, 6))
    plt.hist(posicao_gols_df['finalizacoes'], bins=int(max_fin - min_fin), weights=posicao_gols_df['gols'], edgecolor='black')
    plt.title('Número de Gols x Finalizações')
    plt.xlabel('Finalizações')
    plt.ylabel('Número de Gols')
    plt.tight_layout()
    plt.show()

    # Plotar o histograma 2d
    # plt.figure(figsize=(10, 6))
    # plt.hist2d(posicao_gols_df['posse_de_bola'], posicao_gols_df['gols'], bins=[10, 5], cmap='Blues')
    # plt.colorbar(label='Frequência')
    # plt.title('Número de Gols x Posse de Bola')
    # plt.xlabel('Posse de Bola (%)')
    # plt.ylabel('Número de Gols')
    # plt.tight_layout()
    # plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plotar_media_gols_posse_bola(caminho_banco):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para obter jogos com posse de bola > 0 e gols
    query_jogos = '''
    SELECT id, id_mandante, id_visitante, posse_mandante, posse_visitante
    FROM jogos
    WHERE posse_mandante > 0 AND posse_visitante > 0
    '''
    jogos_df = pd.read_sql_query(query_jogos, conn)

    # Consulta para obter os gols
    query_gols = '''
    SELECT id_jogo, id_time
    FROM gols
    '''
    gols_df = pd.read_sql_query(query_gols, conn)

    # Contar os gols por mandante e visitante
    gols_contagem = gols_df.groupby(['id_jogo', 'id_time']).size().reset_index(name='gols')

    # Agregar os gols aos dados de jogos
    mandante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_mandante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)
    visitante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_visitante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)

    mandante_gols['gols'] = mandante_gols['gols'].astype(int)
    visitante_gols['gols'] = visitante_gols['gols'].astype(int)

    # Organizar os dados para cálculo da média de gols por posse de bola
    posicao_gols = []

    for _, row in mandante_gols.iterrows():
        posicao_gols.append((row['posse_mandante'], row['gols']))

    for _, row in visitante_gols.iterrows():
        posicao_gols.append((row['posse_visitante'], row['gols']))

    # Criar DataFrame com os dados
    posicao_gols_df = pd.DataFrame(posicao_gols, columns=['posse_de_bola', 'gols'])

    # Agrupar por posse de bola e calcular a média de gols
    media_gols_df = posicao_gols_df.groupby('posse_de_bola', as_index=False)['gols'].mean().sort_values('posse_de_bola')

    # Plotar o gráfico de linha
    plt.figure(figsize=(10, 6))
    plt.plot(media_gols_df['posse_de_bola'], media_gols_df['gols'], marker='o', color='blue')
    plt.title('Média de Gols por Posse de Bola')
    plt.xlabel('Posse de Bola (%)')
    plt.ylabel('Média de Gols')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plotar_media_gols_finalizacoes(caminho_banco):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para obter jogos com posse de bola > 0 e gols
    query_jogos = '''
    SELECT id, id_mandante, id_visitante, finalizacoes_mandante, finalizacoes_visitante
    FROM jogos
    WHERE finalizacoes_mandante > 0 AND finalizacoes_visitante > 0
    '''
    jogos_df = pd.read_sql_query(query_jogos, conn)

    # Consulta para obter os gols
    query_gols = '''
    SELECT id_jogo, id_time
    FROM gols
    '''
    gols_df = pd.read_sql_query(query_gols, conn)

    # Contar os gols por mandante e visitante
    gols_contagem = gols_df.groupby(['id_jogo', 'id_time']).size().reset_index(name='gols')

    # Agregar os gols aos dados de jogos
    mandante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_mandante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)
    visitante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_visitante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)

    mandante_gols['gols'] = mandante_gols['gols'].astype(int)
    visitante_gols['gols'] = visitante_gols['gols'].astype(int)

    # Organizar os dados para cálculo da média de gols por posse de bola
    posicao_gols = []

    for _, row in mandante_gols.iterrows():
        posicao_gols.append((row['finalizacoes_mandante'], row['gols']))

    for _, row in visitante_gols.iterrows():
        posicao_gols.append((row['finalizacoes_visitante'], row['gols']))

    # Criar DataFrame com os dados
    posicao_gols_df = pd.DataFrame(posicao_gols, columns=['finalizacoes', 'gols'])

    # Agrupar por posse de bola e calcular a média de gols
    media_gols_df = posicao_gols_df.groupby('finalizacoes', as_index=False)['gols'].mean().sort_values('finalizacoes')

    # Plotar o gráfico de linha
    plt.figure(figsize=(10, 6))
    plt.plot(media_gols_df['finalizacoes'], media_gols_df['gols'], marker='o', color='blue')
    plt.title('Média de Gols por Finalizações')
    plt.xlabel('Finalizações')
    plt.ylabel('Média de Gols')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plotar_media_gols_escanteios(caminho_banco):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para obter jogos com posse de bola > 0 e gols
    query_jogos = '''
    SELECT id, id_mandante, id_visitante, escanteios_mandante, escanteios_visitante
    FROM jogos
    WHERE escanteios_mandante > 0 AND escanteios_visitante > 0
    '''
    jogos_df = pd.read_sql_query(query_jogos, conn)

    # Consulta para obter os gols
    query_gols = '''
    SELECT id_jogo, id_time
    FROM gols
    '''
    gols_df = pd.read_sql_query(query_gols, conn)

    # Contar os gols por mandante e visitante
    gols_contagem = gols_df.groupby(['id_jogo', 'id_time']).size().reset_index(name='gols')

    # Agregar os gols aos dados de jogos
    mandante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_mandante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)
    visitante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_visitante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)

    mandante_gols['gols'] = mandante_gols['gols'].astype(int)
    visitante_gols['gols'] = visitante_gols['gols'].astype(int)

    # Organizar os dados para cálculo da média de gols por posse de bola
    posicao_gols = []

    for _, row in mandante_gols.iterrows():
        posicao_gols.append((row['escanteios_mandante'], row['gols']))

    for _, row in visitante_gols.iterrows():
        posicao_gols.append((row['escanteios_visitante'], row['gols']))

    # Criar DataFrame com os dados
    posicao_gols_df = pd.DataFrame(posicao_gols, columns=['escanteios', 'gols'])

    # Agrupar por posse de bola e calcular a média de gols
    media_gols_df = posicao_gols_df.groupby('escanteios', as_index=False)['gols'].mean().sort_values('escanteios')

    # Plotar o gráfico de linha
    plt.figure(figsize=(10, 6))
    plt.plot(media_gols_df['escanteios'], media_gols_df['gols'], marker='o', color='blue')
    plt.title('Média de Gols por Escanteios')
    plt.xlabel('Escanteios')
    plt.ylabel('Média de Gols')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()

def plotar_media_gols_faltas(caminho_banco):
    # Conexão com o banco de dados
    conn = sqlite3.connect(caminho_banco)

    # Consulta para obter jogos com posse de bola > 0 e gols
    query_jogos = '''
    SELECT id, id_mandante, id_visitante, faltas_mandante, faltas_visitante
    FROM jogos
    WHERE faltas_mandante > 0 AND faltas_visitante > 0
    '''
    jogos_df = pd.read_sql_query(query_jogos, conn)

    # Consulta para obter os gols
    query_gols = '''
    SELECT id_jogo, id_time
    FROM gols
    '''
    gols_df = pd.read_sql_query(query_gols, conn)

    # Contar os gols por mandante e visitante
    gols_contagem = gols_df.groupby(['id_jogo', 'id_time']).size().reset_index(name='gols')

    # Agregar os gols aos dados de jogos
    mandante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_mandante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)
    visitante_gols = jogos_df.merge(gols_contagem, left_on=['id', 'id_visitante'], right_on=['id_jogo', 'id_time'], how='left').fillna(0)

    mandante_gols['gols'] = mandante_gols['gols'].astype(int)
    visitante_gols['gols'] = visitante_gols['gols'].astype(int)

    # Organizar os dados para cálculo da média de gols por posse de bola
    posicao_gols = []

    for _, row in mandante_gols.iterrows():
        posicao_gols.append((row['faltas_visitante'], row['gols']))

    for _, row in visitante_gols.iterrows():
        posicao_gols.append((row['faltas_mandante'], row['gols']))

    # Criar DataFrame com os dados
    posicao_gols_df = pd.DataFrame(posicao_gols, columns=['faltas', 'gols'])

    # Agrupar por posse de bola e calcular a média de gols
    media_gols_df = posicao_gols_df.groupby('faltas', as_index=False)['gols'].mean().sort_values('faltas')

    # Plotar o gráfico de linha
    plt.figure(figsize=(10, 6))
    plt.plot(media_gols_df['faltas'], media_gols_df['gols'], marker='o', color='blue')
    plt.title('Média de Gols por Faltas')
    plt.xlabel('Faltas')
    plt.ylabel('Média de Gols')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Fechar a conexão com o banco de dados
    conn.close()