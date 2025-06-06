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
