import test

# Tipo do campeonato - 0 para mata mata, 1 para campeonatos de pontos corridos
#test.extrair_campeonato('https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766', "Campeonato Brasileiro", 2024, 1)

test.extrair_campeonato("https://www.sofascore.com/pt/torneio/futebol/england/premier-league/17#id:29415","Premier League", "2021", 1)
test.extrair_dados_links("Premier League", "2021")