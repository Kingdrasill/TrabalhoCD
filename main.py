import test
# import testar_banco
import banco
# import extracao
import juncao_banco
import glob
import plotar_graficos

# Tipo do campeonato - 0 para mata mata, 1 para campeonatos de pontos corridos
#test.extrair_campeonato('https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766', "Campeonato Brasileiro", 2024, 1)

# test.extrair_campeonato("https://www.sofascore.com/pt/torneio/futebol/south-america/conmebol-sudamericana/480#id:35645","Sudamericana", 2021, 2)
# test.extrair_dados_links("Sudamericana", 2021)

# testar_banco.verificar_jogos_faltantes('bancos/Ligue 1 2022.db', id_campeonato=1, id_inicial=2, id_final=23)


### Se quiser retirar um jogo específico
# dados_jogo = extracao.processar_jogo("https://www.sofascore.com/pt/football/match/racing-de-montevideo-corinthians/hOskak#id:12172399", {"Racing":1,"Corinthians":4})

# database = banco.sqlite3.connect(f'bancos/Sudamericana 2024.db')

# banco.salvar_jogo_no_banco(dados_jogo,database)


## Juntar os bancos
# banco.criar_banco("banco_geral")

# bancos_paths = glob.glob("bancos/*.db")
# for banco_path in bancos_paths:
#     juncao_banco.consolidar_banco(banco_path, "banco_geral.db")

# plotar_graficos.plotar_gols_minuto("bancos/La Liga 2021.db")

plotar_graficos.plotar_gols_minuto("banco_geral.db")
