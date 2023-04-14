from repository.mappers.ttv201_valor_mercado_hdr import Ttv201ValorMercadoHdr

from repository.repo import Repository
from repository.mappers.tta150_parametro import Tta150Parametro
from repository.mappers.tta036_j_cod_prov_cotacao_mes import Tta036JCodProvCotacaoMes
from repository.mappers.ttv201_valor_mercado_hdr import Ttv201ValorMercadoHdr
from repository.mappers.tta039_j_lista_prod_captura import Tta039JListaProdCaptura
from dataclasses import dataclass
from utils.logger import Logger
from typing import Type, List
from sqlalchemy import or_, and_

@dataclass
class CotacaoAProcessar:
    id: str
    nome_produto: str
    codigo_produto: str
    produto_captura: Type[Tta039JListaProdCaptura]
    parametros_produto: Type[List[Tta036JCodProvCotacaoMes]]

@dataclass
class Output:
    cotacoes_a_processar: Type[List[CotacaoAProcessar]]

class GetCotacoesAProcessarUsecase:

    def __init__(self, repository: Type[Repository], logger) -> None:
        self.repository = repository
        self.logger = logger

    def execute(self):
        tta150_parametro = self.repository.get(mapper=Tta150Parametro)
        data_referencia = tta150_parametro.dt_vm_ultima_atualizacao
        safra = data_referencia.year
        mes = data_referencia.month

        lista_produtos_captura = self.repository.filter(mapper=Tta039JListaProdCaptura)

        cotacoes_a_processar = []
        for produto_captura in lista_produtos_captura:
            parametros_produto = self.repository.filter(
                mapper=Tta036JCodProvCotacaoMes, 
                filter=(
                    Tta036JCodProvCotacaoMes.safra >= safra,
                    Tta036JCodProvCotacaoMes.cd_grp_produto == produto_captura.cd_grp_produto,
                    Tta036JCodProvCotacaoMes.cd_parametro_superior == produto_captura.cd_parametro_superior,
                    
                ),
                order_by=(
                    Tta036JCodProvCotacaoMes.safra,
                    Tta036JCodProvCotacaoMes.cd_grp_produto,
                    Tta036JCodProvCotacaoMes.mes)
            )
            cotacoes_a_processar.append(
                CotacaoAProcessar(
                    id=f'{produto_captura.cd_parametro_superior} - {produto_captura.produto}',
                    nome_produto=produto_captura.produto,
                    codigo_produto=produto_captura.cd_grp_produto,
                    produto_captura=produto_captura,
                    parametros_produto=parametros_produto,
                )
            )

        return Output(
            cotacoes_a_processar=cotacoes_a_processar
        )
            
     
        
        