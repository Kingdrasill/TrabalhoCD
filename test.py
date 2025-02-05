import banco
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests

# Configurando a saída padrão para UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Inicializando o WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)

def coletar_classificacao(nome, ano, tipo, database):
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

    database.commit()

def coletar_links_jogos(links):
    try:
        # Aguarda a div dos jogos carregar
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Box.kiSsvW"))
        )

        # Encontra todos os jogos na div
        jogos = driver.find_elements(By.CLASS_NAME, "kugaRD")

        for jogo in jogos:
            try:
                ActionChains(driver).move_to_element(jogo).click().perform()

                print(jogo.tag_name)

                time.sleep(1)
            except Exception as e:
                print(f"Erro ao coletar link de um jogo: {e}")
                continue

    except Exception as e:
        print(f"Erro ao coletar links dos jogos: {e}")
        return []

# Função para navegar para a página anterior (rodada anterior)
def navegar_para_pagina_anterior():
    try:
        parent = driver.find_element(By.CLASS_NAME, 'gURdCf')

        children = parent.find_elements(By.XPATH, './*')

        if children and children[0].is_displayed():
            # Clica no botão de voltar
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(children[0]))

            # Click using JavaScript to avoid unwanted navigation
            driver.execute_script("arguments[0].click();", children[0])
            
            # Aguarda a página recarregar
            time.sleep(3)

            return True
        else:
            return False

    except Exception as e:
        print(f"Erro ao navegar para a página anterior: {e}")


# Abrindo a página
url = 'https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766'
#url = "https://www.sofascore.com/pt/torneio/futebol/germany/bundesliga/35#id:52608"
driver.get(url)

nome = "Campeonato Brasileiro"
ano = 2024
tipo = 1
nome_banco = nome + " " + str(ano)

banco.criar_banco(nome_banco)

database = banco.sqlite3.connect(f'bancos/{nome_banco}.db')

time.sleep(5)

links_jogos = []
# Loop para navegar pelas rodadas
while True:
    # Coleta os links dos jogos da rodada atual
    coletar_links_jogos(links_jogos)
    print(len(links_jogos))
    # Tenta navegar para a página anterior
    try:
        if not navegar_para_pagina_anterior():
            print("Não há mais rodadas anteriores.")
            break
    except:
        print("ERRO - Não há mais rodadas anteriores.")
        break

print(len(links_jogos))

driver.quit()