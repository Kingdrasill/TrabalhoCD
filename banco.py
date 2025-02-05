import sqlite3

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
            dados_jogo['faltas_mandante'], dados_jogo['posse_mandante'], dados_jogo['finalizacoes_mandante'], dados_jogo['escanteios_mandante'],
            dados_jogo['faltas_visitante'], dados_jogo['posse_visitante'], dados_jogo['finalizacoes_visitante'], dados_jogo['escanteios_visitante'],
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

def get_id_time(nome_time, cursor):
    cursor.execute(f"""
        SELECT id FROM times
            WHERE nome = '{nome_time}'
    """)
    return cursor.fetchone()