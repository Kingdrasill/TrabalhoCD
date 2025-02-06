import test
import testar_banco

# Tipo do campeonato - 0 para mata mata, 1 para campeonatos de pontos corridos
#test.extrair_campeonato('https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766', "Campeonato Brasileiro", 2024, 1)

# test.extrair_campeonato("https://www.sofascore.com/pt/torneio/futebol/france/ligue-1/34#id:52571","Ligue 1", "2024", 1)
# test.extrair_dados_links("Ligue 1", "2024")

testar_banco.verificar_jogos_faltantes('bancos/Ligue 1 2024.db', id_campeonato=1, id_inicial=1, id_final=18)