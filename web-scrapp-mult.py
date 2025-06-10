import os
import re
import platform
import time
import pdfplumber
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === DETECTA O SISTEMA E DEFINE DIRETÓRIO DE DOWNLOAD ===
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

def esperar_download_concluir(pasta, timeout=60):
    start_time = time.time()
    while True:
        cr_files = [f for f in os.listdir(pasta) if f.endswith(".crdownload")]
        if not cr_files:
            break
        if time.time() - start_time > timeout:
            raise TimeoutError("⏰ Tempo limite ao esperar o download.")
        time.sleep(1)

# === ETAPA 1: BAIXAR TODOS OS PDFs ===
driver = webdriver.Chrome(service=Service(), options=chrome_options)
url = "https://crea-to.implanta.net.br/portaltransparencia/#publico/Listas?id=46daa17b-3013-4e95-90c3-f8733d27ed27"
driver.get(url)
time.sleep(10)

for pagina in range(7, 13):
    try:
        print(f"\n📄 Acessando página {pagina}...")
        aba = driver.find_element(By.XPATH, f"//a[@alt='Pagina {pagina}' and text()='{pagina}']")
        try:
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI"))
            )
        except:
            print("⚠️ Overlay ainda visível antes de clicar na página.")
        aba.click()
        time.sleep(5)
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'AjaxDownloadFile')]")
        print(f"🔗 Encontrados {len(links)} arquivos")
        for link in links:
            try:
                print(f"⬇️ Baixando: {link.text.strip()}...")
                try:
                    WebDriverWait(driver, 30).until(
                        EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI"))
                    )
                except:
                    print("⚠️ Overlay não desapareceu. Forçando clique...")
                driver.execute_script("arguments[0].click();", link)
                esperar_download_concluir(download_base)
                time.sleep(1)
            except Exception as e:
                print(f"❌ Erro ao baixar: {e}")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Erro ao acessar a página {pagina}: {e}")

driver.quit()
print("\n✅ Todos os downloads finalizados. Iniciando renomeação...")

# === ETAPA 2: RENOMEAR PDFs ===

def limpar_nome(texto):
    texto = re.sub(r'[\\/:*?"<>|]', '_', texto)  # Remove caracteres inválidos
    texto = re.sub(r'\s+', ' ', texto).strip()   # Espaços duplos
    return texto

def extrair_nome_pdf(caminho_pdf):
    # Cabeçalhos a ignorar (case insensitive, com ou sem acento)
    cabecalhos = [
        r"servi[cç]o p[úu]blico federal",
        r"conselho regional de engenharia e agronomia do tocantins",
        r"crea-to"
    ]
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto = pdf.pages[0].extract_text()
            if not texto:
                return None
            linhas = [l.strip() for l in texto.splitlines() if l.strip()]
            # Remove linhas de cabeçalho
            linhas_filtradas = []
            for linha in linhas:
                if not any(re.search(cab, linha, re.IGNORECASE) for cab in cabecalhos):
                    linhas_filtradas.append(linha)
            # Procura padrão "ATA DA 344ª ...", ignorando o texto entre parênteses
            for linha in linhas_filtradas:
                m = re.match(r"(ATA DA\s+(\d+)[ªa]?)(?:\s*\(.*?\))?(.*)", linha, re.IGNORECASE)
                if m:
                    numero = m.group(2)
                    resto = m.group(3).strip()
                    nome = f"ATA DA {numero}{' ' + resto if resto else ''}"
                    return limpar_nome(nome)
            # Se não encontrar, retorna a primeira linha útil
            if linhas_filtradas:
                return limpar_nome(linhas_filtradas[0])
    except Exception as e:
        print(f"⚠️ Erro ao extrair nome do PDF: {e}")
    return None

for arquivo in os.listdir(download_base):
    if arquivo.lower().endswith(".pdf"):
        caminho = os.path.join(download_base, arquivo)
        nome_extraido = extrair_nome_pdf(caminho)
        if nome_extraido:
            novo_nome = nome_extraido + ".pdf"
            novo_caminho = os.path.join(download_base, novo_nome)
            if not os.path.exists(novo_caminho):
                os.rename(caminho, novo_caminho)
                print(f"✔️ Renomeado: {novo_nome}")
            else:
                print(f"⚠️ Arquivo já existe: {novo_nome}")
        else:
            print(f"❌ Não foi possível extrair nome de: {arquivo}")

print("\n✅ Renomeação finalizada!")
