import json
import re
import time
import os
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

driver.switch_to.frame(iframe)
driver.execute_script(
    "document.body.innerHTML = arguments[0];", texto_ata.replace('\n', '<br>')
)
driver.switch_to.default_content()
