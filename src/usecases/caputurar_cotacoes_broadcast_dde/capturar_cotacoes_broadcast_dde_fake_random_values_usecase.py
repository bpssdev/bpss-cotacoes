from repository.repo import Repository
from repository.mappers.tta150_parametro import Tta150Parametro
from repository.mappers.tta036_j_cod_prov_cotacao_mes import Tta036JCodProvCotacaoMes
from repository.mappers.ttv201_valor_mercado_hdr import Ttv201ValorMercadoHdr
from repository.mappers.tta039_j_lista_prod_captura import Tta039JListaProdCaptura
from dataclasses import dataclass
from utils.logger import Logger
from typing import Type, List
from utils.file import writefile
import random
from os import path
import json
from datetime import datetime

@dataclass
class ParametroDDEInput:
    safra: int
    mes: int
    cd_grp_produto: int
    parametro_dde_broadcast: str

@dataclass
class Cotacao:
    year: int
    month: int
    param_dde: str
    value: float

@dataclass
class Output:
    cd_grp_produto: int
    cotacoes: Type[List[Cotacao]]

class CapturarCotacoesDDEBroadcastFakeRandomValuesUsecase:
    
    DDE_APPLICATION_NAME = 'BC'
    DDE_TOPIC = 'Cot'

    def __init__(self, repository: Type[Repository], logger) -> None:
        self.repository = repository
        self.logger = logger

    def execute(self, cd_grp_produto, cd_parametro_superior, cd_parametro_inferior, data_referencia, parametros_dde_broadcast):
        def getvalue():
            return random.uniform(1, 100)
        cotacoes = [
                Cotacao(1, parametros_dde_broadcast[0].parametro_dde_broadcast, getvalue()),
                Cotacao(2, parametros_dde_broadcast[1].parametro_dde_broadcast, getvalue()),
                Cotacao(3, parametros_dde_broadcast[2].parametro_dde_broadcast, getvalue()),
                Cotacao(4, parametros_dde_broadcast[3].parametro_dde_broadcast, getvalue()),
                Cotacao(5, parametros_dde_broadcast[4].parametro_dde_broadcast, getvalue()),
                Cotacao(6, parametros_dde_broadcast[5].parametro_dde_broadcast, getvalue()),
                Cotacao(7, parametros_dde_broadcast[6].parametro_dde_broadcast, getvalue()),
                Cotacao(8, parametros_dde_broadcast[7].parametro_dde_broadcast, getvalue()),
                Cotacao(9, parametros_dde_broadcast[8].parametro_dde_broadcast, getvalue()),
                Cotacao(10, parametros_dde_broadcast[9].parametro_dde_broadcast, getvalue()),
                Cotacao(11, parametros_dde_broadcast[10].parametro_dde_broadcast, getvalue()),
                Cotacao(12, parametros_dde_broadcast[11].parametro_dde_broadcast, getvalue()),
        ]
        output = Output(
            cd_grp_produto=cd_grp_produto,
            cotacoes=cotacoes
        )
        cotacao_json = json.dumps({
                "timestamp": datetime.now().isoformat(),
                "cdGrpProduto": cd_grp_produto,
                "cdParametroSuperior": cd_parametro_superior,
                "cdParametroInferior": cd_parametro_inferior,
                "cotacoes": [cot.__dict__ for cot in cotacoes]
            }, indent=4
        )
        writefile(
            path=path.join('tmp', 'dde', f'cotacao_prod_{cd_grp_produto}_param_{cd_parametro_superior}.json'), 
            content=cotacao_json)
        self.logger.info(cotacao_json)
        return output
       
            
        
    