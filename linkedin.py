import sys
import os
import json
import time
import langid
from lxml import html
from datetime import datetime

#Projeto
import util

#Define variáveis globais
util.set_diretorio_download(sys.argv[1])
util.set_delay_download(int(sys.argv[2]))
util.set_nome_versao()
processo = sys.argv[3]


def crawler_linkedin_pesquisa():
    """Realiza crawler no linkedin por estado, cidade e descrição"""
    util.log_linha()
    util.log('crawler_linkedin_pesquisa', None)

    lst_cidade = []
    arq_cidade = util.open_read('cidade.json', None)
    lst_cidade = json.load(arq_cidade)
    arq_cidade.close()

    lst_descricao = []
    arq_descricao = util.open_read('descricao.json', None)
    lst_descricao = json.load(arq_descricao)
    arq_descricao.close()

    # Download htmls de vagas no linkedin
    for cid in lst_cidade:
        for des in lst_descricao:
            time.sleep(util.delay_download)
            descricao = des['descricao']
            estado = cid['estado']
            cidade = cid['cidade']

            local = '{cidade}, {estado}'.format(estado=estado, cidade=cidade)
            url = 'https://www.linkedin.com/jobs/search/?keywords={descricao}&location={local}'.format(descricao=descricao, local=local)
            arquivo = '{versao}-{estado}-{cidade}-{descricao}'.format(versao=util.nome_versao, estado=estado, cidade=cidade, descricao=descricao)

            diretorio = util.diretorio_pesquisa_html(util.nome_versao)
            if not os.path.isdir(diretorio):
                os.makedirs(diretorio)

            util.download_html(url, diretorio, arquivo)


def scrapy_linkedin_pesquisa():
    """Realiza scrapy no linkedin em pesquisa estado, cidade e descrição"""
    util.log_linha()
    util.log('scrapy_linkedin_pesquisa', None)

    lst_vaga = []

    diretorio = util.diretorio_pesquisa_html(None)
    for dir, subdir, nomes in os.walk(diretorio):
        for nome in nomes:
            estado = nome.split('-')[2]
            cidade = nome.split('-')[3]
            util.log('scrapy_linkedin_pesquisa', '{} / {}'.format(estado, cidade))

            arq = util.open_read(nome, dir)
            txt = ''.join(arq.readlines())
            arq.close()
            tree = html.fromstring(txt)
            vagas = tree.xpath('//li[@class="result-card job-result-card result-card--with-hover-state"]/a[@class="result-card__full-card-link"]/@href[1]')

            for ite_vaga in vagas:
                ite = {}
                ite['url'] = ite_vaga.split('?')[0]
                ite['codigo'] = ite['url'].split('-')[-1].strip()
                ite['titulo'] = tree.xpath('//li[@class="result-card job-result-card result-card--with-hover-state"]/a[@href="{}"]//span[1]/text()'.format(ite_vaga))[0]
                ite['estado'] = estado
                ite['cidade'] = cidade
                ite['arquivo'] = nome
                lst_vaga.append(ite)

    # Cria lista de vagas de pesquisa
    arq_json = util.open_write('vagas-pesquisa.json', None)
    txt_json = json.dumps(lst_vaga, ensure_ascii=False, indent=4)
    arq_json.write(txt_json)
    arq_json.close()


def crawler_linkedin_vaga():
    """Realiza crawler no linkedin por estado, cidade e descrição"""
    util.log_linha()
    util.log("crawler_linkedin_vaga", None)

    lst_vaga = util.listar_linkedin_vaga()

    # Download htmls de vagas no linkedin
    for ite in lst_vaga:
        url = ite['url']
        estado = ite['estado']
        cidade = ite['cidade']
        codigo = ite['codigo']
        titulo = ite['titulo']

        util.log_linha_simples()
        util.log('crawler_linkedin_vaga', 'Codigo ({codigo}) Titulo ({titulo})'.format(codigo=codigo, titulo=titulo))
        util.log('crawler_linkedin_vaga', 'Estado ({estado}) Cidade ({cidade})'.format(estado=estado, cidade=cidade))
        util.log('crawler_linkedin_vaga', '{url}'.format(url=url))

        #Cria diretório caso não exista
        diretorio = util.diretorio_vaga_html()
        if not os.path.isdir(diretorio):
            os.makedirs(diretorio)

        #Realiza download caso arquivo não exista na pasta
        if not os.path.isfile('{diretorio}/{codigo}.html'.format(diretorio=diretorio, codigo=codigo)):
            time.sleep(util.delay_download)
            util.download_html(url, diretorio, codigo)


def scrapy_linkedin_vaga():
    """Realiza scrapy no linkedin em vaga"""
    util.log_linha()
    util.log('scrapy_linkedin_vaga', None)

    lst_vaga_pesquisa = util.listar_linkedin_vaga_pesquisa()
    dic_vaga_valida = {}

    # Busca vaga por código em pasta
    for ite in lst_vaga_pesquisa:
        util.log('scrapy_linkedin_vaga', '{} - {} / {} - {}'.format(ite['codigo'], ite['estado'], ite['cidade'], ite['titulo']))

        arq = util.open_read('{}.html'.format(ite['codigo']), util.diretorio_vaga_html())
        txt = ''.join(arq.readlines())
        arq.close()
        tree = html.fromstring(txt)

        titulo = tree.xpath('//div[@class="topcard__content-left"]/*[self::h1]/text()')
        empresa = tree.xpath('//a[@class="topcard__org-name-link topcard__flavor--black-link"]/text()')
        local = tree.xpath('//span[@class="topcard__flavor topcard__flavor--bullet"]/text()')
        descricao = tree.xpath('//div[@class="description__text description__text--rich"]//text()')

        descricao_lst = []
        for d in descricao:
            try:
                texto = d.strip().replace('"','')
                if texto:
                    descricao_lst.append(texto)
            except:
                log('scrapy_linkedin_vaga', 'Falha')

        vaga = {}
        vaga['codigo'] = ite['codigo']
        vaga['estado'] = ite['estado']
        vaga['cidade'] = ite['cidade']
        vaga['localizacao'] = '{cidade}, {estado}'.format(estado=vaga['estado'], cidade=vaga['cidade'])
        vaga['titulo'] = ite['titulo']
        vaga['empresa'] = ''
        vaga['descricao'] = ''
        vaga['idioma'] = ''

        if titulo:
            vaga['titulo'] = titulo[0]
        if empresa:
            vaga['empresa'] = empresa[0]
        if local:
            vaga['localizacao'] = local[0]
        if descricao_lst:
            vaga['descricao'] = '\n'.join(descricao_lst)
            vaga['idioma'] = langid.classify(vaga['descricao'])[0]

        if vaga['descricao']:
            # Cria arquivos
            dir_json = util.diretorio_vaga_json()
            if not os.path.isdir(dir_json):
                os.makedirs(dir_json)
            arq_json = util.open_write('{codigo}.json'.format(codigo=ite['codigo']), dir_json)
            txt_json = json.dumps(vaga, ensure_ascii=False, indent=4)
            arq_json.write(txt_json)
            arq_json.close()

            # Inclui em listas
            ite_valido = {}
            ite_valido['codigo'] = vaga['codigo']
            ite_valido['estado'] = vaga['estado']
            ite_valido['cidade'] = vaga['cidade']
            ite_valido['localizacao'] = vaga['localizacao']
            ite_valido['titulo'] = vaga['titulo']
            ite_valido['empresa'] = vaga['empresa']
            ite_valido['idioma'] = vaga['idioma']
            dic_vaga_valida[ite_valido['codigo']] = ite_valido

    # Cria lista de vagas únicas
    lst_vaga_valida = []
    for i in dic_vaga_valida:
        lst_vaga_valida.append(dic_vaga_valida[i])
    arq_json = util.open_write('vagas-valida.json', None)
    txt_json = json.dumps(lst_vaga_valida, ensure_ascii=False, indent=4)
    arq_json.write(txt_json)
    arq_json.close()


#Controle principal
if __name__ == '__main__':
    if processo == 'CP':
        crawler_linkedin_pesquisa()
    if processo == 'SP':
        scrapy_linkedin_pesquisa()
    if processo == 'CV':
        crawler_linkedin_vaga()
    if processo == 'SV':
        scrapy_linkedin_vaga()
