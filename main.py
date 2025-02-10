import test
# import testar_banco
import banco
# import extracao
import juncao_banco
import glob
import plotar_graficos
import pandas as pd
import sqlite3
import estatisticas

# Tipo do campeonato - 0 para mata mata, 1 para campeonatos de pontos corridos
#test.extrair_campeonato('https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766', "Campeonato Brasileiro", 2024, 1)

# test.extrair_campeonato("https://www.sofascore.com/pt/torneio/futebol/south-america/conmebol-libertadores/384#id:47974","Libertadores", 2023, 2)
# test.extrair_dados_links("Libertadores", 2023)

# testar_banco.verificar_jogos_faltantes('bancos/Ligue 1 2022.db', id_campeonato=1, id_inicial=2, id_final=23)


### Se quiser retirar um jogo específico
# dados_jogo = extracao.processar_jogo("https://www.sofascore.com/pt/football/match/racing-de-montevideo-corinthians/hOskak#id:12172399", {"Racing":1,"Corinthians":4})

# database = banco.sqlite3.connect(f'bancos/Sudamericana 2024.db')

# banco.salvar_jogo_no_banco(dados_jogo,database)


# Juntar os bancos
# banco.criar_banco("banco_geral")

# bancos_paths = glob.glob("bancos/*.db")
# for banco_path in bancos_paths:
#     juncao_banco.consolidar_banco(banco_path, "banco_geral.db")

##########################################################################################################################################################
# plotar_graficos.plotar_gols_minuto("bancos/La Liga 2021.db")

# plotar_graficos.plotar_gols_minuto("banco_geral.db", 3)
# plotar_graficos.plotar_gols_minuto_jogo_inteiro("banco_geral.db", 3)

# campeonatos = [("Campeonato Brasileiro", 2024),("Campeonato Brasileiro", 2023),("Premier League", 2024),("Premier League", 2023)]
# plotar_graficos.plot_gols_campeonatos("banco_geral.db",campeonatos,1)

# maior_media = 0
# melhor_i = 0
# melhor_matriz = []
# for i in range(1,16):
#     matriz_correlacao, mean_correlacao = estatisticas.calcular_correlacoes(i)
#     if mean_correlacao > maior_media:
#         maior_media = mean_correlacao
#         melhor_i = i
#         melhor_matriz = matriz_correlacao

# print(f"O melhor intervalo testado foi: {melhor_i}")
# plotar_graficos.plotar_matriz_correlacoes(melhor_matriz)

# matriz_correlacao, mean_correlacao = estatisticas.calcular_correlacoes(5)
# plotar_graficos.plotar_matriz_correlacoes(matriz_correlacao)

# dados_A = banco.get_gols("Campeonato Brasileiro", 2022)
# dados_B = banco.get_gols("Campeonato Brasileiro", 2021)

# dados_A['tempo'] = dados_A['tempo'].astype(int)
# dados_B['tempo'] = dados_B['tempo'].astype(int)

# for i in range(1,11):
#     grupo_A = plotar_graficos.agrupar_por_intervalo(dados_A, i)
#     grupo_B = plotar_graficos.agrupar_por_intervalo(dados_B, i)
#     print(f"Correlação A com B para intervalos de {i} minutos:")
#     estatisticas.correlacao(grupo_A, grupo_B)

# plotar_graficos.plot_gols_campeonatos("banco_geral.db",[("Campeonato Brasileiro", 2024),("Campeonato Brasileiro", 2023),("Campeonato Brasileiro", 2022),("Campeonato Brasileiro", 2021)],5)

# grupo_A = plotar_graficos.agrupar_por_intervalo(dados_A, melhor_i)
# grupo_B = plotar_graficos.agrupar_por_intervalo(dados_B, melhor_i)
# estatisticas.correlacao(grupo_A, grupo_B)

caminho_banco = "banco_geral.db"
# nome_campeonato = "Campeonato Brasileiro"
# ano_campeonato = 2024
# plotar_graficos.plotar_relacoes_campeonato(caminho_banco, nome_campeonato, ano_campeonato)

# estatisticas.ranking_placares_por_campeonato(caminho_banco)

# plotar_graficos.plotar_gols_minuto_jogo_todo(caminho_banco, 1)
# plotar_graficos.plotar_gols_tipo2_3(caminho_banco,1)
# plotar_graficos.plotar_media_gols_faltas(caminho_banco)
plotar_graficos.plotar_media_gols_por_cartoes_vermelhos(caminho_banco)