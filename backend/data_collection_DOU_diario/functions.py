import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
from tqdm import tqdm  

# Função para capturar o link do banco de dados do DOU
def link_jornal_diario(dia, mes, ano):
    url_bd_dou = "https://www.in.gov.br/leiturajornal?data="
    meses = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    data_input = datetime(ano, mes, dia)
    data_atual = datetime.now()

    if data_input > data_atual:
        return "Data informada é posterior à data atual."
    else:
        dia_str = str(dia).zfill(2)
        mes_str = meses[mes - 1]
        url_consulta = f"{url_bd_dou}{dia_str}-{mes_str}-{ano}&secao=do3"
        response = requests.get(url_consulta)

        # Verifica se a requisição foi bem sucedida
        if response.status_code == 200:
            return url_consulta
        else:
            return f"Falha ao acessar a página. Status code: {response.status_code}"

def extrair_url_titles(url):
    # Obter o HTML da página
    response = requests.get(url)
    response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the script tag with the JSON data
    script_tag = soup.find('script', id='params', type='application/json')

    if not script_tag:
        print("Tag <script> com id 'params' não encontrada.")
        return []

    # Load the JSON data
    data = json.loads(script_tag.string)

    # Extract the urlTitle values and prepend the base URL
    base_url = "http://www.in.gov.br/web/dou/-/"
    url_titles = [base_url + item['urlTitle'] for item in data.get('jsonArray', [])]

    return url_titles

def extraindo_avisos_licitacao(lista_de_urls):
    links_avisos_licitacao = []
    termos = ["aviso-de-licitacao", "aviso-de-licitação"]

    for url in lista_de_urls:
        if any(term in url for term in termos):
            links_avisos_licitacao.append(url)

    return links_avisos_licitacao

def extrair_info_aviso(url):
    # Obter o HTML da página
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extrair informações principais
    tipo_elem = soup.find('p', class_='identifica')
    if tipo_elem:
        tipo = tipo_elem.text.strip()
    else:
        tipo = "N/A"

    identifica_elems = soup.find_all('p', class_='identifica')
    if len(identifica_elems) > 1:
        subtitulo = identifica_elems[1].text.strip()
    else:
        subtitulo = "N/A"

    descricao_elem = soup.find('p', class_='dou-paragraph')
    if descricao_elem:
        descricao = descricao_elem.text.strip()
    else:
        descricao = "N/A"

    assinante_elem = soup.find('p', class_='assina')
    if assinante_elem:
        assinante = assinante_elem.text.strip()
    else:
        assinante = "N/A"

    cargo_elem = soup.find('p', class_='cargo')
    if cargo_elem:
        cargo = cargo_elem.text.strip()
    else:
        cargo = "N/A"

    # Extrair informações adicionais
    detalhes_dou = soup.find('div', class_='detalhes-dou')
    if detalhes_dou:
        data_publicacao = detalhes_dou.find('span', class_='publicado-dou-data').text.strip() if detalhes_dou.find('span', class_='publicado-dou-data') else "N/A"
        edicao = detalhes_dou.find('span', class_='edicao-dou-data').text.strip() if detalhes_dou.find('span', class_='edicao-dou-data') else "N/A"
        secao_pagina = detalhes_dou.find('span', class_='secao-dou').text.strip() if detalhes_dou.find('span', class_='secao-dou') else "N/A"
        orgao = detalhes_dou.find('span', class_='orgao-dou-data').text.strip() if detalhes_dou.find('span', class_='orgao-dou-data') else "N/A"
    else:
        data_publicacao = "N/A"
        edicao = "N/A"
        secao_pagina = "N/A"
        orgao = "N/A"

    # Construir o dicionário com as informações
    aviso_info = {
        "tipo": tipo,
        "subtitulo": subtitulo,
        "descricao": descricao,
        "assinante": assinante,
        "cargo": cargo,
        "data_publicacao": data_publicacao,
        "edicao": edicao,
        "secao/pagina": secao_pagina,
        "orgao": orgao,
        "link": url
    }

    return aviso_info

def filtrando_os_avisos_de_brasilia(aviso_info):
    # Palavras específicas que estamos procurando
    palavras_especificas = ["Brasilia", "Brasília", " DF "]
    counter = 0
    # Verificar se alguma das palavras específicas está na descrição
    descricao = aviso_info.get('descricao', '').lower()  # Usar .lower() para fazer a verificação case-insensitive
    if any(palavra.lower() in descricao for palavra in palavras_especificas):
        # Verifica se as palavras "horarios" ou "horário" estão próximas das palavras-chave
        for palavra_chave in palavras_especificas:
            if palavra_chave.lower() in descricao:
                indice_palavra_chave = descricao.index(palavra_chave.lower())
                trecho_analisado = descricao[max(0, indice_palavra_chave - 30):indice_palavra_chave + len(palavra_chave) + 30]
                if "horarios" not in trecho_analisado and "horário" not in trecho_analisado:
                    counter += 1
                    print(counter)
                    return aviso_info  # Se encontrar, retorna o aviso_info

    return None  # Se nenhuma palavra específica estiver presente ou se encontrar "horarios"/"horário" nas proximidades


def criandojsoncomavisos(links_avisos, dia, mes, ano):
    avisos_detalhados = []
    maxil = len(links_avisos)
    cont = 1
    for link in links_avisos:
        info_aviso = filtrando_os_avisos_de_brasilia(extrair_info_aviso(link))
        if info_aviso:  # Verifica se o dicionário não está vazio
            avisos_detalhados.append(info_aviso)
            print("Processando licitação " + str(cont) + " de " + str(maxil))
            cont += 1



    # Converter a lista de dicionários em JSON e salvar em um arquivo
    data_str = f"{ano}-{str(mes).zfill(2)}-{str(dia).zfill(2)}"
    output_file = f"{data_str}_avisos_licitacao.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(avisos_detalhados, f, ensure_ascii=False, indent=4)

    return avisos_detalhados


links_dos_avisos = extraindo_avisos_licitacao(extrair_url_titles(link_jornal_diario(31,8,2023)))
criandojsoncomavisos(links_dos_avisos,31,8,2023)