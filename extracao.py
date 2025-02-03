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

def coletar_links_jogos():
    try:
        # Aguarda a div dos jogos carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Box.kiSsvW"))
        )

        # Encontra todos os jogos na div
        jogos = driver.find_elements(By.CLASS_NAME, "Box.klGMtt.sc-efac74ba-1.kugaRD")

        links = []
        for jogo in jogos:
            try:
                ActionChains(driver).move_to_element(jogo).click().perform()

                # Aguarda a div de informações preliminares carregar
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "Box.klGMtt.sc-34673537-0.bYPUQx.widget"))
                )
                # mostrar_mais = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="show_more"] button')
                # print(mostrar_mais)
                # link = mostrar_mais.get_attribute("href")
                mostrar_mais = driver.find_element(By.CSS_SELECTOR, '[data-testid="show_more"]')
                link = mostrar_mais.get_attribute("href")
                links.append(link)
            except Exception as e:
                print(f"Erro ao coletar link de um jogo: {e}")
                continue

        return links

    except Exception as e:
        print(f"Erro ao coletar links dos jogos: {e}")
        return []

def processar_jogo(link):
    try:
        # Abre o link em uma nova aba
        driver.execute_script("window.open('');")  # Abre uma nova aba
        driver.switch_to.window(driver.window_handles[1])  # Muda para a nova aba
        driver.get(link)  # Navega para o link do jogo

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Seletores para os dados do jogo
        dados_jogo = {
            "posse_mandante": None,
            "posse_visitante": None,
            "finalizacoes_mandante": None,
            "finalizacoes_visitante": None,
            "faltas_mandante": None,
            "faltas_visitante": None,
            "escanteios_mandante": None,
            "escanteios_visitante": None
        }

        # Define os textos-alvo que vamos buscar
        estatisticas_interesse = ["Finalizações", "Faltas", "Escanteios", "Posse de bola"]
        
        dados_jogo = {}

        for estatistica in estatisticas_interesse:
            # Busca por elementos que contenham o texto da estatística
            elemento_estatistica = soup.find(lambda tag: tag.name == "span" and estatistica in tag.text)

            if elemento_estatistica:
                # Subir até o pai do pai para encontrar a estrutura completa
                elemento_completo = elemento_estatistica.find_parent("div").find_parent("div")
                
                # Extrair os valores (times à esquerda e à direita)
                valores = elemento_completo.find_all("span", class_="Text")
                
                if len(valores) >= 3:
                    valor_esquerda = valores[0].text.strip()
                    valor_direita = valores[2].text.strip()
                    print(f"{estatistica}: {valor_esquerda} - {valor_direita}")
                else:
                    print(f"Erro ao extrair valores para {estatistica}")
            else:
                print(f"Estatística '{estatistica}' não encontrada.")

        return dados_jogo

    except Exception as e:
        print(f"Erro ao processar o jogo {link}: {e}")

    finally:
        # Fecha a aba do jogo e volta para a aba principal
        driver.close()
        driver.switch_to.window(driver.window_handles[0])  # Volta para a aba principal

# Função para navegar para a página anterior (rodada anterior)
def navegar_para_pagina_anterior():
    try:
        # Encontra o botão de voltar
        botao_voltar = driver.find_element(By.CSS_SELECTOR, 'button.Button.iCnTrv')

        # Clica no botão de voltar
        ActionChains(driver).move_to_element(botao_voltar).click().perform()

        # Aguarda a página recarregar
        time.sleep(3)

    except Exception as e:
        print(f"Erro ao navegar para a página anterior: {e}")


# Abrindo a página
url = 'https://www.sofascore.com/pt/torneio/futebol/brazil/brasileirao-serie-a/325#id:58766'
driver.get(url)

nome = "Campeonato Brasileiro"
ano = 2024
tipo = 1
nome_banco = nome + " " + str(ano)

banco.criar_banco(nome_banco)

database = banco.sqlite3.connect(f'bancos/{nome_banco}.db')

if tipo == 1:
    coletar_classificacao(nome, ano, 1, database)

# Loop para navegar pelas rodadas
while True:
    # Coleta os links dos jogos da rodada atual
    links_jogos = coletar_links_jogos()

    # Tenta navegar para a página anterior
    try:
        navegar_para_pagina_anterior()
    except:
        print("Não há mais rodadas anteriores.")
        break

print(len(links_jogos))
# Processa cada jogo
# for link in links_jogos:
#     processar_jogo(link)
#     break

driver.quit()

# times = cursor.execute('''
#     SELECT * FROM times
# ''')

# for i in times:
#     print(i)

