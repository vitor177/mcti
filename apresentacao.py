
# %%

import json
import requests
from datetime import datetime, timedelta    
import csv
from io import StringIO
from ammonit_relatorio import processa_tudo

PROJECT_KEY = "GWFR"
TOKEN = "f7c9d9394c73b9bd3d020eb485d5387de6b4d31b"
SERVER_URL = "https://or.ammonit.com"
FILE_TYPE = "primary"
headers = {"Authorization": f"Token {TOKEN}"}


# Lista de dispositivos em projeto com seus metadados básicos

url = f"{SERVER_URL}/api/{PROJECT_KEY}/loggers-list/"
data = requests.get(url, headers=headers).json()

# %%
data
# %%

# Informações básicas sobre um dispositivo específico no projeto
url = f"{SERVER_URL}/api/{PROJECT_KEY}/D230012/files/{FILE_TYPE}/"
data = requests.get(url, headers=headers).json()
data
# %%
url = f"https://or.ammonit.com/api/{PROJECT_KEY}/D230012/files/{FILE_TYPE}/"
data = requests.get(url, headers=headers).json()
data
# %%

url = f"https://or.ammonit.com/api/{PROJECT_KEY}/D230012/files/{FILE_TYPE}/D230012_20240729_0000.csv/"
data = requests.get(url, headers=headers).json()
data
# %%
url = f"https://or.ammonit.com/api/{PROJECT_KEY}/D230012/completeness/"
data = requests.get(url, headers=headers).json()
data
# %%
url = f" https://or.ammonit.com/api/{PROJECT_KEY}/D230012/completeness/day/"