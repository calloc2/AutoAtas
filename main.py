import pdfplumber
import re
import json
import os
import sys

def extrair_dados_ata(path_pdf, presidente_nome):
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

    # Busca padrão principal: trecho entre "Encerramento:" e "minutos"
    match_fim = re.search(
        r'Encerramento:(.*?minutos?[.\-–]+)',
        texto_completo,
        re.DOTALL | re.IGNORECASE
    )
    # Fallback: busca só o trecho "finalizando a sessão plenária ... minutos"
    if not match_fim:
        match_fim = re.search(
            r'finalizando a sessão plenária.*?minutos?[.\-–]+',
            texto_completo,
            re.DOTALL | re.IGNORECASE
        )
    # Fallback: busca o último "minutos" seguido de ponto/traço
    if not match_fim:
        match_fim = re.search(
            r'([^.]{0,200}minutos?[.\-–]+)', texto_completo[::-1], re.DOTALL | re.IGNORECASE
        )
        fim_ata = match_fim.group(1)[::-1].strip() if match_fim else "Encerramento não encontrado"
    else:
        fim_ata = match_fim.group(1).strip() if match_fim.lastindex else match_fim.group(0).strip()

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

    # Integrantes: apenas nomes, sem prefixos
    lista_integrantes = []
    if match_fim and match_inicio:
        integrantes_texto = texto_completo[fim_index:]
        matches = re.findall(r'Eng\.(?:\s*\w+\.)*\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^E\n]+)', integrantes_texto)
        pulou_primeira_linha = False
        for idx, nome in enumerate(matches):
            nome = nome.strip()
            nome = re.sub(r'\s{2,}', ' ', nome)
            nome = nome.strip('. ')
            nome = nome.replace('.', '')
            # Pula a primeira linha (presidente + secretaria)
            if not pulou_primeira_linha:
                pulou_primeira_linha = True
                continue
            if nome and nome not in lista_integrantes:
                lista_integrantes.append(nome)
        # Adiciona o presidente manualmente como primeiro integrante
        lista_integrantes.insert(0, presidente_nome)
    else:
        lista_integrantes = []

    return {
        "numero": numero_ata,
        "presidente": presidente_nome,
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

def processar_atas(pdf_paths):
    for pdf_path in pdf_paths:
        if not pdf_path.lower().endswith('.pdf'):
            print(f"Arquivo ignorado (não é PDF): {pdf_path}")
            continue
        if not os.path.exists(pdf_path):
            print(f"Arquivo não encontrado: {pdf_path}")
            continue
        dados = extrair_dados_ata(pdf_path)
        txt_path = os.path.splitext(pdf_path)[0] + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"Processado: {pdf_path} -> {txt_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py arquivo1.pdf [arquivo2.pdf ...]")
    else:
        processar_atas(sys.argv[1:])
