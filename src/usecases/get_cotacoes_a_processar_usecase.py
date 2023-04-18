from repository.repo import Repository
from repository.mappers.tta150_parametro import Tta150Parametro
from repository.mappers.tta036_j_cod_prov_cotacao_mes import Tta036JCodProvCotacaoMes
from repository.mappers.ttv201_valor_mercado_hdr import Ttv201ValorMercadoHdr
from repository.mappers.tta039_j_lista_prod_captura import Tta039JListaProdCaptura

from dataclasses import dataclass
from typing import Type, List
import logging

@dataclass
class ProdutoAProcessar:
    id: str
    nome_produto: str
    codigo_produto: str
    multiplicador_de_valor: float
    produto_captura: Type[Tta039JListaProdCaptura]
    parametros_produto: Type[List[Tta036JCodProvCotacaoMes]]

@dataclass
class Output:
    lista_produtos_a_processar: Type[List[ProdutoAProcessar]]

class GetCotacoesAProcessarUsecase:

    MULTIPLICADOR_DE_VALOR_DEFAULT = 1
    MULTIPLICADOR_DE_VALOR_ESPECIAL = 0.01

    def __init__(self, repository: Type[Repository]) -> None:
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self):
        tta150_parametro = self.repository.get(mapper=Tta150Parametro)
        data_referencia = tta150_parametro.dt_vm_ultima_atualizacao
        safra = data_referencia.year

        lista_produtos_captura = self.repository.filter(mapper=Tta039JListaProdCaptura)
        self.logger.info('Produtos a processar: ' + ', '.join(list(map(lambda tta039: f'[cd_produto: {str(tta039.cd_grp_produto)}, cd_parametro_superior: {str(tta039.cd_parametro_superior)}]', lista_produtos_captura))))

        lista_produtos_a_processar = []
        self.logger.info('Obtendo parametros dos produtos')
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

            produtos_com_multiplicador_especial = [143, 287, 405]
            multiplicador_de_valor = self.MULTIPLICADOR_DE_VALOR_ESPECIAL if int(produto_captura.cd_grp_produto) in produtos_com_multiplicador_especial \
                else self.MULTIPLICADOR_DE_VALOR_DEFAULT

            lista_produtos_a_processar.append(
                ProdutoAProcessar(
                    id=f'{produto_captura.cd_parametro_superior} - {produto_captura.produto}',
                    nome_produto=produto_captura.produto,
                    multiplicador_de_valor=multiplicador_de_valor,
                    codigo_produto=produto_captura.cd_grp_produto,
                    produto_captura=produto_captura,
                    parametros_produto=parametros_produto,
                )
            )
        self.logger.debug('Pametros dos produtos: ')
        self.logger.debug(lista_produtos_a_processar)
        return Output(
            lista_produtos_a_processar=lista_produtos_a_processar
        )
            
     
        
        