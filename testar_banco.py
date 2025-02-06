import banco

def verificar_jogos_faltantes(caminho_banco, id_campeonato, id_inicial, id_final):
    conn = banco.sqlite3.connect(caminho_banco)
    cursor = conn.cursor()

    # Consulta para buscar os nomes dos times e seus IDs
    cursor.execute("SELECT id, nome FROM times WHERE id BETWEEN ? AND ?", (id_inicial, id_final))
    times_dict = dict(cursor.fetchall())  # dicionário {id: nome}

    jogos_verificados = set()

    for id_mandante in range(id_inicial, id_final + 1):
        for id_visitante in range(id_mandante + 1, id_final + 1):  # Evita verificações duplicadas
            time_mandante = times_dict[id_mandante]
            time_visitante = times_dict[id_visitante]

            cursor.execute('''
                SELECT COUNT(*) 
                FROM jogos 
                WHERE id_campeonato = ? AND
                      ((id_mandante = ? AND id_visitante = ?) OR
                      (id_mandante = ? AND id_visitante = ?))
            ''', (id_campeonato, id_mandante, id_visitante, id_visitante, id_mandante))
            total_jogos = cursor.fetchone()[0]

            if total_jogos < 2:
                jogos_verificados.add((time_mandante, time_visitante))

                falta_mandante = falta_visitante = ""
                # Verificar qual jogo está faltando
                cursor.execute('''
                    SELECT id_mandante, id_visitante 
                    FROM jogos 
                    WHERE id_campeonato = ? AND
                          ((id_mandante = ? AND id_visitante = ?) OR
                          (id_mandante = ? AND id_visitante = ?))
                ''', (id_campeonato, id_mandante, id_visitante, id_visitante, id_mandante))
                registros = cursor.fetchall()

                tem_ida = any(jogo == (id_mandante, id_visitante) for jogo in registros)
                tem_volta = any(jogo == (id_visitante, id_mandante) for jogo in registros)

                if not tem_ida:
                    falta_mandante = f"falta jogo com {time_mandante} como mandante e {time_visitante} como visitante"
                if not tem_volta:
                    falta_visitante = f"falta jogo com {time_visitante} como mandante e {time_mandante} como visitante"

                faltantes = [msg for msg in [falta_mandante, falta_visitante] if msg]
                print(f"Times {time_mandante} e {time_visitante}: {', '.join(faltantes)}")

    conn.close()
