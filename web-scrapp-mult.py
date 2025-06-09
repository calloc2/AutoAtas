import os
import platform
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === DETECTA O SISTEMA E DEFINE DIRETÓRIO ===
sistema = platform.system()

if sistema == "Windows":
    download_base = os.path.join(os.environ["USERPROFILE"], "Downloads", "atas_crea")
else:
    download_base = os.path.join(os.path.expanduser("~"), "Downloads", "atas_crea")

os.makedirs(download_base, exist_ok=True)
print(f"📁 Diretório de download: {download_base}")

# === CONFIGURAÇÕES DO CHROME ===
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_base,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})

# === FUNÇÕES AUXILIARES ===

def esperar_download_concluir(pasta, timeout=60):
    """Aguarda até que não haja mais arquivos .crdownload"""
    start_time = time.time()
    while True:
        cr_files = [f for f in os.listdir(pasta) if f.endswith(".crdownload")]
        if not cr_files:
            break
        if time.time() - start_time > timeout:
            raise TimeoutError("Tempo limite ao esperar o download.")
        time.sleep(1)

def obter_pdf_recente(pasta, t_antes):
    """Retorna o arquivo PDF mais recente criado após o tempo t_antes"""
    arquivos = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith(".pdf")]
    arquivos_novos = [f for f in arquivos if os.path.getctime(f) >= t_antes]
    if not arquivos_novos:
        return None
    return max(arquivos_novos, key=os.path.getctime)

# === INICIA O NAVEGADOR ===
driver = webdriver.Chrome(service=Service(), options=chrome_options)

url = "https://crea-to.implanta.net.br/portaltransparencia/#publico/Listas?id=46daa17b-3013-4e95-90c3-f8733d27ed27"
driver.get(url)
time.sleep(10)

# === LOOP DE PÁGINAS DE 7 A 12 ===
for pagina in range(7, 13):
    try:
        print(f"\n📄 Acessando página {pagina}...")
        aba = driver.find_element(By.XPATH, f"//a[@alt='Pagina {pagina}' and text()='{pagina}']")
        aba.click()
        time.sleep(5)

        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'AjaxDownloadFile')]")
        print(f"🔗 Encontrados {len(links)} arquivos")

        for link in links:
            try:
                nome_arquivo = link.text.strip().replace("/", "_").replace("\\", "_")
                print(f"⬇️ Baixando: {nome_arquivo}...")

                tempo_antes = time.time()
                link.click()

                esperar_download_concluir(download_base)
                time.sleep(1)  # Garante que o sistema finalize a escrita

                arquivo_baixado = obter_pdf_recente(download_base, tempo_antes)

                if arquivo_baixado:
                    novo_caminho = os.path.join(download_base, nome_arquivo + ".pdf")
                    os.rename(arquivo_baixado, novo_caminho)
                    print(f"✔️ Renomeado: {nome_arquivo}.pdf")
                else:
                    print("❌ Nenhum PDF detectado após clique.")

                time.sleep(2)

            except Exception as e:
                print(f"❌ Erro ao baixar/renomear: {e}")

    except Exception as e:
        print(f"⚠️ Erro ao acessar a página {pagina}: {e}")

driver.quit()
print("\n✅ Finalizado com sucesso!")
