import pdfplumber
import re

def extrair_dados_ata(path_pdf):
    with pdfplumber.open(path_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"

    texto_completo = re.sub(r'\s{2,}', ' ', texto_completo)  # limpa espaços extras

    # Título da ata
    match_titulo = re.search(r'ATA DA\s+\d+ª.*?REALIZADA EM [\w\s]+ DE \d{4}', texto_completo, re.IGNORECASE)
    titulo_ata = match_titulo.group(0) if match_titulo else "Título não encontrado"

    # Início da ata (linha 1) - captura só a primeira linha após o número 1
    match_inicio = re.search(
        r'1\s+([ÀA][^\n\.]+?[\.\n])', texto_completo
    )
    inicio_ata = match_inicio.group(1).strip() if match_inicio else "Início não encontrado"

    # Fim da ata (aceita qualquer número romano no item de encerramento)
    match_fim = re.search(
        r'ITEM [IVXLCDM]+\s*–\s*Encerramento:.*?finalizando a sessão plenária às .*?minutos[.\-–]+',
        texto_completo,
        re.DOTALL | re.IGNORECASE
    )
    fim_ata = match_fim.group(0) if match_fim else "Encerramento não encontrado"

    # Texto da ata (completo)
    if match_inicio and match_fim:
        inicio_index = texto_completo.find(match_inicio.group(0))
        fim_index = texto_completo.find(match_fim.group(0)) + len(match_fim.group(0))
        corpo_ata = texto_completo[inicio_index:fim_index]
    else:
        corpo_ata = "Corpo da ata não encontrado"

    # Lista de integrantes (tudo após o encerramento)
    lista_integrantes = ""
    if match_fim and match_inicio:
        integrantes_texto = texto_completo[fim_index:]
        # Tentativa de extrair blocos com nomes + cargos
        integrantes_linhas = re.findall(r'Eng\..+?(?:\n|$)', integrantes_texto)
        lista_integrantes = "\n".join(linha.strip() for linha in integrantes_linhas if "Serviço Público Federal" not in linha)
    else:
        lista_integrantes = "Integrantes não encontrados"

    return {
        "titulo": titulo_ata,
        "inicio": inicio_ata,
        "fim": fim_ata,
        "texto_completo_ata": corpo_ata,
        "integrantes": lista_integrantes.strip()
    }

# Exemplo de uso
dados = extrair_dados_ata("document.pdf")

# Saída
print("📝 Título:", dados["titulo"])
print("⏱ Início:", dados["inicio"])
print("✅ Fim:", dados["fim"])
print("\n📜 Texto da Ata:\n", dados["texto_completo_ata"][:1000], "...")
print("\n👥 Integrantes:\n", dados["integrantes"])
