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
from json import dump
from typing import Type, List
from sqlalchemy import or_, and_
from utils.file import readfile_asjson
import logging
import os

@dataclass
class Cotacao:
    year: int
    month: int
    param_dde: str
    value: float

@dataclass
class CotacaoProduto:

    timestamp: datetime
    cd_grp_produto: int
    cd_parametro_superior: int
    cd_parametro_inferior: int
    cotacoes: Type[List[Cotacao]]

    def __init__(self, file) -> None:
        dde_cotacao_produto_json = readfile_asjson(file)
        self.timestamp = dde_cotacao_produto_json['timestamp']
        self.cd_grp_produto = dde_cotacao_produto_json['cdGrpProduto']
        self.cd_parametro_superior = dde_cotacao_produto_json['cdParametroSuperior']
        self.cd_parametro_inferior = dde_cotacao_produto_json['cdParametroInferior']
        self.cotacoes = []
        for cotacao in dde_cotacao_produto_json['cotacoes']:
            self.cotacoes.append(Cotacao(
                year=cotacao['year'],
                month=cotacao['month'],
                param_dde=cotacao['param_dde'],
                value=cotacao['value'],
            ))
    
    def get_cotacoes_by_safra(self, safra):
        return list(filter(lambda cot: cot.year == safra, self.cotacoes))
    
    def get_value_of_cotacao_by(self, safra, mes):
        cotacao = next(filter(lambda cot: cot.year == safra and cot.month == mes, self.cotacoes))
        return 0.0 if cotacao is None else cotacao.value

class UpdateValoresMercado:

    VM_ATTRIBUTE_FINAL_INDEX = 36
    MES_DE_JANEIRO = 1
    ULTIMO_MES_DO_ANO = 12

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

            dde_cotacao_produto_json_file = os.path.join(cotacoes_produtos_folder_path, dde_cotacao_produto_file)
            cotacao_produto = CotacaoProduto(file=dde_cotacao_produto_json_file)

            # Valores mercado do safra atual(ano data referencia)
            ttv201_valor_mercado_hdr_atual, is_update = self.__populate_ttv201_valor_mercado_hdr_safra_atual(
                data_referencia, 
                cotacao_produto
            )
            self.logger.info(f'{"Atualizando" if is_update else "Inserindo"} TTV201_VALOR_MERCADO_HDR (SAFRA ATUAL): {str(ttv201_valor_mercado_hdr_atual.__dict__)}')
            if is_update: self.repository.update(ttv201_valor_mercado_hdr_atual)
            else: self.repository.insert(ttv201_valor_mercado_hdr_atual)

            # Valores mercado futuro da safra atual
            ttv202_projecao_futura_vm, is_update = self.__popular_lista_ttv202_projecao_futura_vm_safra_atual(
                cd_projecao_futura_vm=ttv201_valor_mercado_hdr_atual.cd_projecao_futura_vm,
                data_referencia=data_referencia,
                cotacao_produto=cotacao_produto
            )
            self.logger.info(f'{"Atualizando" if is_update else "Inserindo"} TTV202_PROJECAO_FUTURA_VM: {str(ttv202_projecao_futura_vm.__dict__)}')
            if is_update: self.repository.update(ttv202_projecao_futura_vm)
            else: self.repository.insert(ttv202_projecao_futura_vm)

            # Valores mercado do safra futura(ano data referencia + 1, mes 1(janeiro))
            ttv201_valor_mercado_hdr_futuro, is_update = self.__populate_ttv201_valor_mercado_hdr_safra_futura(
                data_referencia, 
                cotacao_produto
            )
            self.logger.info(f'{"Atualizando" if is_update else "Inserindo"} TTV201_VALOR_MERCADO_HDR (SAFRA FUTURA): {str(ttv201_valor_mercado_hdr_futuro.__dict__)}')
            if is_update: self.repository.update(ttv201_valor_mercado_hdr_futuro)
            else: self.repository.insert(ttv201_valor_mercado_hdr_futuro)
            
            # Valores mercado futuro da safra futura
            ttv202_projecao_futura_vm_safra_futuro, is_update = self.__popular_lista_ttv202_projecao_futura_vm_safra_futura(
                cd_projecao_futura_vm=ttv201_valor_mercado_hdr_futuro.cd_projecao_futura_vm,
                data_referencia=data_referencia,
                cotacao_produto=cotacao_produto
            )
            self.logger.info(f'{"Atualizando" if is_update else "Inserindo"} TTV202_PROJECAO_FUTURA_VM (SAFRA FUTURA): {str(ttv202_projecao_futura_vm_safra_futuro.__dict__)}')
            if is_update: self.repository.update(ttv202_projecao_futura_vm_safra_futuro)
            else: self.repository.insert(ttv202_projecao_futura_vm_safra_futuro)


            
            
        
    def __populate_ttv201_valor_mercado_hdr_safra_atual(self, data_referencia: Type[datetime], cotacao_produto: Type[CotacaoProduto]):
        self.logger.info(f'Populando TTV201_VALOR_MERCADO_HDR: produto: {str(cotacao_produto.cd_grp_produto)}, cd_parametro_superior: {str(cotacao_produto.cd_parametro_superior)}')
        ttv201_valor_mercado_hdr = self.repository.get(
            mapper=Ttv201ValorMercadoHdr,
            filter=(
                Ttv201ValorMercadoHdr.ano_safra == data_referencia.year,
                Ttv201ValorMercadoHdr.dt_movimento == data_referencia,
                Ttv201ValorMercadoHdr.cd_parametro_superior == cotacao_produto.cd_parametro_superior,
                Ttv201ValorMercadoHdr.cd_produto == cotacao_produto.cd_grp_produto
            )
        )
        is_update = not ttv201_valor_mercado_hdr is None
        is_insert = ttv201_valor_mercado_hdr is None

        if ttv201_valor_mercado_hdr is None:
            ttv201_valor_mercado_hdr = Ttv201ValorMercadoHdr(
                ano_safra=data_referencia.year,
                dt_movimento=data_referencia,
                cd_parametro_superior=cotacao_produto.cd_parametro_superior,
                cd_parametro_inferior=cotacao_produto.cd_parametro_inferior,
                vl_valor_mercado=None,
                cd_projecao_futura_vm =self.repository.sequence_value("TTV_CD_PROJECAO_FUTURA_VM"),
                cd_produto = cotacao_produto.cd_grp_produto,
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
        
        valor_mercado = cotacao_produto.get_value_of_cotacao_by(
            safra=data_referencia.year,
            mes=data_referencia.month
        )

        if is_insert or (is_update and valor_mercado != 0):
            ttv201_valor_mercado_hdr.vl_valor_mercado = valor_mercado

        return (ttv201_valor_mercado_hdr, is_update)

    def __populate_ttv201_valor_mercado_hdr_safra_futura(self, data_referencia: Type[datetime], cotacao_produto: Type[CotacaoProduto]):
        self.logger.info(f'Populando TTV201_VALOR_MERCADO_HDR: produto: {str(cotacao_produto.cd_grp_produto)}, cd_parametro_superior: {str(cotacao_produto.cd_parametro_superior)}')
        ano_referencia_futura = data_referencia.year + 1

        ttv201_valor_mercado_hdr = self.repository.get(
            mapper=Ttv201ValorMercadoHdr,
            filter=(
                Ttv201ValorMercadoHdr.ano_safra == ano_referencia_futura,
                Ttv201ValorMercadoHdr.dt_movimento == data_referencia,
                Ttv201ValorMercadoHdr.cd_parametro_superior == cotacao_produto.cd_parametro_superior,
                Ttv201ValorMercadoHdr.cd_produto == cotacao_produto.cd_grp_produto
            )
        )
        is_update = not ttv201_valor_mercado_hdr is None
        is_insert = ttv201_valor_mercado_hdr is None

        if ttv201_valor_mercado_hdr is None:
            ttv201_valor_mercado_hdr = Ttv201ValorMercadoHdr(
                ano_safra=ano_referencia_futura,
                dt_movimento=data_referencia,
                cd_parametro_superior=cotacao_produto.cd_parametro_superior,
                cd_parametro_inferior=cotacao_produto.cd_parametro_inferior,
                vl_valor_mercado=None,
                cd_projecao_futura_vm =self.repository.sequence_value("TTV_CD_PROJECAO_FUTURA_VM"),
                cd_produto = cotacao_produto.cd_grp_produto,
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
        
        valor_mercado = cotacao_produto.get_value_of_cotacao_by(
            safra=ano_referencia_futura,
            mes=1
        )

        if is_insert or (is_update and valor_mercado != 0):
            ttv201_valor_mercado_hdr.vl_valor_mercado = valor_mercado

        return (ttv201_valor_mercado_hdr, is_update)

    def __popular_lista_ttv202_projecao_futura_vm_safra_atual(self, cd_projecao_futura_vm, data_referencia: Type[datetime], cotacao_produto: Type[CotacaoProduto]):
        self.logger.info(f'Populando TTV202_PROJECAO_FUTURA_VM: produto: {str(cotacao_produto.cd_grp_produto)}, cd_parametro_superior: {str(cotacao_produto.cd_parametro_superior)}')
        
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
        
        mes = data_referencia.month + 1
        ano_safra = data_referencia.year
        index_attributo_vm = 1
        while mes <= self.ULTIMO_MES_DO_ANO:
            valor_projecao = cotacao_produto.get_value_of_cotacao_by(
                safra=ano_safra,
                mes=mes
            )
            if is_insert or (is_update and valor_projecao > 0):
                setattr(ttv202_projecao_futura_vm, f'vm_{index_attributo_vm}', valor_projecao)
            index_attributo_vm += 1
            mes += 1

        while index_attributo_vm <= self.VM_ATTRIBUTE_FINAL_INDEX:
            setattr(ttv202_projecao_futura_vm, f'vm_{index_attributo_vm}', 0)
            index_attributo_vm += 1

        return (ttv202_projecao_futura_vm, is_update)
    
    def __popular_lista_ttv202_projecao_futura_vm_safra_futura(self, cd_projecao_futura_vm, data_referencia: Type[datetime], cotacao_produto: Type[CotacaoProduto]):
        self.logger.info(f'Populando TTV202_PROJECAO_FUTURA_VM: produto: {str(cotacao_produto.cd_grp_produto)}, cd_parametro_superior: {str(cotacao_produto.cd_parametro_superior)}')
        
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
        
        mes = self.MES_DE_JANEIRO
        ano_safra_futura = data_referencia.year + 1
        index_attributo_vm = self.ULTIMO_MES_DO_ANO - data_referencia.month + 1 # Continua a apartir do umtimo index vm da projecacao da safra atual

        while mes <= self.ULTIMO_MES_DO_ANO:
            valor_projecao = cotacao_produto.get_value_of_cotacao_by(
                safra=ano_safra_futura,
                mes=mes
            )
            if is_insert or (is_update and valor_projecao > 0):
                setattr(ttv202_projecao_futura_vm, f'vm_{index_attributo_vm}', valor_projecao)
            index_attributo_vm += 1
            mes += 1

        while index_attributo_vm <= self.VM_ATTRIBUTE_FINAL_INDEX:
            setattr(ttv202_projecao_futura_vm, f'vm_{index_attributo_vm}', 0)
            index_attributo_vm += 1

        return (ttv202_projecao_futura_vm, is_update)


            
        
           
        
