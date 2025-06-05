# AutoAtas

Automação para extração de dados de atas do CREA-TO em arquivos PDF, gerando arquivos `.txt` no formato JSON prontos para uso em integrações e automações.

## Descrição

Este projeto automatiza o processo de coleta e extração de dados de atas do CREA-TO, reduzindo erros manuais e otimizando o tempo de trabalho. Os dados extraídos podem ser utilizados em sistemas como o Implanta ou em automações com Selenium.

## Requisitos

- Python 3.8+
- pip

## Instalação

1. Clone este repositório:
    ```sh
    git clone https://github.com/seu-usuario/AutoAtas.git
    cd AutoAtas
    ```

2. Crie um ambiente virtual (opcional, mas recomendado):
    ```sh
    python -m venv venv
    ```

3. Ative o ambiente virtual:

    - **Windows:**
      ```sh
      venv\Scripts\activate
      ```
    - **Linux/Mac:**
      ```sh
      source venv/bin/activate
      ```

4. Instale as dependências:
    ```sh
    pip install -r requirements.txt
    ```
    > Se não existir um arquivo `requirements.txt`, instale manualmente:
    ```sh
    pip install pdfplumber streamlit
    ```

## Como usar

### Linha de comando

Para processar um ou mais PDFs e gerar arquivos `.txt` com o mesmo nome:

```sh
python main.py ata363.pdf ata364.pdf
```

Os arquivos `ata363.txt`, `ata364.txt`, etc. serão gerados na mesma pasta.

### Interface Web

Para usar a interface web:

1. Execute:
    ```sh
    streamlit run web_interface.py
    ```
2. Abra o navegador no endereço exibido (geralmente http://localhost:8501).
3. Faça upload de um ou mais arquivos PDF e acompanhe os logs coloridos.

## Estrutura dos arquivos gerados

Cada arquivo `.txt` gerado contém um JSON com os campos extraídos da ata, por exemplo:

```json
{
    "numero": "364ª",
    "tipo": "Ordinária",
    "data": "01 DE NOVEMBRO DE 2024",
    "data_iso": "2024-11-01",
    "inicio": "...",
    "fim": "...",
    "texto_completo_ata": "...",
    "integrantes": [
        "Eng. Civ. Daniel Iglesias de Carvalho",
        "Eng. Civ. Fabiano Fagundes"
    ]
}
```

## Observações

- Os arquivos `.pdf` e `.txt` estão listados no `.gitignore` e não são versionados.
- O script filtra cabeçalhos, rodapés e números de ordem das atas automaticamente.

---

Desenvolvido por **Yuri Barbosa Takahashi** e **Gabriel Oliveira Aires**.
