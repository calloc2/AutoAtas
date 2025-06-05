import pdfplumber
import re
import json
import os

def extrair_dados_ata(path_pdf):
    with pdfplumber.open(path_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"

    texto_completo = re.sub(r'\s{2,}', ' ', texto_completo)

    match_numero = re.search(r'ATA DA\s+(\d+ª)', texto_completo, re.IGNORECASE)
    numero_ata = match_numero.group(1) if match_numero else "Número não encontrado"

    match_tipo = re.search(r'SESSÃO PLENÁRIA\s+(ORDINÁRIA|EXTRAORDINÁRIA)', texto_completo, re.IGNORECASE)
    tipo_ata = match_tipo.group(1).capitalize() if match_tipo else "Tipo não encontrado"

    match_data = re.search(r'REALIZADA EM\s+([\w\sÀ-ú]+DE\s+\d{4})', texto_completo, re.IGNORECASE)
    if match_data:
        data_ata = match_data.group(1).replace('\n', ' ').strip()
        data_ata_iso = parse_data_ptbr(data_ata)
    else:
        data_ata = "Data não encontrada"
        data_ata_iso = "Data não encontrada"

    match_inicio = re.search(
        r'1\s+([ÀA][^\n\.]+?[\.\n])', texto_completo
    )
    inicio_ata = match_inicio.group(1).strip() if match_inicio else "Início não encontrado"

    match_fim = re.search(
        r'ITEM [IVXLCDM]+\s*–\s*Encerramento:.*?finalizando a sessão plenária às .*?minutos[.\-–]+',
        texto_completo,
        re.DOTALL | re.IGNORECASE
    )
    fim_ata = match_fim.group(0) if match_fim else "Encerramento não encontrado"

    if match_inicio and match_fim:
        inicio_index = texto_completo.find(match_inicio.group(0))
        fim_index = texto_completo.find(match_fim.group(0)) + len(match_fim.group(0))
        corpo_ata = texto_completo[inicio_index:fim_index]
        corpo_ata = re.sub(
            r'(Serviço Público Federal\s*Conselho Regional de Engenharia e Agronomia do Tocantins\s*CREA-TO\s*)|'
            r'(Quadra 106 norte Alameda 17, Lote 10, 77006-070 Palmas – TO\s*www\.crea-to\.org\.br \| Fone: \(63\) 3219-9800\s*)',
            '', corpo_ata, flags=re.IGNORECASE
        )
        corpo_ata = re.sub(r'(?:^|\n)\d{1,3}(?=\s)', '', corpo_ata)
        corpo_ata = re.sub(r'^1\s+', '', corpo_ata)
        corpo_ata = corpo_ata.replace('\n', ' ')
        corpo_ata = corpo_ata.strip()
    else:
        corpo_ata = "Corpo da ata não encontrado"

    lista_integrantes = []
    if match_fim and match_inicio:
        integrantes_texto = texto_completo[fim_index:]
        integrantes_linhas = re.findall(r'Eng\..+?(?:\n|$)', integrantes_texto)
        lista_integrantes = [
            linha.strip()
            for linha in integrantes_linhas
            if "Serviço Público Federal" not in linha and linha.strip()
        ]
    else:
        lista_integrantes = []

    return {
        "numero": numero_ata,
        "tipo": tipo_ata,
        "data": data_ata,
        "data_iso": data_ata_iso,
        "inicio": inicio_ata,
        "fim": fim_ata,
        "texto_completo_ata": corpo_ata,
        "integrantes": lista_integrantes
    }

def parse_data_ptbr(data_str):
    meses = {
        "JANEIRO": "01", "FEVEREIRO": "02", "MARÇO": "03", "ABRIL": "04",
        "MAIO": "05", "JUNHO": "06", "JULHO": "07", "AGOSTO": "08",
        "SETEMBRO": "09", "OUTUBRO": "10", "NOVEMBRO": "11", "DEZEMBRO": "12"
    }
    match = re.search(r'(\d{1,2}) DE (\w+) DE (\d{4})', data_str.upper())
    if match:
        dia, mes_pt, ano = match.groups()
        mes = meses.get(mes_pt, "01")
        return f"{ano}-{mes}-{int(dia):02d}"
    return "Data inválida"

pdf_path = "document.pdf"
dados = extrair_dados_ata(pdf_path)

txt_path = os.path.splitext(pdf_path)[0] + ".txt"
with open(txt_path, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)

print("Número da Ata:", dados["numero"])
print("Tipo:", dados["tipo"])
print("Data:", dados["data"])
print("Data (ISO):", dados["data_iso"])
print("⏱ Início:", dados["inicio"])
print("✅ Fim:", dados["fim"])
print("\n📜 Texto da Ata:\n", dados["texto_completo_ata"][:1000], "...")
print("\n👥 Integrantes:\n", dados["integrantes"])
print(f"\nArquivo JSON salvo em: {txt_path}")
