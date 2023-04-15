from repository.repo import Repository
from service.dde_client_service import DdeClientService
from dataclasses import dataclass
from utils.logger import Logger
from typing import Type, List
from utils.file import writefile
import random
from os import path
import json
from datetime import datetime
import re
import time 
from utils.var import Var

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
    
    MAXIXUM_BROADCAST_ATTEMPT_VALUE = 5

    def __init__(self, repository: Type[Repository], logger) -> None:
        self.repository = repository
        self.logger = logger
        

    def execute(self, cd_grp_produto, cd_parametro_superior, cd_parametro_inferior, data_referencia, parametros_dde_broadcast):
        index = 0
        cotacoes = []
        self.dde_client_service = DdeClientService("BC")

        for parametro_dde in parametros_dde_broadcast:
            parametro_dde_broadcast_raw = str(parametro_dde.parametro_dde_broadcast)
            parametro_dde_broadcast_parts = parametro_dde_broadcast_raw.split(';')
            is_parametro_dde_invalido = not (len(parametro_dde_broadcast_parts) == 3)
            if is_parametro_dde_invalido: raise Exception(f"Parametro dde invalido: {parametro_dde_broadcast_raw}")
            dde_application, dde_topic, dde_item = parametro_dde_broadcast_parts
            dde_application = dde_application.replace('=', '').strip()
            dde_topic =  dde_topic.strip()
            dde_item =  dde_item.strip()

            self.logger.info(f"[capturar_cotacoes_dde_brodcast_usecase] Conectando ao servidor de DDE: {dde_application}...")
            
            broadcast_value = None
            broadcast_attempt = 0
            while broadcast_value is None:
                self.logger.info(f"[capturar_cotacoes_dde_brodcast_usecase] Buscando valor na broadcast: Safra: {str(parametro_dde.safra)}, Mês:{str(parametro_dde.mes)} Application: {dde_application}, topic: {dde_topic}, item: {dde_item}")
                broadcast_attempt += 1

                try:
                    broadcast_value = self.dde_client_service.get_data(
                        application=dde_application,
                        topic=dde_topic,
                        item=dde_item
                    )
                    print(f"[capturar_cotacoes_dde_brodcast_usecase] DDE[attempt: {str(broadcast_attempt)}]: Application: {dde_application}, topic: {dde_topic}, item: {dde_item} >>> VALUE: {str(broadcast_value)}")
                    broadcast_value = 0 if (type(broadcast_value)) is str else broadcast_value

                except Exception as e:
                    time.sleep(1)
                    self.logger.info(f"[capturar_cotacoes_dde_brodcast_usecase] Broadcast retornou ({broadcast_value}) com os parametros[attempt: {str(broadcast_attempt)}]: {dde_application}, topic: {dde_topic}, item: {dde_item}")
                    print(f"[capturar_cotacoes_dde_brodcast_usecase] Broadcast retornou ({broadcast_value}) com os parametros[attempt: {str(broadcast_attempt)}]: {dde_application}, topic: {dde_topic}, item: {dde_item}")
                    print(str(e))
                    if not Var.IS_RUNNING: 
                        self.logger.info("[capturar_cotacoes_dde_brodcast_usecase] PARADA FORÇADA DURANTE A OBTENÇÃO DE DADOS DO BROADCAST")
                        raise Exception("PARADA FORÇADA DURANTE A OBTENÇÃO DE DADOS DO BROADCAST")
                    if broadcast_attempt >= self.MAXIXUM_BROADCAST_ATTEMPT_VALUE:
                        self.logger.info("[capturar_cotacoes_dde_brodcast_usecase] NUMERO MÁXIMO DE TENTATIVAS")
                        broadcast_value = 0
                        broadcast_attempt = 0

            value = 0 if broadcast_value is None else broadcast_value

            cotacoes.append(Cotacao(
                year=parametro_dde.safra,
                month=index+1, 
                value=value,
                param_dde=parametro_dde_broadcast_raw
            ))
            index += 1
        
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
       
            
        
    