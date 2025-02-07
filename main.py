import test
import testar_banco
import banco

# Tipo do campeonato - 0 para mata mata, 1 para campeonatos de pontos corridos
#test.extrair_campeonato('https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766', "Campeonato Brasileiro", 2024, 1)

#test.extrair_campeonato("https://www.sofascore.com/pt/torneio/futebol/europe/uefa-champions-league/7#id:29267","Liga dos Campeões", 2021, 2)
# test.extrair_dados_links("Liga dos Campeões", 2021)

# testar_banco.verificar_jogos_faltantes('bancos/Ligue 1 2022.db', id_campeonato=1, id_inicial=2, id_final=23)

dados_jogo = {
    'id_mandante': 65,
    'id_visitante': 38,
    'faltas_mandante': -1,
    'faltas_mandante': -1,
    'posse_mandante': -1,
    'finalizacoes_mandante': -1,
    'escanteios_mandante': -1,
    'faltas_visitante': -1,
    'posse_visitante': -1,
    'finalizacoes_visitante': -1,
    'escanteios_visitante': -1,
    'gols_mandante': [],
    'gols_visitante': [["Gol", 94, 0]],
    'cartoes_mandante': [["Amarelo", 17, 0],["Amarelo",62,0],["Amarelo",73,0],["Amarelo",74,0],["Vermelho",97,0]],
    'cartoes_visitante': [["Amarelo", 39, 0],["Amarelo",74,0],["Amarelo",116,0]] ,
    'data': "19/08/2020-12:00",
}

database = banco.sqlite3.connect(f'bancos/Liga dos Campeões 2021.db')

banco.salvar_jogo_no_banco(dados_jogo,database)