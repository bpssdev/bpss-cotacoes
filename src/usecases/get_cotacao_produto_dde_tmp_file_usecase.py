import os
from utils.file import readfile_asjson
from dataclasses import dataclass
from datetime import datetime
from typing import List, Type
import logging

@dataclass
class Cotacao:
    safra: int
    month: int
    param_dde: str
    value: float

@dataclass
class Output:
    timestamp: datetime
    cd_grp_produto: int
    cd_parametro_superior: int
    cd_parametro_inferior: int
    cotacoes: Type[List[Cotacao]]

class GetCotacaoProdutoDdeTmpFileUsecase:

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def execute(self, cd_grp_produto, cd_parametro_superior):
        cotacao_file_path = os.path.join("tmp", "dde", f"cotacao_prod_{cd_grp_produto.strip()}_param_{cd_parametro_superior.strip()}.json")
        cotacao_file_not_exists = not os.path.exists(cotacao_file_path)

        if cotacao_file_not_exists: 
            self.logger.info("Não há cotações disponiveis no diretório tmp/dde")
            return None

        cotacao_file_json = readfile_asjson(cotacao_file_path)
        
        return Output(
            timestamp=datetime.strptime(cotacao_file_json["timestamp"], '%Y-%m-%dT%H:%M:%S.%f'),
            cd_grp_produto=cotacao_file_json["cdGrpProduto"],
            cd_parametro_superior=cotacao_file_json["cdParametroSuperior"],
            cd_parametro_inferior=cotacao_file_json["cdParametroInferior"],
            cotacoes=[
                Cotacao(
                    safra=cot["year"],
                    month=cot["month"],
                    param_dde=cot["param_dde"],
                    value=cot["value"]
                ) for cot in cotacao_file_json["cotacoes"]
            ]
        )