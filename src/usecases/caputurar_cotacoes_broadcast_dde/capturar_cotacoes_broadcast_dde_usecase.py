from repository.repo import Repository
from service.dde_client_service import DdeClientService
from utils.file import writefile

from os import path
import json
from datetime import datetime
from dataclasses import dataclass
import time 
import logging
from utils.var import Var
from typing import Type, List

@dataclass
class ParametroDDEInput:
    safra: int
    mes: int
    cd_grp_produto: int
    parametro_dde_broadcast: str
    valor_teste: float

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

class CapturarCotacoesDDEBroadcastUsecase:
    
    MAXIXUM_number_of_attempts_VALUE = 5


    def __init__(self, repository: Type[Repository]) -> None:
        self.repository = repository
        self.logger = logging.getLogger(__name__)
        
        self.logger.debug('CapturarCotacoesDDEBroadcastUsecase initialized')
        
    def execute(self, cd_grp_produto, cd_parametro_superior, cd_parametro_inferior, multiplicador_de_valor: float, parametros_dde_broadcast: Type[List[ParametroDDEInput]]):
        index = 0
        cotacoes = []
        
        for parametro_dde in parametros_dde_broadcast:
            dde_application, dde_topic, dde_item, parametro_dde_broadcast_raw = self.__get_dde_broadcast_param(parametro_dde)

            self.logger.info(f"Conectando ao servidor de DDE: {dde_application} ...")

            value = self.__get_dde_broadcast_value(
                dde_application=dde_application,
                dde_topic=dde_topic,
                dde_item=dde_item, 
                parametro_dde=parametro_dde
            )
            
            value = value * multiplicador_de_valor

            cotacoes.append(Cotacao(
                year=parametro_dde.safra,
                month=parametro_dde.mes, 
                value=value,
                param_dde=parametro_dde_broadcast_raw
            ))
            index += 1
        
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
            content=cotacao_json
        )
        self.logger.debug(cotacao_json)

        return Output(
            cd_grp_produto=cd_grp_produto,
            cotacoes=cotacoes
        )
       
    def __get_dde_broadcast_param(self, parametro_dde):
        parametro_dde_broadcast_raw = str(parametro_dde.parametro_dde_broadcast)
        parametro_dde_broadcast_parts = f'{parametro_dde_broadcast_raw}'.split(';')
        is_parametro_dde_invalido = not (len(parametro_dde_broadcast_parts) == 3)
        if is_parametro_dde_invalido: raise Exception(f"Parametro dde invalido: {parametro_dde_broadcast_raw}")
        dde_application, dde_topic, dde_item = parametro_dde_broadcast_parts

        dde_application = dde_application.replace('=', '').strip()
        dde_topic = dde_topic.strip()
        dde_item = dde_item.strip()

        return (dde_application, dde_topic, dde_item, parametro_dde_broadcast_raw)

    def __get_dde_broadcast_value(self, dde_application, dde_topic, dde_item, parametro_dde):
        broadcast_value = None
        number_of_attempts = 0

        self.dde_client_service = DdeClientService(dde_application)
        while broadcast_value is None and number_of_attempts < self.MAXIXUM_number_of_attempts_VALUE:
            
            self.logger.info(f"Buscando valor na broadcast+ {dde_application}({str(number_of_attempts + 1)}/{str(self.MAXIXUM_number_of_attempts_VALUE)}): Safra: {str(parametro_dde.mes)}/{str(parametro_dde.safra)} > [topic: '{dde_topic}', item: '{dde_item}']")
            number_of_attempts += 1

            broadcast_value = self.dde_client_service.get_data(
                application=f'{dde_application.strip()}',
                topic=f'{dde_topic.strip()}',
                item=f'{dde_item.strip()}'
            )

            invalid_broadcast_values = ["N/D", "N/A", ""]
            is_invalid_broadcast_value = broadcast_value is None or broadcast_value in invalid_broadcast_values
            is_valid_broadcast_value = not is_invalid_broadcast_value and str(broadcast_value).replace(',', '').replace('.', '').isdigit()

            self.logger.info(f'Valor obtido da broadcast+[{"INVALID" if is_invalid_broadcast_value else "VALID"}]: {str(broadcast_value)}')

            if is_valid_broadcast_value:
                broadcast_value = float(str(broadcast_value).replace('.', '').replace(',', '.'))
            
            if is_invalid_broadcast_value:
                time.sleep(.5)
                if not Var.IS_RUNNING: 
                    self.logger.info("Parada forçada durante a obtenção de valores do broadcast+ DDE")
                    raise Exception("Parada forçada durante a obtenção de valores do broadcast+ DDE")
        
        broadcast_value = 0 if (type(broadcast_value)) is str or broadcast_value is None else broadcast_value
        return broadcast_value
    