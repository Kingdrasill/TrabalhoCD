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
            FOREIGN KEY(id_jogo) references jogos(id)
            FOREIGN KEY(id_time) references times(id)
        )''')

    conn.commit() 

    conn.close()