import sys
import os
import requests
import time
import json
from datetime import datetime


# Variáveis globais
diretorio_download = ''
delay_download = 0
nome_versao = ''


def set_nome_versao():
    """Define nome base de versão"""
    global nome_versao
    nome_versao = datetime.today().strftime('%Y%m%d-%H%M')


def set_diretorio_download(diretorio):
    """Define pasta raiz de download"""
    global diretorio_download
    diretorio_download = diretorio


def set_delay_download(segundos):
    """Define delay para realização de download"""
    global delay_download
    delay_download = segundos


def formata_data_hora_atual():
    """Retorna texto de data e hora atual no formato padrão de data e hora"""
    return formata_data_hora(datetime.today())


def formata_data_hora(data):
    """Retorna texto de formato padrão de data e hora"""
    return data.strftime('%d/%m/%Y %H:%M:%S')


def log(metodo, descricao):
    """Imprime log na tela com o horário atual"""
    if descricao:
        print('{data} => {metodo} - {descricao}'.format(data=formata_data_hora_atual(), metodo=metodo, descricao=descricao))
    else:
        print('{data} => {metodo}'.format(data=formata_data_hora_atual(), metodo=metodo))


def log_linha():
    """Imprime linha para separação de log"""
    print('{data} => {separador}'.format(data=formata_data_hora(datetime.today()), separador = '='*150))


def log_linha_simples():
    """Imprime linha para separação de log"""
    print('{data} => {separador}'.format(data=formata_data_hora(datetime.today()), separador = '-'*150))


def listar_stop_words():
    """Retorna lista de stop words"""
    lst = []
    lst_arq = open('{}/stopwords.txt'.format(diretorio_download), 'r', encoding='utf-8').readlines()
    for ite in lst_arq:
        lst.append(ite.replace('\n','').strip())
    return lst


def listar_stop_caracters():
    """Retorna lista de stop caracters"""
    lst = []
    lst_arq = open('{}/stopcaracters.txt'.format(diretorio_download), 'r', encoding='utf-8').readlines()
    for ite in lst_arq:
        lst.append(ite.replace('\n','').strip())
    lst.append('\n')
    return lst


def open_read(arquivo, diretorio):
    """Retorna abertura de arquivo no modo leitura e UTF-8"""
    if diretorio:
        return open('{diretorio}/{arquivo}'.format(diretorio=diretorio, arquivo=arquivo), 'r', encoding='utf-8')
    else:
        return open('{diretorio}/{arquivo}'.format(diretorio=diretorio_download, arquivo=arquivo), 'r', encoding='utf-8')


def open_write(arquivo, diretorio):
    """Retorna abertura de arquivo no modo escrita e UTF-8"""
    if diretorio:
        return open('{diretorio}/{arquivo}'.format(diretorio=diretorio, arquivo=arquivo), 'w', encoding='utf-8')
    else:
        return open('{diretorio}/{arquivo}'.format(diretorio=diretorio_download, arquivo=arquivo), 'w', encoding='utf-8')


def download_html(url, diretorio, arquivo):
    """Realiza download de arquivo html"""
    log('download_html', 'Arquivo {diretorio}/{arquivo}.html'.format(diretorio=diretorio, arquivo=arquivo))
    try:
        page = requests.get(url).text
        arq = open_write('{}.html'.format(arquivo), diretorio)
        arq.write(page)
        arq.close()
    except:
        log('download_html', 'Erro download html')


def diretorio_pesquisa_html(versao):
    """Retorna diretorio com base em versão ou raiz de pesquisa"""
    if versao:
        return '{diretorio}/pesquisa-html/{versao}'.format(diretorio=diretorio_download, versao=versao)
    else:
        return '{diretorio}/pesquisa-html'.format(diretorio=diretorio_download)


def diretorio_vaga_html():
    """Retorna diretorio com base em raiz de pesquisa"""
    return "{diretorio}/vaga-html".format(diretorio=diretorio_download)


def diretorio_vaga_json():
    """Retorna diretorio com base em raiz de pesquisa"""
    return "{diretorio}/vaga-json".format(diretorio=diretorio_download)


def listar_linkedin_vaga_pesquisa():
    """Retorna lista com informações de vagas (podendo repetir)"""
    log_linha()
    log("listar_linkedin_vaga_pesquisa", None)
    arq_vaga = open_read('vagas-pesquisa.json', None)
    lst_vaga = json.load(arq_vaga)
    arq_vaga.close()
    return lst_vaga


def listar_linkedin_vaga_valida():
    """Retorna lista com informações de vagas (únicas)"""
    log_linha()
    log("listar_linkedin_vaga_valida", None)
    arq_vaga = open_read('vagas-valida.json', None)
    lst_vaga = json.load(arq_vaga)
    arq_vaga.close()
    return lst_vaga
