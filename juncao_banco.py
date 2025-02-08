import sqlite3

def copiar_campeonato(cursor_origem, cursor_destino):
    cursor_origem.execute("SELECT nome, ano, tipo FROM campeonatos")
    campeonato = cursor_origem.fetchone()
    cursor_destino.execute("INSERT INTO campeonatos (nome, ano, tipo) VALUES (?, ?, ?)", campeonato)
    cursor_destino.execute("SELECT last_insert_rowid()")  # Obter ID do campeonato copiado
    return cursor_destino.fetchone()[0]

def copiar_times(cursor_origem, cursor_destino):
    cursor_origem.execute("SELECT id, nome FROM times")
    times = cursor_origem.fetchall()
    mapa_times = {}
    for id_antigo, nome in times:
        cursor_destino.execute("SELECT id FROM times WHERE nome = ?", (nome,))
        resultado = cursor_destino.fetchone()
        if resultado:
            mapa_times[id_antigo] = resultado[0]  # Time já existe
        else:
            cursor_destino.execute("INSERT INTO times (nome) VALUES (?)", (nome,))
            cursor_destino.execute("SELECT last_insert_rowid()")
            mapa_times[id_antigo] = cursor_destino.fetchone()[0]  # Novo ID gerado
    return mapa_times

def copiar_classificacoes(cursor_origem, cursor_destino, id_novo_campeonato, mapa_times):
    cursor_origem.execute("SELECT id_campeonato, id_time, posicao FROM classificacoes WHERE id_campeonato = ?", (1,))
    classificacoes = cursor_origem.fetchall()
    for id_campeonato, id_time, posicao in classificacoes:
        if id_campeonato == 1 and id_time in mapa_times:
            cursor_destino.execute("""
                INSERT INTO classificacoes (id_campeonato, id_time, posicao)
                VALUES (?, ?, ?)
            """, (id_novo_campeonato, mapa_times[id_time], posicao))

def copiar_jogos_gols_cartoes(cursor_origem, cursor_destino, id_novo_campeonato, mapa_times):
    cursor_origem.execute("SELECT * FROM jogos")
    jogos = cursor_origem.fetchall()
    colunas_jogos = [desc[0] for desc in cursor_origem.description]

    for jogo in jogos:
        dados_jogo = dict(zip(colunas_jogos, jogo))
        # Atualizar IDs
        dados_jogo["id_campeonato"] = id_novo_campeonato
        dados_jogo["id_mandante"] = mapa_times[dados_jogo["id_mandante"]]
        dados_jogo["id_visitante"] = mapa_times[dados_jogo["id_visitante"]]

        # Inserir jogo e capturar novo ID
        id_jogo_original = dados_jogo['id']
        del dados_jogo['id']
        cursor_destino.execute(f"""
            INSERT INTO jogos ({', '.join(dados_jogo.keys())})
            VALUES ({', '.join('?' * len(dados_jogo))})
        """, list(dados_jogo.values()))
        cursor_destino.execute("SELECT last_insert_rowid()")
        id_novo_jogo = cursor_destino.fetchone()[0]

        # Copiar Gols do Jogo
        cursor_origem.execute("SELECT id_time, tempo, tipo, acrescimos FROM gols WHERE id_jogo = ?", (id_jogo_original,))
        gols = cursor_origem.fetchall()
        for id_time, tempo, tipo, acrescimos in gols:
            cursor_destino.execute("""
                INSERT INTO gols (id_jogo, id_time, tempo, tipo, acrescimos)
                VALUES (?, ?, ?, ?, ?)
            """, (id_novo_jogo, mapa_times[id_time], tempo, tipo, acrescimos))

        # Copiar Cartões do Jogo
        cursor_origem.execute("SELECT id_time, tempo, tipo, acrescimos FROM cartoes WHERE id_jogo = ?", (id_jogo_original,))
        cartoes = cursor_origem.fetchall()
        for id_time, tempo, tipo, acrescimos in cartoes:
            cursor_destino.execute("""
                INSERT INTO cartoes (id_jogo, id_time, tempo, tipo, acrescimos)
                VALUES (?, ?, ?, ?, ?)
            """, (id_novo_jogo, mapa_times[id_time], tempo, tipo, acrescimos))

def consolidar_banco(origem_db_path, destino_db_path):
    try:
        # Conectar aos bancos de dados
        conn_origem = sqlite3.connect(origem_db_path)
        cursor_origem = conn_origem.cursor()

        conn_destino = sqlite3.connect(destino_db_path)
        cursor_destino = conn_destino.cursor()

        # 1. Copiar campeonato
        id_novo_campeonato = copiar_campeonato(cursor_origem, cursor_destino)
        print(f"Campeonato copiado com ID {id_novo_campeonato}.")

        # 2. Copiar times e mapear IDs antigos para novos
        mapa_times = copiar_times(cursor_origem, cursor_destino)
        print(f"Times copiados e mapeados: {mapa_times}")

        cursor_destino.execute(f"SELECT tipo FROM campeonatos WHERE id = {id_novo_campeonato}")
        tipo_novo_campeonato = cursor_destino.fetchone()[0]
        print(f"Tipo do campeonato: {tipo_novo_campeonato}")
        if tipo_novo_campeonato == 1:
            copiar_classificacoes(cursor_origem, cursor_destino, id_novo_campeonato, mapa_times)
            print("Classificações copiadas com sucesso.")

        # 3. Copiar jogos e atualizar gols e cartões
        copiar_jogos_gols_cartoes(cursor_origem, cursor_destino, id_novo_campeonato, mapa_times)
        print("Jogos, gols e cartões copiados com sucesso.")

        # Commit das mudanças no banco de dados consolidado
        conn_destino.commit()
        print("Banco de dados consolidado com sucesso!")

    except Exception as e:
        print(f"Erro durante a consolidação: {e}")
    finally:
        # Fechar conexões
        conn_origem.close()
        conn_destino.close()