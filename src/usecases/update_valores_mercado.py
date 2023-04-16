from repository.mappers.ttv201_valor_mercado_hdr import Ttv201ValorMercadoHdr
from repository.mappers.ttv202_projecao_futura_vm import Ttv202ProjecaoFuturaVm
from datetime import datetime
from repository.repo import Repository
from repository.mappers.tta150_parametro import Tta150Parametro
from repository.mappers.tta036_j_cod_prov_cotacao_mes import Tta036JCodProvCotacaoMes
from repository.mappers.ttv201_valor_mercado_hdr import Ttv201ValorMercadoHdr
from repository.mappers.tta039_j_lista_prod_captura import Tta039JListaProdCaptura
from dataclasses import dataclass
from utils.logger import Logger
from typing import Type, List
from sqlalchemy import or_, and_
from utils.file import readfile_asjson
import logging
import os

class UpdateValoresMercado:

    VM_ATTRIBUTE_FINAL_INDEX = 36

    def __init__(self, repository: Type[Repository]) -> None:
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self, data_referencia: Type[datetime], cotacoes_produtos_folder_path):
        dir_notfound = not os.path.isdir(cotacoes_produtos_folder_path)
        if dir_notfound: 
            self.logger.info(f'Diretório de cotações: {cotacoes_produtos_folder_path} não encontrado')
            raise Exception(f'{cotacoes_produtos_folder_path} not found')

        self.logger.info(f"{len(os.listdir(cotacoes_produtos_folder_path))} arquivos de cotações de produtos as serem processados")

        for dde_cotacao_produto_file in os.listdir(cotacoes_produtos_folder_path):
            cotacao_file_path = os.path.join(cotacoes_produtos_folder_path, dde_cotacao_produto_file)
            self.logger.info(f"Lendo arquivo: {cotacao_file_path}...")

            dde_cotacao_produto_json = readfile_asjson(os.path.join(cotacoes_produtos_folder_path, dde_cotacao_produto_file))

            # Valores mercado do mês referente
            ttv201_valor_mercado_hdr, is_update = self.__populate_ttv201_valor_mercado_hdr(data_referencia, dde_cotacao_produto_json)
            self.logger.info(f'{"Atualizando" if is_update else "Inserindo"} TTV201_VALOR_MERCADO_HDR: {str(ttv201_valor_mercado_hdr.__dict__)}')
            if is_update: self.repository.update(ttv201_valor_mercado_hdr)
            else: self.repository.insert(ttv201_valor_mercado_hdr)

            # Valores mercado futuro
            ttv202_projecao_futura_vm, is_update = self.__popular_lista_ttv202_projecao_futura_vm(
                cd_projecao_futura_vm=ttv201_valor_mercado_hdr.cd_projecao_futura_vm,
                data_referencia=data_referencia,
                dde_cotacao_produto_json=dde_cotacao_produto_json
            )
            self.logger.info(f'{"Atualizando" if is_update else "Inserindo"} TTV202_PROJECAO_FUTURA_VM: {str(ttv202_projecao_futura_vm.__dict__)}')
            if is_update: self.repository.update(ttv202_projecao_futura_vm)
            else: self.repository.insert(ttv202_projecao_futura_vm)
            
        
    def __populate_ttv201_valor_mercado_hdr(self, data_referencia: Type[datetime], dde_cotacao_produto_json):
        self.logger.info(f'Populando TTV201_VALOR_MERCADO_HDR: produto: {str(dde_cotacao_produto_json["cdGrpProduto"])}, cd_parametro_superior: {str(dde_cotacao_produto_json["cdParametroSuperior"])}')
        ttv201_valor_mercado_hdr = self.repository.get(
            mapper=Ttv201ValorMercadoHdr,
            filter=(
                Ttv201ValorMercadoHdr.ano_safra == data_referencia.year,
                Ttv201ValorMercadoHdr.dt_movimento == data_referencia,
                Ttv201ValorMercadoHdr.cd_parametro_superior == dde_cotacao_produto_json["cdParametroSuperior"],
                Ttv201ValorMercadoHdr.cd_produto == dde_cotacao_produto_json['cdGrpProduto']
            )
        )
        is_update = not ttv201_valor_mercado_hdr is None
        is_insert = ttv201_valor_mercado_hdr is None

        if ttv201_valor_mercado_hdr is None:
            ttv201_valor_mercado_hdr = Ttv201ValorMercadoHdr(
                ano_safra=data_referencia.year,
                dt_movimento=data_referencia,
                cd_parametro_superior=dde_cotacao_produto_json['cdParametroSuperior'],
                cd_parametro_inferior=dde_cotacao_produto_json['cdParametroInferior'],
                vl_valor_mercado=None,
                cd_projecao_futura_vm =self.repository.sequence_value("TTV_CD_PROJECAO_FUTURA_VM"),
                cd_produto = dde_cotacao_produto_json['cdGrpProduto'],
                cd_empresa = None,
                ano_mes = None,
                cd_local_embarque = None,
                cd_cidade = None,
                cd_estado = None,
                dt_atualizacao = None,
                dt_criacao = datetime.now(),
                cd_usuario_manutencao = None
            )
        ttv201_valor_mercado_hdr.dt_atualizacao = datetime.now()
        ttv201_valor_mercado_hdr.cd_usuario_manutencao = 'sistema'
        
        valor_mercado = 0
        for cotacao in dde_cotacao_produto_json['cotacoes']:
            if cotacao['month'] == data_referencia.month and cotacao['year'] == data_referencia.year:
                valor_mercado = cotacao['value']
                break

        if is_insert or (is_update and valor_mercado != 0):
            ttv201_valor_mercado_hdr.vl_valor_mercado = valor_mercado
        return (ttv201_valor_mercado_hdr, is_update)

    def __popular_lista_ttv202_projecao_futura_vm(self, cd_projecao_futura_vm, data_referencia: Type[datetime], dde_cotacao_produto_json):
        self.logger.info(f'Populando TTV202_PROJECAO_FUTURA_VM: produto: {str(dde_cotacao_produto_json["cdGrpProduto"])}, cd_parametro_superior: {str(dde_cotacao_produto_json["cdParametroSuperior"])}')
        
        ttv202_projecao_futura_vm = self.repository.get(
            mapper=Ttv202ProjecaoFuturaVm,
            filter=(
                Ttv202ProjecaoFuturaVm.cd_projecao_futura_vm==cd_projecao_futura_vm,
            )
        )
        is_update = not ttv202_projecao_futura_vm is None
        is_insert = ttv202_projecao_futura_vm is None

        if is_insert:
            ttv202_projecao_futura_vm = Ttv202ProjecaoFuturaVm()
            ttv202_projecao_futura_vm.cd_projecao_futura_vm = cd_projecao_futura_vm
        
        cotacoes = dde_cotacao_produto_json['cotacoes']
        cotacoes_mensais_futuras = list(filter(lambda cot: 
            (cot['month'] > data_referencia.month and cot['year'] == data_referencia.year) or (cot['year'] > data_referencia.year), 
            cotacoes
        ))
        cotacoes_mensais_futuras.sort(key=lambda cot: f'{str(cot["month"])} {str(cot["year"])}')
        index = 1
        
        for cotacao in cotacoes_mensais_futuras:
            valor_projecao = cotacao["value"]
            if is_insert or (is_update and valor_projecao > 0):
                setattr(ttv202_projecao_futura_vm, f'vm_{index}', valor_projecao)
            index += 1

        while index <= self.VM_ATTRIBUTE_FINAL_INDEX:
            setattr(ttv202_projecao_futura_vm, f'vm_{index}', 0)
            index += 1

        return (ttv202_projecao_futura_vm, is_update)


            
        
           
        
