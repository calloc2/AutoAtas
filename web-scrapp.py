from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

# Diretório de download
download_dir = os.path.expanduser("~/Downloads/atas_crea")
os.makedirs(download_dir, exist_ok=True)

# Configuração do Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})

# Inicializa o navegador
driver = webdriver.Chrome(service=Service(), options=chrome_options)

# Acessa a página inicial
url = "https://crea-to.implanta.net.br/portaltransparencia/#publico/Listas?id=46daa17b-3013-4e95-90c3-f8733d27ed27"
driver.get(url)
time.sleep(10)

# Função auxiliar: espera download concluir
def esperar_download_concluir(pasta):
    while True:
        cr_files = [f for f in os.listdir(pasta) if f.endswith(".crdownload")]
        if not cr_files:
            break
        time.sleep(1)

# Função auxiliar: pega último PDF baixado
def obter_arquivo_mais_recente(pasta):
    arquivos = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith(".pdf")]
    if not arquivos:
        return None
    return max(arquivos, key=os.path.getmtime)

# Laço da página 7 até a 12
for pagina in range(7, 13):
    try:
        print(f"\n📄 Acessando página {pagina}...")

        # Clica na aba da página
        aba = driver.find_element(By.XPATH, f"//a[@alt='Pagina {pagina}' and text()='{pagina}']")
        aba.click()
        time.sleep(5)

        # Coleta links de download
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'AjaxDownloadFile')]")
        print(f"🔗 Encontrados {len(links)} arquivos na página {pagina}")

        for link in links:
            try:
                nome_arquivo = link.text.strip().replace("/", "_")  # Evita erro com caracteres
                print(f"⬇️ Baixando: {nome_arquivo}...")

                link.click()
                esperar_download_concluir(download_dir)

                arquivo_original = obter_arquivo_mais_recente(download_dir)

                if arquivo_original:
                    novo_nome = os.path.join(download_dir, nome_arquivo + ".pdf")
                    os.rename(arquivo_original, novo_nome)
                    print(f"✔️ Renomeado para: {nome_arquivo}.pdf")
                else:
                    print("❌ PDF não encontrado para renomear.")

                time.sleep(2)

            except Exception as e:
                print(f"❌ Erro ao baixar arquivo: {e}")
        
    except Exception as e:
        print(f"⚠️ Erro ao acessar a página {pagina}: {e}")
        continue

driver.quit()
print("\n✅ Finalizado com sucesso!")
