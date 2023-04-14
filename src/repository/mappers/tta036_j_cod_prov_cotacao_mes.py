from dataclasses import dataclass
from config.sqlalchemy.base import Base
from sqlalchemy import Column, Integer, String

@dataclass
class Tta036JCodProvCotacaoMes(Base):
    __tablename__ = 'TTA036_J_COD_PROV_COTACAO_MES'
    
    cd_grp_produto = Column(Integer, primary_key=True, name="CD_GRP_PRODUTO")
    mes = Column(Integer, primary_key=True, name="MES")
    safra = Column(Integer, primary_key=True, name="SAFRA")

    cd_parametro_superior = Column(Integer, primary_key=True, name="CD_PARAMETRO_SUPERIOR")

    cod_prod_prov = Column(String, name="COD_PROD_PROV")
    nm_grp_produto = Column(String, name="NM_GRP_PRODUTO")


