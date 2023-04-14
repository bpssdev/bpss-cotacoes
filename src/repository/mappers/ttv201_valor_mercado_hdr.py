from dataclasses import dataclass
from config.sqlalchemy.base import Base
from sqlalchemy import Column, String, Date, Integer, Double, DateTime


@dataclass()
class Ttv201ValorMercadoHdr(Base):
    __tablename__ = 'TTV201_VALOR_MERCADO_HDR'
    
    ano_safra = Column(Integer, primary_key=True, name="ANO_SAFRA")
    dt_movimento = Column(Date, primary_key=True, name="DT_MOVIMENTO")
    cd_parametro_superior = Column(Integer, primary_key=True, name="CD_PARAMETRO_SUPERIOR")
    cd_parametro_inferior = Column(Integer, primary_key=True, name="CD_PARAMETRO_INFERIOR")

    vl_valor_mercado = Column(Double, name="VL_VALOR_MERCADO")
    cd_projecao_futura_vm = Column(Integer, name="CD_PROJECAO_FUTURA_VM")
    cd_produto = Column(Integer, name="CD_PRODUTO")
    cd_empresa = Column(Integer, name="CD_EMPRESA")
    ano_mes = Column(String, name="ANO_MES")
    cd_local_embarque = Column(Integer, name="CD_LOCAL_EMBARQUE")
    cd_cidade = Column(Integer, name="CD_CIDADE")
    cd_estado = Column(Integer, name="CD_ESTADO")
    dt_atualizacao = Column(DateTime, name="DT_ATUALIZACAO")
    dt_criacao = Column(String, name="DT_CRIACAO")
    cd_usuario_manutencao = Column(String, name="CD_USUARIO_MANUTENCAO")
    cd_classe_trigo = Column(String, name="CD_CLASSE_TRIGO")
    cd_ph_trigo = Column(String, name="CD_PH_TRIGO")
   