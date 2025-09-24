import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

def coletar_urls_com_scroll(driver, url_pagina_lista, total_desejado):
    """
    Coleta as URLs de sons em uma página de listagem, rolando para carregar mais conteúdo.
    """
    driver.get(url_pagina_lista)
    print(f"Iniciando a coleta de até {total_desejado} URLs...")
    
    urls_coletadas = set()
    scroll_count = 0
    
    while len(urls_coletadas) < total_desejado:
        try:
            elementos_links = driver.find_elements(By.CLASS_NAME, "instant-link")
            for elemento in elementos_links:
                href = elemento.get_attribute("href")
                if href:
                    urls_coletadas.add(href)
        except StaleElementReferenceException:
            print("Elemento obsoleto, tentando novamente...")
            continue
        
        print(f"URLs encontradas: {len(urls_coletadas)} de {total_desejado}")
        
        if len(urls_coletadas) >= total_desejado:
            break
            
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) 
        
        scroll_count += 1
        if scroll_count > 50 and len(urls_coletadas) < 100:
             print("Aviso: Rolagem excessiva sem encontrar novos elementos. Finalizando.")
             break

    print(f"Coleta finalizada. Total de URLs únicas encontradas: {len(urls_coletadas)}")
    return list(urls_coletadas)

def baixar_som_myinstants(driver, url_som):
    """
    Baixa um som de uma URL específica do Myinstants usando um driver já inicializado.
    """
    print(f"\n--- Processando URL: {url_som} ---")
    try:
        driver.get(url_som)
        
        # O novo XPath busca por qualquer elemento que contenha o texto 'Baixar MP3'
        xpath_botao_download = "//*[contains(text(), 'Baixar MP3')]"
        
        # Usa WebDriverWait para esperar o botão de download carregar
        print("Aguardando o botão 'Baixar MP3'...")
        wait = WebDriverWait(driver, 10)
        botao_download = wait.until(
            EC.presence_of_element_located((By.XPATH, xpath_botao_download))
        )
        
        # Clica no botão de download
        botao_download.click()
        
        # Uma pequena espera para o download iniciar
        time.sleep(3)
        
        print("Download iniciado! Aguardando o próximo...")
        
    except (TimeoutException, Exception) as e:
        print(f"Ocorreu um erro ao processar {url_som}: {e}")

# --- Exemplo de uso ---
if __name__ == "__main__":
    URL_PAGINA_INICIAL = "https://www.myinstants.com/pt/index/br/"
    TOTAL_SONS_DESEJADO = 500

    CAMINHO_DESTINO = os.path.join(os.getcwd(), "downloads_myinstants")
    
    if not os.path.exists(CAMINHO_DESTINO):
        os.makedirs(CAMINHO_DESTINO)

    opcoes_chrome = Options()
    opcoes_chrome.add_experimental_option(
        "prefs", {
            "download.default_directory": CAMINHO_DESTINO,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    
    servico = Service()
    driver = webdriver.Chrome(service=servico, options=opcoes_chrome)

    try:
        lista_de_urls = coletar_urls_com_scroll(driver, URL_PAGINA_INICIAL, TOTAL_SONS_DESEJADO)
        
        print(f"\nIniciando o download de até {TOTAL_SONS_DESEJADO} sons.")
        print(lista_de_urls)
        for i, url in enumerate(lista_de_urls):
            if i >= TOTAL_SONS_DESEJADO:
                break
            baixar_som_myinstants(driver, url)
            
        print("\nTodos os downloads foram processados. Verifique a pasta de destino.")
            
    finally:
        driver.quit()