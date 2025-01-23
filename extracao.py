import banco
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sys


# Configurando a saída padrão para UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Inicializando o WebDriver
driver = webdriver.Chrome()

# Abrindo a página
url = 'https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766'
driver.get(url)

nome = "Campeonato Brasileiro"
ano = 2024
tipo = 1
nome_banco = nome + " " + str(ano)

banco.criar_banco(nome_banco)

database = banco.sqlite3.connect(f'bancos/{nome_banco}.db')
cursor = database.cursor()

cursor.execute('''
    INSERT INTO campeonatos (nome, ano, tipo)
    VALUES (?, ?, ?)
''', (nome, ano, tipo))
id_campeonato = cursor.lastrowid

conteudo_pagina = driver.page_source

# Utilizando BeautifulSoup para parsear o HTML
soup = BeautifulSoup(conteudo_pagina, 'html.parser')

# Extraindo os times pela classe fsoviT
times = soup.find_all(class_='fsoviT')

# Imprimindo os nomes dos times
for i, time in enumerate(times, start=1):
    cursor.execute('''
        INSERT INTO times (nome)
        VALUES (?)
    ''', (str(time.text),))
    id_time = cursor.lastrowid

    cursor.execute('''
        INSERT INTO classificacoes (id_campeonato, id_time, posicao)
        VALUES (?, ?, ?)
    ''', (id_campeonato, id_time, i))

times = cursor.execute('''
    SELECT * FROM times
''')

for i in times:
    print(i)

database.commit()

# Fechando o driver
driver.quit()