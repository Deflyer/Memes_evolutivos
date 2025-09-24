import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException

def coletar_urls_pinterest(driver, termo_busca, total_desejado):
    """
    Coleta URLs de imagens do Pinterest para um termo de busca, rolando a página.
    """
    url_busca = f'https://br.pinterest.com/search/pins/?q={termo_busca.replace(" ", "%20")}'
    driver.get(url_busca)
    
    print(f"Iniciando a coleta de até {total_desejado} imagens para '{termo_busca}'...")
    
    urls_coletadas = set()
    
    while len(urls_coletadas) < total_desejado:
        try:
            # Encontra todas as tags <img> com a classe específica para imagens de pin
            elementos_imagens = driver.find_elements(By.CLASS_NAME, 'hCL')
            
            for img in elementos_imagens:
                srcset = img.get_attribute('srcset')
                if srcset:
                    # O srcset contém vários URLs. Vamos pegar o de maior resolução.
                    # Geralmente é o que tem 'originals' ou a maior largura.
                    urls_list = [url.strip() for url in srcset.split(',')]
                    
                    # Encontra a URL com a maior resolução
                    url_encontrada = ''
                    for url_with_size in urls_list:
                        # Extrai a URL
                        url = url_with_size.split(' ')[0]
                        if 'originals' in url:
                            url_encontrada = url
                            break # Encontramos a melhor qualidade, podemos parar de procurar
                        elif '736x' in url:
                             url_encontrada = url # Prioriza 736x se 'originals' não for encontrado
                        
                    if url_encontrada:
                        urls_coletadas.add(url_encontrada)

        except StaleElementReferenceException:
            print("Elemento obsoleto, tentando novamente...")
            continue
            
        print(f"URLs encontradas: {len(urls_coletadas)} de {total_desejado}")
        
        if len(urls_coletadas) >= total_desejado:
            break
            
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) 

    print(f"Coleta finalizada. Total de URLs únicas encontradas: {len(urls_coletadas)}")
    return list(urls_coletadas)

def baixar_imagem_da_url(url_imagem, caminho_destino, nome_arquivo):
    """
    Baixa uma imagem de uma URL usando a biblioteca requests.
    """
    try:
        response = requests.get(url_imagem, stream=True, timeout=10)
        if response.status_code == 200:
            caminho_completo = os.path.join(caminho_destino, nome_arquivo)
            with open(caminho_completo, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Imagem salva: {nome_arquivo}")
        else:
            print(f"Falha ao baixar {url_imagem}. Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao baixar a imagem {url_imagem}: {e}")

# --- Exemplo de uso ---
if __name__ == "__main__":
    TERMO_BUSCA = "figurinha"
    TOTAL_IMAGENS_DESEJADO = 100

    CAMINHO_DESTINO = os.path.join(os.getcwd(), "imagens_pinterest")
    
    if not os.path.exists(CAMINHO_DESTINO):
        os.makedirs(CAMINHO_DESTINO)

    opcoes_chrome = Options()
    servico = Service()
    driver = webdriver.Chrome(service=servico, options=opcoes_chrome)

    try:
        lista_de_urls = coletar_urls_pinterest(driver, TERMO_BUSCA, TOTAL_IMAGENS_DESEJADO)
        
        print(f"\nIniciando o download de {len(lista_de_urls)} imagens.")
        for i, url in enumerate(lista_de_urls):
            # Obtém a extensão do arquivo da URL (ex: .jpg, .png)
            extensao = os.path.splitext(url)[1].split('?')[0]
            nome_arquivo = f"{TERMO_BUSCA.replace(' ', '_')}_{i+1}{extensao}"
            baixar_imagem_da_url(url, CAMINHO_DESTINO, nome_arquivo)
            time.sleep(1) # Pausa para não sobrecarregar o servidor
            
        print("\nTodos os downloads foram processados. Verifique a pasta de destino.")
            
    finally:
        driver.quit()