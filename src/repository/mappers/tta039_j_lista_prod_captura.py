from dataclasses import dataclass
from config.sqlalchemy.base import Base
from sqlalchemy import Column, Integer, String, Float

@dataclass
class Tta039JListaProdCaptura(Base):
    __tablename__ = 'TTA039_J_LISTA_PROD_CAPTURA'
    
    cd_parametro_superior = Column(String, primary_key=True, name="CD_PARAMETRO_SUPERIOR")
    cd_parametro_inferior = Column(String, primary_key=True,name="CD_PARAMETRO_INFERIOR")
    cd_grp_produto = Column(String, primary_key=True, name="CD_GRP_PRODUTO")
    produto = Column(String, primary_key=True, name="PRODUTO")
    cot_teste = Column(Float, name="COT_TESTE")
