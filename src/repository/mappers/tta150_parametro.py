from dataclasses import dataclass
from config.sqlalchemy.base import Base
from sqlalchemy import Column, String, DateTime

@dataclass
class Tta150Parametro(Base):
    __tablename__ = 'TTA150_PARAMETRO'

    ambiente = Column(String, name="AMBIENTE")
    ano_safra_anterior = Column(String, name="ANO_SAFRA_ANTERIOR")
    ano_safra_anterior_bi = Column(String, name="ANO_SAFRA_ANTERIOR_BI")
    ano_safra_atual = Column(String, name="ANO_SAFRA_ATUAL")
    ano_safra_atual_bi = Column(String, name="ANO_SAFRA_ATUAL_BI")
    ano_safra_posterior = Column(String, name="ANO_SAFRA_POSTERIOR")
    ano_safra_posterior_bi = Column(String, name="ANO_SAFRA_POSTERIOR_BI")
    ano_safra_vigente = Column(String, name="ANO_SAFRA_VIGENTE")
    cd_bolsa = Column(String, name="CD_BOLSA")
    cd_conta = Column(String, name="CD_CONTA")
    cd_corretora = Column(String, name="CD_CORRETORA")
    cd_parametro = Column(String, primary_key=True, name="CD_PARAMETRO")
    dh_atual_cotacao = Column(String, name="DH_ATUAL_COTACAO")
    dt_bi = Column(String, name="DT_BI")
    dt_esm_saf_anterior = Column(String, name="DT_ESM_SAF_ANTERIOR")
    dt_esm_saf_atual = Column(String, name="DT_ESM_SAF_ATUAL")
    dt_esm_saf_posterior = Column(String, name="DT_ESM_SAF_POSTERIOR")
    dt_interp_manual = Column(String, name="DT_INTERP_MANUAL")
    dt_virada_safra = Column(String, name="DT_VIRADA_SAFRA")
    dt_vm_ultima_atualizacao = Column(DateTime, name="DT_VM_ULTIMA_ATUALIZACAO")
    email_serv = Column(String, name="EMAIL_SERV")
    fl_aa = Column(String, name="FL_AA")
    fl_conf_email = Column(String, name="FL_CONF_EMAIL")
    fl_exp_cambial = Column(String, name="FL_EXP_CAMBIAL")
    fl_gera_bi = Column(String, name="FL_GERA_BI")
    fl_integracao = Column(String, name="FL_INTEGRACAO")
    fl_orig_virtual = Column(String, name="FL_ORIG_VIRTUAL")
    fl_versao_cliente = Column(String, name="FL_VERSAO_CLIENTE")
    hora_fim = Column(String, name="HORA_FIM")
    hora_ini = Column(String, name="HORA_INI")
    host_serv_email = Column(String, name="HOST_SERV_EMAIL")
    id_saf_atual = Column(String, name="ID_SAF_ATUAL")
    id_saf_post = Column(String, name="ID_SAF_POST")
    interpolar_ptax = Column(String, name="INTERPOLAR_PTAX")
    nr_dias = Column(String, name="NR_DIAS")
    porta_serv = Column(String, name="PORTA_SERV")
    senha_serv = Column(String, name="SENHA_SERV")
    versao = Column(String, name="VERSAO")
    versao_sistema = Column(String, name="VERSAO_SISTEMA")


