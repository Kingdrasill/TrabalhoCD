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
from PIL import Image
import time
import re

# Configurando a saída padrão para UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Inicializando o WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

def coletar_classificacao(driver, nome, ano, tipo, database):
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

def coletar_links_jogos(driver, links):
    try:
        # Aguarda a div dos jogos carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Box.kiSsvW"))
        )

        # Encontra todos os jogos na div
        jogos = driver.find_elements(By.CLASS_NAME, "Box.klGMtt.sc-efac74ba-1.kugaRD")

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
                # soup = BeautifulSoup(driver.page_source, 'html.parser')
                # soup2 = soup.find('div', class_='Box Flex dZNeJi bnpRyo')

                # team_names = [bdi_tag.text for bdi_tag in soup2.find_all("bdi")]

                # print(team_names)

                if not driver.find_elements(By.CLASS_NAME, 'Text.dRRggn'):
                    mostrar_mais = driver.find_element(By.CSS_SELECTOR, '[data-testid="show_more"]')
                    link = mostrar_mais.get_attribute("href")
                    links.append(link)
                else:
                    print("Adiado")
            except Exception as e:
                print(f"Erro ao coletar link de um jogo: {e}")
                continue

    except Exception as e:
        print(f"Erro ao coletar links dos jogos: {e}")
        return []

# Função para navegar para a página anterior (rodada anterior)
def navegar_para_pagina_anterior(driver):
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

def extrair_campeonato(link, nome, ano, tipo):
    nome_banco = nome + " " + str(ano)
    # banco.criar_banco(nome_banco)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    database = banco.sqlite3.connect(f'bancos/{nome_banco}.db')
    cursor = database.cursor()
    # if tipo == 1:
    #     coletar_classificacao(driver, nome, ano, 1, database)
    links_jogos = []
    while True:
        # Coleta os links dos jogos da rodada atual
        coletar_links_jogos(driver, links_jogos)
        # Tenta navegar para a página anterior
        try:
            if not navegar_para_pagina_anterior(driver):
                print("Não há mais rodadas anteriores.")
                break
        except:
            print("ERRO - Não há mais rodadas anteriores.")
            break

    file_path = f"arquivos/{nome}_{str(ano)}.txt"

    # Salvar cada item do vetor em uma linha do arquivo
    with open(file_path, "w", encoding='utf-8') as file:
        for item in links_jogos:
            file.write(item + "\n")
    
    driver.quit()

def extrair_nome_time(div_time):
    bdi_tag = div_time.find('bdi', {'class': 'Text fIvzGZ'})
    if bdi_tag:
        return bdi_tag.text.strip()
    return None

def extrair_dados_links(nome, ano):
    nome_banco = nome + " " + str(ano)
    file_path = f"arquivos/{nome}_{str(ano)}.txt"
    database = banco.sqlite3.connect(f'bancos/{nome_banco}.db')
    cursor = database.cursor()

    driver = webdriver.Chrome(options=chrome_options)
    tags_auxs = ['Gol', 'Pênalti', 'Gol contra', 'Cartão amarelo', 'Cartão vermelho', '2º cartão amarelo (vermelho)']
    estatisticas_interesse = ["Finalizações", "Faltas", "Escanteios", "Posse de bola"]

    while True:
        links_jogos_faltantes = []
        # Salvar cada item do vetor em uma linha do arquivo
        with open(file_path, "r", encoding='utf-8') as file:
            while True:
                link = file.readline()
                if link == '':
                    break

                try:
                    driver.get(link)  # Navega para o link do jogo

                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Box.Flex.dZNeJi.bnpRyo')))

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    dados_jogo = {}

                    # IDs
                    div_mandante = soup.find('div', {'data-testid': 'left_team'})
                    div_visitante = soup.find('div', {'data-testid': 'right_team'})

                    nome_mandante = extrair_nome_time(div_mandante)
                    nome_visitante = extrair_nome_time(div_visitante)

                    id_mandante = banco.get_id_time(nome_mandante, cursor)[0]
                    id_visitante = banco.get_id_time(nome_visitante, cursor)[0]

                    cursor.execute(f"""
                        SELECT id FROM jogos
                            WHERE id_campeonato = 1 AND id_mandante = {id_mandante} AND id_visitante = {id_visitante}
                    """)
                    id = cursor.fetchone()

                    if not id:
                        # Pega os IDs dos times
                        dados_jogo["id_mandante"] = id_mandante
                        dados_jogo["id_visitante"] = id_visitante
                        
                        # Pega a data do jogo
                        data = driver.find_element("css selector", "span.Text.hZKSbA")
                        dados_jogo["data"] = data.text.strip()[:10] + '-' + data.text.strip()[10:]

                        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Box.fTPNOD')))
                        # Pega os cartoes e gols
                        container = driver.find_element(By.CLASS_NAME, "Box.fTPNOD")
                        filhos = container.find_elements(By.CLASS_NAME, "Box.cbmnyx")

                        gols_mandante = []
                        gols_visitante = []
                        cartoes_mandante = []
                        cartoes_visitante = []
                        
                        for filho in filhos:
                            driver.execute_script("arguments[0].scrollIntoView();", filho)
                            direcao = filho.find_element(By.TAG_NAME, 'div').get_attribute('direction')
                            mandante = False
                            if direcao == 'row':
                                mandante = True
                                
                            tempo_tag = filho.find_element(By.CSS_SELECTOR, 'div.Text.eySDEN')
                            evento_tag = filho.find_element(By.TAG_NAME, 'svg').get_attribute('innerHTML')

                            match_title = re.search(r'<title>(.*?)</title>', evento_tag)
                            if match_title:
                                evento = match_title.group(1)
                                if evento in tags_auxs:
                                    index = tags_auxs.index(evento)

                                    match_tempo  = re.match(r"(\d+)'(?:\s*\+\s*(\d+))?", tempo_tag.text.strip())

                                    primeiro_numero = int(match_tempo.group(1))
                                    segundo_numero = int(match_tempo.group(2)) if match_tempo.group(2) else 0
                                    acrescimos = True if match_tempo.group(2) else False

                                    tempo_total = primeiro_numero + segundo_numero

                                    if index <= 2:
                                        if mandante:
                                            gols_mandante.append([tags_auxs[index],tempo_total,acrescimos])
                                        else:
                                            gols_visitante.append([tags_auxs[index],tempo_total,acrescimos])
                                    else:
                                        if mandante:
                                            if index != 5:
                                                cartoes_mandante.append([tags_auxs[index],tempo_total,acrescimos])
                                            else: 
                                                cartoes_mandante.append([tags_auxs[4],tempo_total,acrescimos])
                                        else:
                                            if index != 5:
                                                cartoes_visitante.append([tags_auxs[index],tempo_total,acrescimos])
                                            else: 
                                                cartoes_visitante.append([tags_auxs[4],tempo_total,acrescimos])
                        
                        dados_jogo['gols_mandante'] = gols_mandante
                        dados_jogo['gols_visitante'] = gols_visitante
                        dados_jogo['cartoes_mandante'] = cartoes_mandante
                        dados_jogo['cartoes_visitante'] = cartoes_visitante

                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        # Pegar estátisticas importantes
                        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Box.Flex.VhXzF.kGBmhP')))
                        estatisticas_divs = driver.find_elements(By.CLASS_NAME, 'Box.Flex.heNsMA.bnpRyo')
                        estatisticas_copia = estatisticas_interesse.copy()

                        for estatistica in estatisticas_divs:
                            driver.execute_script("arguments[0].scrollIntoView();", estatistica)
                            estatistica_valores = estatistica.find_elements(By.TAG_NAME, 'bdi')

                            valor_esquerda = estatistica_valores[0].text.strip()
                            estatistica_nome = estatistica_valores[1].text.strip()
                            valor_direita = estatistica_valores[2].text.strip()
                            
                            if estatistica_nome in estatisticas_copia:
                                estatisticas_copia.remove(estatistica_nome)

                                if estatistica_nome == "Finalizações":
                                    dados_jogo["finalizacoes_mandante"] = int(valor_esquerda)
                                    dados_jogo["finalizacoes_visitante"] = int(valor_direita)
                                elif estatistica_nome == "Faltas":
                                    dados_jogo["faltas_mandante"] = int(valor_esquerda)
                                    dados_jogo["faltas_visitante"] = int(valor_direita)
                                elif estatistica_nome == "Escanteios":
                                    dados_jogo["escanteios_mandante"] = int(valor_esquerda)
                                    dados_jogo["escanteios_visitante"] = int(valor_direita)
                                elif estatistica_nome == "Posse de bola":
                                    dados_jogo["posse_mandante"] = int(valor_esquerda.strip('%'))
                                    dados_jogo["posse_visitante"] = int(valor_direita.strip('%'))
                        
                        banco.salvar_jogo_no_banco(dados_jogo,database)
                    else:
                        print("Já está no banco")      
                except:
                    links_jogos_faltantes.append(link)
                    print("Erro ao buscar os dados")  
        
        if links_jogos_faltantes:
            with open(file_path, "w", encoding='utf-8') as file:
                for item in links_jogos_faltantes:
                    file.write(item)
        else:
            break 
    
    driver.quit()