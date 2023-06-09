from repository.repo import Repository
from repository.mappers.tta150_parametro import Tta150Parametro
from repository.mappers.tta036_j_cod_prov_cotacao_mes import Tta036JCodProvCotacaoMes
from repository.mappers.ttv201_valor_mercado_hdr import Ttv201ValorMercadoHdr
from repository.mappers.tta039_j_lista_prod_captura import Tta039JListaProdCaptura
from dataclasses import dataclass
from typing import Type, List
from utils.file import writefile
from os import path
import json
import logging
from datetime import datetime
import random

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

class CapturarCotacoesDDEBroadcastFakeCotacoesTestUsecase:
    
    def __init__(self, repository: Type[Repository]) -> None:
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self, cd_grp_produto, cd_parametro_superior, cd_parametro_inferior, multiplicador_de_valor: float, parametros_dde_broadcast):
        cotacoes = []
        for parametro_dde_broadcast in parametros_dde_broadcast:
            cotacoes.append(
                Cotacao(
                    year=parametro_dde_broadcast.safra,
                    month=parametro_dde_broadcast.mes,
                    param_dde=parametro_dde_broadcast.parametro_dde_broadcast, 
                    value=parametro_dde_broadcast.valor_teste * multiplicador_de_valor + (random.random() * 0.001)
                )
            )

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
       
            
        
    