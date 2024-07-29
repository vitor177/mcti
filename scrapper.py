
# import requests
# %%
import json
import requests

# Definindo as variáveis
server_url = "https://or.ammonit.com"  # URL do servidor AmmonitOR
project_key = "GWFR"  # Project Key
token = "f7c9d9394c73b9bd3d020eb485d5387de6b4d31b"  # Token de autenticação


# Função para formatar a saída
def format_output(output):
    return json.dumps(json.loads(output.decode("utf-8")), indent=4, sort_keys=True)

device_serial = "D230012"
#url = f"{server_url}/api/{project_key}/loggers-list/"
#url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/"


#  List of all the device measurement files in AmmonitOR 
url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/"


file_type = "primary"
# List of all the device files in AmmonitOR
url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/{file_type}/"


file = "D230012_20240725_0000_sec.csv"

# Download of the measurement file content (one file per request only).
#url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/{file}/"

# Download of the file content (one file per request only).
#url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/{file_type}/{file}/"

url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/{file_type}/"

headers = {"Authorization": f"Token {token}"}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    with open("meu_teste.json", 'w', encoding='utf-8') as file:
        file.write(format_output(response.content))
else:
    print(f"Error: {response.status_code}")
    print(response.json())

# %%
type(response.json())

# %%
data = response.json()


# print(type(data))
# file_content = data.get("file_content", "")
# print(file_content)
# output_filename = data.get("original_filename", "output.csv")


# %%
type(response.json())
# %%
resultados = []
for i in response.json():
    if i.get('is_valid'):
        resultados.append(i.get('original_filename'))
    #print(i.get('original_filename'))
    #print(i)

# %%
resultados
# %%
from datetime import datetime, timedelta    
yesterday = datetime.now() - timedelta(1)
yesterday_str = yesterday.strftime('%Y%m%d')
yesterday_str
# %%
yesterday_files = [file for file in resultados if yesterday_str in file]
yesterday_files

# %%
# %%

url = f"https://or.ammonit.com/api/{project_key}/{device_serial}/files/{file_type}/{str(yesterday_files[0])}/"

arquivo = requests.get(url, headers=headers)

# %%
type(arquivo)

# %%
resposta = arquivo.json().get('file_content')
# %%
resposta 
# %%
arquivo.content
# %%
import csv
from io import StringIO

def str_to_csv(data_str, output_file):
    """
    Converte uma string com dados CSV para um arquivo CSV.
    
    Args:
        data_str (str): A string contendo os dados no formato CSV.
        output_file (str): O caminho do arquivo CSV de saída.
    """
    # Usar StringIO para tratar a string como um arquivo
    csv_data = StringIO(data_str)
    
    # Abrir o arquivo CSV de saída
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Criar um objeto DictReader para ler a string como um arquivo CSV
        reader = csv.reader(csv_data)
        
        # Criar um objeto writer para escrever o arquivo CSV
        writer = csv.writer(csvfile)
        
        # Escrever as linhas no arquivo CSV
        for row in reader:
            writer.writerow(row)

    print(f"Dados salvos em {output_file}")

# Exemplo de uso:
csv_string = resposta
output_csv_file = 'output.csv'
str_to_csv(csv_string, output_csv_file)

# %%
import pandas as pd
df = pd.read_csv('output.csv')
df.tail()
# %%
print(df[:1441].isna().sum().sum())
# %%
# %%
5840/40
# %%
df[1440:]