import pandas as pd
from io import StringIO
from datetime import datetime
import numpy as np
import logging
import os

# Dado um .csv de minuto, retorna o dataframe de dados e o dataframe de metadados
def parser(filename):
    dados = []
    metadados = []
    with open(filename, 'r') as arquivo:
        linhas = arquivo.readlines()

    metadados_encontrados = False

    for linha in linhas:
        if linha.startswith("[System]"):
            metadados_encontrados = True
        if metadados_encontrados:
            metadados.append(linha)
        else:
            dados.append(linha)
    return dados, metadados

def lista_para_df(lista):
    return pd.read_csv(StringIO(''.join(lista)))

def calcular_dia_juliano(timestamp_str):
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    return timestamp.timetuple().tm_yday

def timestamp_para_horalocal(timestamp_str):
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    horalocal = timestamp.hour * 60 + timestamp.minute
    return horalocal

def obter_data_hora():
    agora = datetime.now()
    
    data_hora_str = agora.strftime('%d/%m/%Y %H:%M:%S')    
    return data_hora_str

def etl_minute(df, name_project):

    duplicated_rows = df[df.duplicated()]
    
    df['Date/time'] = pd.to_datetime(df['Date/time'])
    start_timestamp = df["Date/time"].min()
    end_timestamp = df["Date/time"].max()
    all_timestamps = pd.date_range(start=start_timestamp, end=end_timestamp, freq='min')

    missing_timestamps = all_timestamps.difference(df['Date/time'])

    # Tive que fazer essa etapa manual, pois na API alguns dados de latitude e longitude retornavam NULL, mesmo com o dado fornecido
    # no ammonit  ! VERIFICAR ISSO COM CAIO 

    if "PE01" in name_project:
        # Fernando de Noronha PE01
        latitude = 	-3.834722
        longitude = -32.398611
    elif "AP01" in name_project:
        # Santana
        latitude =  -0.053980
        longitude = -51.155080
    elif "AP02" in name_project:
        # Porto Grande
        latitude = 	0.697290
        longitude = -51.389150
    elif "AP03" in name_project:
        # Laranjal
        latitude = 	-0.828611
        longitude = -52.507222
    elif "AP04" in name_project:
        # Ilha de Maracá
        latitude = 	2.096944
        longitude = -50.496944
    else:
        # Tartarugalzinho
        latitude = 1.519722
        longitude = -50.917778


    longitude_ref = -45
    isc = 1367
    colunas = df.columns
    ghi_avg_colunas = [coluna for coluna in colunas if 'GHI' in coluna and coluna.endswith('Avg')]
    info_ghi = {col: {'contador_fisicamente_possivel': 0} for col in ghi_avg_colunas}

    for index, row in df.iterrows():
        timestamp_str = str(row['Date/time'])
        dia_juliano = calcular_dia_juliano(timestamp_str)

        rad = (2 * np.pi * (dia_juliano - 1) / 365)
        eo = 1.00011 + (0.0334221 * np.cos(rad)) + (0.00128 * np.sin(rad)) + (0.000719 * np.cos(2 * rad)) + (0.000077 * np.sin(2 * rad))
        io = isc * eo
        iox = max(io, 0)

        horalocal = timestamp_para_horalocal(timestamp_str)
        et = 229.18 * (0.000075 + 0.001868 * np.cos(rad) - 0.032077 * np.sin(rad) - 0.014615 * np.cos(2 * rad) - 0.04089 * np.sin(2 * rad))
        horasolar = (horalocal + ((4 * (longitude - longitude_ref)) + et)) / 60
        omega = (horasolar - 12) * 15
        declinacao = 23.45 * np.sin(((dia_juliano + 284) * (360 / 365)) * np.pi / 180)
        cosAZS = (np.sin(latitude * np.pi / 180) * np.sin(declinacao * np.pi / 180)) + (np.cos(latitude * np.pi / 180) * np.cos(declinacao * np.pi / 180) * np.cos(omega * np.pi / 180))
        AZS = np.arccos(cosAZS) * 180 / np.pi

        cosAZS12 = cosAZS ** 1.2 if AZS <= 90 else 0
        fpmin = -4
        fpmax = (1.5 * iox * cosAZS12) + 100

        for col in ghi_avg_colunas:
            value = row[col]
            if pd.notna(value) and isinstance(value, (int, float, str)):
                try:
                    value = float(value)
                    if fpmin < value < fpmax:
                        info_ghi[col]['contador_fisicamente_possivel'] += 1
                except ValueError:
                    continue

    return len(duplicated_rows), len(missing_timestamps), info_ghi





def gera_cabecalho(data, arquivo):
    with open(arquivo, 'a', encoding="utf-8") as f:
        f.write(f"Registro diário\n")
        f.write(f"Data: {data}\n")
        f.write(f"Execução: {obter_data_hora()}\n\n\n")



# Tenho que passar de forma automática o Project Name, Serial, Override_latitude e Override_longitude
def processa_tudo(filename, name_project, data, arquivo):
    dados, _ = parser(filename)
    df = lista_para_df(dados)

    print(name_project)

    qtd_duplicados, qtd_missing, dic = etl_minute(df, name_project)



    with open(arquivo, 'a', encoding="utf-8") as f:
        f.write(f"Nome do Projeto: {name_project}\n")
        f.write(f"Data: {data}\n")
        f.write(f"    Quantidade de duplicados: {qtd_duplicados}\n")
        f.write(f"    Quantidade de timestamps faltantes: {qtd_missing}\n")

        outer_key = next(iter(dic))
        inner_dict = dic[outer_key]
        value = next(iter(inner_dict.values()))

        #print(value)

        total = 1440

        f.write(f"    Quantidade fisicamente possíveis: {value}\n")



        anomalos = total - int(value)


        #status = ""
        if anomalos/total < 0.01:
            status = "Consistente"
        elif anomalos/total >= 0.01 and anomalos/total <= 0.05:
            status = "Atenção"
        else:
            status = "Inconsistente"

        porcentagem = (anomalos/total)*100

        f.write(f"          Dados Anômalos: {porcentagem:,.2f}%\n")
        f.write(f"          Situação: {status}\n")

        f.write("\n\n")

def processa_tudo_ausente(name_project, data, arquivo):
    with open(arquivo, 'a', encoding="utf-8") as f:
        f.write(f"Nome do Projeto: {name_project}\n")
        f.write(f"Data: {data}\n")
        f.write(f"Não houve arquivos para o dia especificado.\n")
        
        f.write("\n\n")

