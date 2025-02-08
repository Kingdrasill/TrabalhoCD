import sqlite3
import pandas as pd

def criar_banco(nome):
    conn = sqlite3.connect(f'bancos/{nome}.db')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS campeonatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ano INTEGER NOT NULL,
            tipo INTEGER NOT NULL
        )''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS classificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_campeonato INTEGER NOT NULL,
            id_time INTEGER NOT NULL,
            posicao INTEGER NOT NULL,
            FOREIGN KEY(id_campeonato) references campeonatos(id)
            FOREIGN KEY(id_time) references times(id)
        )''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_campeonato INTEGER NOT NULL,
            id_mandante INTEGER NOT NULL,
            id_visitante INTEGER NOT NULL,
            faltas_mandante INTEGER NOT NULL,
            posse_mandante INTEGER NOT NULL,
            finalizacoes_mandante INTEGER NOT NULL,
            escanteios_mandante INTEGER NOT NULL,
            faltas_visitante INTEGER NOT NULL,
            posse_visitante INTEGER NOT NULL,
            finalizacoes_visitante INTEGER NOT NULL,
            escanteios_visitante INTEGER NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY(id_campeonato) references campeonatos(id)
            FOREIGN KEY(id_mandante) references times(id)
            FOREIGN KEY(id_visitante) references times(id)
        )''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS gols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogo INTEGER NOT NULL,
            id_time INTEGER NOT NULL,
            tempo TEXT NOT NULL,
            tipo INTEGER NOT NULL,
            acrescimos INTEGER NOT NULL,
            FOREIGN KEY(id_jogo) references jogos(id)
            FOREIGN KEY(id_time) references times(id)
        )''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS cartoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogo INTEGER NOT NULL,
            id_time INTEGER NOT NULL,
            tempo TEXT NOT NULL,
            tipo INTEGER NOT NULL,
            acrescimos INTEGER NOT NULL,
            FOREIGN KEY(id_jogo) references jogos(id)
            FOREIGN KEY(id_time) references times(id)
        )''')

    conn.commit() 

    conn.close()

def salvar_jogo_no_banco(dados_jogo, conn):
    try:
        tem_estatisticas = any([
            dados_jogo.get('faltas_mandante'),
            dados_jogo.get('posse_mandante'),
            dados_jogo.get('finalizacoes_mandante'),
            dados_jogo.get('escanteios_mandante'),
            dados_jogo.get('faltas_visitante'),
            dados_jogo.get('posse_visitante'),
            dados_jogo.get('finalizacoes_visitante'),
            dados_jogo.get('escanteios_visitante')
        ])

        #if not tem_estatisticas:
        #    raise ValueError("Nenhuma estatística relevante encontrada para salvar o jogo.")
    
        cursor = conn.cursor()

        # Inserir dados na tabela jogos
        cursor.execute('''
            INSERT INTO jogos (
                id_campeonato, id_mandante, id_visitante,
                faltas_mandante, posse_mandante, finalizacoes_mandante, escanteios_mandante,
                faltas_visitante, posse_visitante, finalizacoes_visitante, escanteios_visitante, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,  # id_campeonato (fixo como 1)
            dados_jogo['id_mandante'], dados_jogo['id_visitante'],
            dados_jogo.get('faltas_mandante', -1),
            dados_jogo.get('posse_mandante', -1),
            dados_jogo.get('finalizacoes_mandante', -1),
            dados_jogo.get('escanteios_mandante', -1),
            dados_jogo.get('faltas_visitante', -1),
            dados_jogo.get('posse_visitante', -1),
            dados_jogo.get('finalizacoes_visitante', -1),
            dados_jogo.get('escanteios_visitante', -1),
            dados_jogo['data']
        ))


        # Obter o ID do jogo inserido
        id_jogo = cursor.lastrowid

        # Inserir gols do time mandante
        for gol in dados_jogo['gols_mandante']:
            cursor.execute('''
                INSERT INTO gols (
                    id_jogo, id_time, tempo, tipo, acrescimos
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                id_jogo, dados_jogo['id_mandante'], gol[1], 1 if gol[0] == 'Gol' else 2 if gol[0] == "Pênalti" else 3, gol[2]
            ))

        # Inserir gols do time visitante
        for gol in dados_jogo['gols_visitante']:
            cursor.execute('''
                INSERT INTO gols (
                    id_jogo, id_time, tempo, tipo, acrescimos
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                id_jogo, dados_jogo['id_visitante'], gol[1], 1 if gol[0] == 'Gol' else 2 if gol[0] == "Pênalti" else 3, gol[2]
            ))

        # Inserir cartões do time mandante
        for cartao in dados_jogo['cartoes_mandante']:
            cursor.execute('''
                INSERT INTO cartoes (
                    id_jogo, id_time, tempo, tipo, acrescimos
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                id_jogo, dados_jogo['id_mandante'], cartao[1], 1 if cartao[0] == 'Cartão amarelo' else 2, cartao[2]
            ))

        # Inserir cartões do time visitante
        for cartao in dados_jogo['cartoes_visitante']:
            cursor.execute('''
                INSERT INTO cartoes (
                    id_jogo, id_time, tempo, tipo, acrescimos
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                id_jogo, dados_jogo['id_visitante'], cartao[1], 1 if cartao[0] == 'Cartão amarelo' else 2, cartao[2]
            ))

        # Commit para salvar as alterações no banco
        conn.commit()
        print("Dados do jogo salvos com sucesso!")

    except Exception as e:
        conn.rollback()  # Desfaz as alterações em caso de erro
        print(f"Erro ao salvar os dados do jogo: {e}")
        raise

def get_id_time(nome_time, cursor):
    cursor.execute("""
        SELECT id FROM times
        WHERE nome = ?
    """, (nome_time,))
    return cursor.fetchone()

def get_id_campeonato(nome_campeonato, ano, cursor):
    cursor.execute("""
        SELECT id FROM campeonatos
        WHERE (campeonatos.nome = ? AND campeonatos.ano = ?)
    """, (nome_campeonato,ano))
    return cursor.fetchone()

def get_campeonatos():
    conn = sqlite3.connect("banco_geral.db")
    campeonatos = '''Select campeonatos.nome, campeonatos.ano FROM campeonatos'''
    return pd.read_sql_query(campeonatos, conn)

def get_gols(nome_campeonato, ano, tempo=0):
    conn = sqlite3.connect("banco_geral.db")
    if tempo == 0:
        cursor = conn.cursor()
        id_campeonato = get_id_campeonato(nome_campeonato,ano,cursor)[0]
        gols_query = '''SELECT gols.tempo 
        FROM gols
        JOIN jogos ON gols.id_jogo = jogos.id
        JOIN campeonatos ON jogos.id_campeonato = ?'''
        return pd.read_sql_query(gols_query, conn, params=(id_campeonato,))
    elif tempo == 1:
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
        return pd.read_sql_query(gols_primeiro_tempo_query, conn, params=(nome_campeonato, ano))
    else:
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
        return pd.read_sql_query(gols_segundo_tempo_query, conn, params=(nome_campeonato, ano))