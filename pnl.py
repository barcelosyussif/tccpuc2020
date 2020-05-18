import sys
import os
import json
import collections
from collections import Counter

# Projeto
import util

# Define variáveis globais
util.set_diretorio_download(sys.argv[1])
lst_stop_words = util.listar_stop_words()
lst_stop_caracters = util.listar_stop_caracters()


def extrair_palavras():
    """Pesquisa palavras e extrai por vaga"""
    util.log_linha()
    util.log('extrair_palavras', None)

    dic_vaga_palavra = {}
    lst_vaga = util.listar_linkedin_vaga_valida()

    # Percorre palavras por vaga
    for ite_vaga in lst_vaga:
        codigo = ite_vaga['codigo']
        dic_vaga_palavra[codigo] = []
        dir_json = "{diretorio}/{codigo}.json".format(diretorio=util.diretorio_vaga_json(), codigo=codigo)

        if os.path.isfile(dir_json):
            arq_vaga = open(dir_json, 'r', encoding='utf-8')
            ite_vaga = json.load(arq_vaga)
            arq_vaga.close()
            descricao = ite_vaga['descricao'].lower().strip()

            if len(descricao) > 0:
                # Limpa stopcaracters
                for ite in lst_stop_caracters:
                    descricao = descricao.replace('{}'.format(ite), ' ')

                # Quebra palavras, desconsidera stopwords
                lst_descricao = descricao.split(' ')
                for ite in lst_descricao:
                    ite = ite.strip()
                    if ite and ite not in lst_stop_words:
                        dic_vaga_palavra[codigo].append(ite)

    # Define proximidade entre palavras no arquivo
    dic_palavra = {}
    for ite_vaga in dic_vaga_palavra.items():
        codigo = ite_vaga[0]
        lst_palavra = ite_vaga[1]
        seq = 0
        qtd = len(lst_palavra)
        lst_faixa = [1, 3, 5, 10]

        for ite_palavra in lst_palavra:
            # Criação de palavra em lista vazia
            if not dic_palavra.get(ite_palavra):
                dic_palavra[ite_palavra] = {}
                dic_palavra[ite_palavra]['qtd'] = 0
                dic_palavra[ite_palavra]['doc'] = []
                for faixa in lst_faixa:
                    dic_palavra[ite_palavra]['+-' + str(faixa)] = []
                    dic_palavra[ite_palavra]['+' + str(faixa)] = []
                    dic_palavra[ite_palavra]['-' + str(faixa)] = []
            dic_palavra[ite_palavra]['qtd'] = dic_palavra[ite_palavra]['qtd'] + 1

            # Inclusão de correlação em faixas
            for faixa in lst_faixa:
                min, max = seq-faixa, seq+faixa+1
                if min < 0: min = 0
                if max >= qtd: max = qtd
                for i in lst_palavra[min:seq]:
                    dic_palavra[ite_palavra]['+-' + str(faixa)].append(i)
                    dic_palavra[ite_palavra]['-' + str(faixa)].append(i)
                for i in lst_palavra[seq+1:max]:
                    dic_palavra[ite_palavra]['+-' + str(faixa)].append(i)
                    dic_palavra[ite_palavra]['+' + str(faixa)].append(i)

            # Incremento sequencial palavras
            seq = seq+1

    # Cria arquivos de palavras por vagas
    lst = []
    for vaga in dic_vaga_palavra.items():
        i = {}
        i['palavras'] = vaga[1]
        i['codigo'] = vaga[0]
        lst.append(i)

    arq_json = util.open_write('palavras-vagas.json', None)
    txt_json = json.dumps(lst, ensure_ascii=False, indent=1)
    arq_json.write(txt_json)
    arq_json.close()

    # Cria arquivo de palavras por proximidade
    lst = []
    for termo in dic_palavra:
        i = {}
        i['palavra'] = termo
        i['quantidade'] = dic_palavra[termo]['qtd']
        i['proximidade'] = dic_palavra[termo]['+-5']
        lst.append(i)

    arq_json = util.open_write('palavras-proximidade.json', None)
    txt_json = json.dumps(lst, ensure_ascii=False, indent=1)
    arq_json.write(txt_json)
    arq_json.close()

    return dic_palavra


dic_termos = extrair_palavras()

util.log_linha()
util.log('PNL', 'Proximidade 1 (seguinte)')
for termo in dic_termos:
    proximidade = 1
    peso_relacao = 0.8
    lst = dic_termos[termo]['+' + str(proximidade)]
    cnt = Counter(lst)
    qtd = dic_termos[termo]['qtd']
    if qtd > 50:
        qtdmin = int(qtd * peso_relacao)
        lstmin = [i for i in cnt.items() if i[1] > qtdmin]
        if len(lstmin) > 0:
            print('Termo {} - Qtd Termo {} '.format(termo, qtd), sorted(lstmin, key=lambda x: x[1], reverse=True))

util.log_linha()
util.log('PNL', 'Proximidade 5 (anteriores e seguintes)')
for termo in ['sql','power','oracle','server','etl','intelligence','learning','machine','business','qlik','metodologias','graduação']:
    proximidade = 5
    peso_relacao = 0.1
    lst = dic_termos[termo]['+-' + str(proximidade)]
    cnt = Counter(lst)
    qtd = dic_termos[termo]['qtd']
    qtdmin = int(qtd * peso_relacao)
    lstmin = [i for i in cnt.items() if i[1] > qtdmin]
    if len(lstmin) > 0:
        print('Termo {} - Qtd Termo {} '.format(termo, qtd), sorted(lstmin, key=lambda x: x[1], reverse=True))
        print('')
