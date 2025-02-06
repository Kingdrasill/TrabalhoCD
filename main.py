import test
import testar_banco

# Tipo do campeonato - 0 para mata mata, 1 para campeonatos de pontos corridos
#test.extrair_campeonato('https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766', "Campeonato Brasileiro", 2024, 1)

#test.extrair_campeonato("https://www.sofascore.com/pt/torneio/futebol/europe/uefa-champions-league/7#id:52162","Liga dos Campeões", 2024, 2)
test.extrair_dados_links("Liga dos Campeões", 2024)

#testar_banco.verificar_jogos_faltantes('bancos/La Liga 2022.db', id_campeonato=1, id_inicial=1, id_final=20)