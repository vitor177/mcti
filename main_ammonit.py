import json
import requests
from datetime import datetime, timedelta    
import csv
from io import StringIO
from ammonit_relatorio import processa_tudo, processa_tudo_ausente
import sys
import os

estacoes_chave_valor = {"GWFR": "f7c9d9394c73b9bd3d020eb485d5387de6b4d31b",
                        "MFXD": "8d96c5fbfc6f1d61141f7c9743d157e4f836fbf7",
                        "DDCV": "2af5f00785a4df006f4b5a93c6dca699a546f5ba", 
                        "DHMJ": "cb9be99f7ed3767d132c34b1c1e0a484564bc5be", 
                        "KHVF": "1a8dbdc10d927c4cd1a367114a3ebcc29d5381ee",
                        "VHKM": "ce3c7608b5c3806db6fb48303b7a9128ac4fd6d1"}

def extrair_data(nome_arquivo):
  componentes = nome_arquivo.split('_')

  # Verificar se a lista tem pelo menos 3 elementos (nome, data, extensão)
  if len(componentes) < 3:
    return None

  # Extrair a data do meio e formatar
  data_str = componentes[1]
  data = f"{data_str[6:8]}-{data_str[4:6]}-{data_str[:4]}"
  return data

def converter_data(data_str):
    # Verifica se a string tem o comprimento correto
    if len(data_str) != 8 or not data_str.isdigit():
        raise ValueError("A string deve ter exatamente 8 dígitos no formato YYYYMMDD")

    # Extrai ano, mês e dia da string
    ano = data_str[:4]
    mes = data_str[4:6]
    dia = data_str[6:8]

    # Formata a data no formato DD/MM/AAAA
    data_formatada = f"{dia}-{mes}-{ano}"

    return data_formatada

def str_to_csv(data_str, output_file):
        
        csv_data = StringIO(data_str)
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:

            # Criar um objeto DictReader para ler a string como um arquivo CSV
            reader = csv.reader(csv_data)
            
            # Criar um objeto writer para escrever o arquivo CSV
            writer = csv.writer(csvfile)
            
            # Escrever as linhas no arquivo CSV
            for row in reader:
                writer.writerow(row)

# Retorna string do dia anterior
def get_dia_anterior():
    yesterday = datetime.now() - timedelta(2)
    yesterday_str = yesterday.strftime('%Y%m%d')
    return yesterday_str


def get_data(project_key, token):
    url = f"https://or.ammonit.com/api/{project_key}/loggers-list/"
    headers = {"Authorization": f"Token {token}"}
    data = requests.get(url, headers=headers).json()
    if len(data) > 0:
        project_data = data[0]['project']
        key = project_data['key']
        name = project_data['name']
        serial = data[0]['serial']
        latitude = data[0]['override_latitude']
        longitude = data[0]['override_longitude']

    return key, name, serial, latitude, longitude

# Lista de arquivos
# primary para segundos e secodnary para segundos
def get_files(project_key, token, file_type="primary"):
    project_key, name, device_serial, latitude, longitude = get_data(project_key, token)
    url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/{file_type}/"
    headers = {"Authorization": f"Token {token}"}
    data = requests.get(url, headers=headers).json()

    resultados = []
    for i in data:
        if i.get('is_valid'):
            resultados.append(i.get('original_filename'))
    return resultados

if __name__=="__main__":

    if len(sys.argv) != 2:
        print("Uso: python main_ammonit.py dd/mm/yyyy")
        sys.exit(1)

    data_str = sys.argv[1]

    try:
        data = datetime.strptime(data_str, "%d/%m/%Y")
        data_formatada = data.strftime("%Y%m%d")
    except ValueError:
        print("Data inválida. Use o formato dd/mm/yyyy.")
        sys.exit(1)
    
    for project_key, token in estacoes_chave_valor.items():

        headers = {"Authorization": f"Token {token}"}

        lista_arquivos = get_files(project_key, token)

        filtered_files = [file for file in lista_arquivos if data_formatada in file]

        file_type = "primary"

        project_key, name, device_serial, latitude, longitude = get_data(project_key, token)

        if len(filtered_files) > 0:
            url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/{file_type}/{str(filtered_files[0])}/"
            arquivo = requests.get(url, headers=headers)
            resposta = arquivo.json().get('file_content')

            str_to_csv(resposta, filtered_files[0])
            processa_tudo(filtered_files[0], name_project=name, data=converter_data(data_formatada))
        else:
            processa_tudo_ausente(name_project=name, data=converter_data(data_formatada))
            print(f"Não foi encontrado dados do dia especificado para a estação: {name}")


# %%
# %%