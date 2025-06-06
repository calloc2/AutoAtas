import json
import re
import time
import os
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tkinter import Tk, filedialog
from dotenv import load_dotenv

load_dotenv()
USUARIO = os.getenv("IMPLANTA_USUARIO")
SENHA = os.getenv("IMPLANTA_SENHA")

if not USUARIO or not SENHA:
    print("Usuário ou senha não definidos no .env")
    exit()

Tk().withdraw()
ata_path = filedialog.askopenfilename(filetypes=[("Atas TXT", "*.txt")])
if not ata_path:
    print("Nenhum arquivo selecionado.")
    exit()

with open(ata_path, encoding="utf-8") as f:
    ata = json.load(f)

numero_ata = re.sub(r'\D', '', ata["numero"])

driver = webdriver.Chrome()
driver.get("https://crea-to.implanta.net.br/logon/sistema/login.aspx")
time.sleep(2)

input_usuario = driver.find_element(By.ID, "MainContent_txtUsuario")
input_usuario.clear()
input_usuario.send_keys(USUARIO)

input_senha = driver.find_element(By.ID, "MainContent_txtSenha")
input_senha.clear()
input_senha.send_keys(SENHA)

btn_login = driver.find_element(By.ID, "MainContent_btnLogin")
btn_login.click()
time.sleep(3)

driver.get("https://crea-to.implanta.net.br/portalTransparencia/admin/#Admin/AtasColegiados")
time.sleep(3)

btn_novo = driver.find_element(By.CLASS_NAME, "btnNovo")
btn_novo.click()
time.sleep(3)

input_numero = driver.find_element(By.ID, "Numero")
input_numero.clear()
input_numero.send_keys(numero_ata)

input_colegiado = driver.find_element(By.ID, "Colegiado")
input_colegiado.clear()
input_colegiado.send_keys("PLENÁRIO")

def iso_to_br(date_iso):
    try:
        y, m, d = date_iso.split('-')
        return f"{d.zfill(2)}/{m.zfill(2)}/{y}"
    except Exception:
        return ""

data_inicio = iso_to_br(ata["data_iso"])
data_termino = iso_to_br(ata["data_iso"])

input_data_inicio = driver.find_element(By.ID, "DataInicio")
input_data_inicio.clear()
input_data_inicio.send_keys(data_inicio)

input_data_termino = driver.find_element(By.ID, "DataTermino")
input_data_termino.clear()
input_data_termino.send_keys(data_termino)

tipo_ata = ata["tipo"].capitalize()

tipo_select = driver.find_element(By.XPATH, "//span[@id='select2-Tipo-container']")
tipo_select.click()
time.sleep(1)

opcao_tipo = driver.find_element(By.XPATH, f"//li[contains(@class, 'select2-results__option') and text()='{tipo_ata}']")
opcao_tipo.click()
time.sleep(1)

texto_ata = ata["texto_completo_ata"]

import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC

wait = ui.WebDriverWait(driver, 10)
iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.cke_wysiwyg_frame")))

driver.switch_to.default_content()
# Use o CKEditor para setar o valor corretamente
driver.execute_script("""
    if (window.CKEDITOR && CKEDITOR.instances && CKEDITOR.instances['Deliberacoes']) {
        CKEDITOR.instances['Deliberacoes'].setData(arguments[0]);
    } else {
        // fallback: tenta setar direto no iframe se não achar o CKEditor
        var iframe = document.querySelector('iframe.cke_wysiwyg_frame');
        if (iframe && iframe.contentDocument && iframe.contentDocument.body) {
            iframe.contentDocument.body.innerHTML = arguments[0];
        }
    }
""", texto_ata.replace('\n', '<br>'))
from selenium.webdriver.common.action_chains import ActionChains

def normalizar_nome(nome):
    return unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII').lower().strip()

for participante in ata["integrantes"]:
    try:
        wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#modalParticipante[style*='display: block']"))
        )
    except Exception:
        pass  # Se já estiver fechado, segue normalmente

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.2)

    btn_adicionar = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.adicionarGrid[data-bind*='ParticipantesViewModel.ParticipanteAdicionar']"))
    )
    try:
        btn_adicionar.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn_adicionar)
    time.sleep(1)

    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#modalParticipante[style*='display: block']"))
    )

    select2_participante = wait.until(
        EC.element_to_be_clickable((By.ID, "select2-IdPessoa-container"))
    )
    select2_participante.click()
    time.sleep(0.5)
    input_search = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field"))
    )
    input_search.clear()
    input_search.send_keys(participante)

    # Aguarda até que o nome do participante apareça ou "Nenhum resultado encontrado"
    timeout = time.time() + 10
    encontrado = False
    while time.time() < timeout:
        # Verifica se apareceu a mensagem de nenhum resultado
        nenhum_resultado = driver.find_elements(By.CSS_SELECTOR, "#select2-IdPessoa-results li.select2-results__message")
        if nenhum_resultado and "nenhum resultado encontrado" in nenhum_resultado[0].text.lower():
            print(f"Nenhum resultado encontrado para: {participante}")
            encontrado = False
            break
        resultados = driver.find_elements(By.CSS_SELECTOR, "#select2-IdPessoa-results li.select2-results__option .selectGrid_8")
        for r in resultados:
            if normalizar_nome(participante) in normalizar_nome(r.text):
                encontrado = True
                break
        if encontrado:
            break
        time.sleep(0.5)
    if not encontrado:
        print(f"Participante não encontrado na lista: {participante}")
        continue

    input_search.send_keys(Keys.ENTER)
    time.sleep(0.5)

    btn_confirmar = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btnVerde[data-bind*='ParticipantesViewModel.ParticipanteSalvar']"))
    )
    btn_confirmar.click()
    time.sleep(1)

# --- ANEXO PDF ---
pdf_path = ata_path.replace('.txt', '.pdf')
if os.path.exists(pdf_path):
    btn_add_anexo = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.adicionarGrid[data-bind*='AnexosViewModel.NovoAnexo']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", btn_add_anexo)
    time.sleep(0.3)
    try:
        btn_add_anexo.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn_add_anexo)
    time.sleep(1)

    # Preenche o campo "Nome" do anexo com o número da ata
    input_nome_anexo = wait.until(
        EC.visibility_of_element_located((By.ID, "Nome"))
    )
    input_nome_anexo.clear()
    input_nome_anexo.send_keys(numero_ata)
    time.sleep(0.3)

    file_input = driver.find_element(By.ID, "fileupload")
    file_input.send_keys(pdf_path)
    time.sleep(2)
    btn_enviar = driver.find_element(By.CSS_SELECTOR, ".infoArquivo button.btnAzul")
    btn_enviar.click()
    time.sleep(2)
    btn_confirmar_anexo = driver.find_element(By.CSS_SELECTOR, "button.btnVerde[data-bind*='AnexosViewModel.AnexoSalvar']")
    btn_confirmar_anexo.click()
    time.sleep(1)
else:
    print(f"Arquivo PDF não encontrado para anexar: {pdf_path}")

# --- FINALIZAR PROCESSO ---
try:
    # Aguarda o botão ficar visível e habilitado
    btn_salvar = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'containerBotoes')]//button[contains(@class,'btnVerde') and contains(text(),'Salvar')]"))
    )
    # Rola até o botão para garantir que não está fora da viewport
    driver.execute_script("arguments[0].scrollIntoView(true);", btn_salvar)
    time.sleep(0.3)
    try:
        btn_salvar.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn_salvar)
    print("Processo finalizado, aguardando confirmação visual...")

    # Aguarda a mensagem de sucesso aparecer
    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#smallbox2.SmallBox .textoFoto span"))
    )
    print("Registro salvo com sucesso!")
    time.sleep(1)  # Aguarda mais um pouco para garantir o fechamento da mensagem
except Exception as e:
    print("Não foi possível clicar no botão Salvar para finalizar o processo.", e)
