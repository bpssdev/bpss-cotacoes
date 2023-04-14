from repository.repo import Repository
import datetime
import time
from os import path
import re
from threading import Thread
from utils.var import Var
from utils.logger import Logger
from utils import formatter
from repository.mappers.tta150_parametro import Tta150Parametro
from usecases.caputurar_cotacoes_broadcast_dde.capturar_cotacoes_broadcast_dde_usecase import  CapturarCotacoesDDEBroadcastUsecase, ParametroDDEInput
from usecases.caputurar_cotacoes_broadcast_dde.capturar_cotacoes_broadcast_dde_fake_cotacoes_teste_usecase import CapturarCotacoesDDEBroadcastFakeCotacoesTestUsecase
from usecases.get_cotacoes_a_processar_usecase import GetCotacoesAProcessarUsecase
#from usecases.capturar_cotacoes_broadcast_dde_usecase import CapturarCotacoesDDEBroadcastUsecase, ParametroDDEInput

from usecases.update_valores_mercado import UpdateValoresMercado
from usecases.get_cotacao_produto_dde_tmp_file_usecase import GetCotacaoProdutoDdeTmpFileUsecase
from service.application_status_service import ApplicationStatusService
from utils.file import readfile_asjson, createdir
from gui.view_async_runner import run_async
from tkinter import messagebox
from utils.configuration import Configuration

class ViewAction:

    def __init__(self, view):
        self.view = view
        self.configuration = Configuration()
        self.repository = Repository()
        self.logger = Logger("log/application.log")
        self.application_status_service = ApplicationStatusService()
        self.get_cotacoes_usecase = GetCotacoesAProcessarUsecase(self.repository, self.logger)
        self.capurar_dde_broadcast_usecase = CapturarCotacoesDDEBroadcastFakeCotacoesTestUsecase(self.repository, self.logger) if self.configuration.test_mode else CapturarCotacoesDDEBroadcastUsecase(self.repository, self.logger)
        self.update_valores_mercado = UpdateValoresMercado(self.repository, self.logger)
        self.get_cotacao_produto_tmp_usecase = GetCotacaoProdutoDdeTmpFileUsecase()
        createdir("tmp")
        

    def init(self):
        def job():
            self.view.set_loading(True)
            self.view.update('status', f'Carregando dados iniciais...')
            output = self.get_cotacoes_usecase.execute()
            tta150_parametro = self.repository.get(Tta150Parametro)
            application_status = self.application_status_service.get_status()
            data_referencia = tta150_parametro.dt_vm_ultima_atualizacao
            
            self.view.update('data_referencia', data_referencia.strftime("%d/%m/%Y - %H:%M:%S"))
            self.view.update('data_ultima_atualizacao', application_status.last_update.strftime("%d/%m/%Y - %H:%M:%S") if not application_status.last_update is None else '')
            self.view.update('lista_produtos', list(map(lambda o: (o.codigo_produto, o.id), output.cotacoes_a_processar)), is_options=True)
            self.view.update('lista_produtos', 0)
            self.handle_select_produto(None)
            self.view.update('inicio_processamento', tta150_parametro.hora_ini)
            self.view.update('fim_processamento', tta150_parametro.hora_fim)
            self.view.set_loading(False)
            self.view.update('status', f'Parado')
        def onerror(exception):
            self.view.set_loading(False)
            messagebox.showwarning(title="Aviso", message=str(exception))

        run_async(job, self.logger, onerror)

    def handle_start(self):
        
        def is_dentro_do_periodo_processamento(tta150_parametro):
            is_perido_processamento_definido = not tta150_parametro.hora_fim is None and not tta150_parametro.hora_ini is None
            is_periodo_processamento_bem_formatado = re.match('\d{2}:\d{2}', tta150_parametro.hora_fim) or re.match('\d{2}:\d{2}', tta150_parametro.hora_ini)
            if is_perido_processamento_definido and is_periodo_processamento_bem_formatado:
                today = datetime.datetime.now()
                today_time_in_seconds = today.hour * 60 * 60 + today.minute * 60 + today.second
                hora_fim, minutos_fim = tta150_parametro.hora_fim.split(":")
                hora_fim_in_seconds = int(hora_fim) * 60 * 60 + int(minutos_fim) * 60
                hora_ini, minutos_ini = tta150_parametro.hora_ini.split(":")
                hora_ini_in_seconds = int(hora_ini) * 60 * 60 + int(minutos_ini) * 60
                
                is_dentro_do_periodo = today_time_in_seconds >= hora_ini_in_seconds and today_time_in_seconds <= hora_fim_in_seconds
                return is_dentro_do_periodo
            return False

        def job():
            self.view.set_loading(True)
            Var.IS_RUNNING = True

            tta150_parametro = self.repository.get(Tta150Parametro)
            is_fora_do_periodo = not is_dentro_do_periodo_processamento(tta150_parametro)
            if is_fora_do_periodo:
                self.view.update('status', f'Finalizado, forado do período de processamento: de {tta150_parametro.hora_ini} até {tta150_parametro.hora_fim}')
                self.logger.info("FORA DO PERIODO DE PROCESSAMENTO DE COTAÇÕES")
                self.logger.info("FIM DO PROCESSAMENTO DE COTAÇÕES")
                self.view.set_loading(False)
                return
            
            self.view.update('status', f'Carregando dados iniciais...')
            data_referencia = tta150_parametro.dt_vm_ultima_atualizacao
            cotacoes_a_processar = self.get_cotacoes_usecase.execute().cotacoes_a_processar
            
            while Var.IS_RUNNING:
                is_fora_do_periodo = not is_dentro_do_periodo_processamento(tta150_parametro)
                if is_fora_do_periodo:
                    self.view.update('status', f'Aguardando atingir o período de processamento: de {tta150_parametro.hora_ini} até {tta150_parametro.hora_fim}')
                    self.logger.info("FORA DO PERIODO DE PROCESSAMENTO DE COTAÇÕES")
                    self.logger.info("PROXIMA TENTATIVA EM 5 MINUTOS")
                    time.sleep(5 * 60)
                    self.view.set_loading(False)
                    continue

                index = 0
                for cotacao in cotacoes_a_processar:
                    self.logger.info(f"BUSCANDO COTAÇÕES NO BROADCAST PRODUTO: {cotacao.codigo_produto}, PARAMETRO SUPERIOR: {cotacao.produto_captura.cd_parametro_superior}")
                    self.view.update('lista_produtos', index)
                    self.view.update('status', f'Processando {cotacao.nome_produto}...')
                    time.sleep(0.5)
                    self.view.update('status', f'Buscando cotações no broadcast: {cotacao.nome_produto}...')
                    cotacoes_produto = self.capurar_dde_broadcast_usecase.execute(
                        cd_grp_produto=cotacao.codigo_produto,
                        cd_parametro_superior=cotacao.produto_captura.cd_parametro_superior,
                        cd_parametro_inferior=cotacao.produto_captura.cd_parametro_inferior,
                        parametros_dde_broadcast=[
                            ParametroDDEInput(
                                cd_grp_produto=param.cd_grp_produto,
                                mes=param.mes,
                                parametro_dde_broadcast=param.cod_prod_prov,
                                safra=param.safra,
                                valor_teste=cotacao.produto_captura.cot_teste
                            ) for param in cotacao.parametros_produto
                        ],
                        data_referencia=data_referencia
                    )
                    self.logger.info(f"COTAÇÕES OBTIDAS NO BROADCAST PRODUTO: {cotacao.codigo_produto}, PARAMETRO SUPERIOR: {cotacao.produto_captura.cd_parametro_superior}")
                    self.view.update('cotacoes_por_produto_treeview', list(map(lambda cot: 
                            (cot.year,
                            formatter.format_month(cot.month), 
                            cot.param_dde,
                            cot.value), cotacoes_produto.cotacoes)))
                    index += 1

                #time.sleep(1)
                self.view.update('status', f'Atualizando banco de dados...')
                self.logger.info("ATUALIZANDO REGISTROS NO BANCO DE DADOS")
                self.update_valores_mercado.execute(
                    data_referencia=data_referencia,
                    cotacoes_produtos_folder_path=path.join('tmp', 'dde')
                )

                self.logger.info("REGISTROS ATUALIZADOS NO BANCO DE DADOS")
                application_status = self.application_status_service.get_status()
                application_status.last_update = datetime.datetime.now()
                self.application_status_service.update_status(application_status)
                
                # Var.IS_RUNNING = False
                
                self.view.update('data_ultima_atualizacao', application_status.last_update.strftime("%m/%d/%Y - %H:%M:%S"))
                self.view.update('lista_produtos', None)

                time.sleep(5)

                
            self.logger.info("FIM DO PROCESSAMENTO DE COTAÇÕES")
            self.view.set_loading(False)
            self.view.update('status', f'Finalizado')
           
        def onerror(exception):
            self.view.set_loading(False)
            self.view.update('status', f'Finalizado')
            messagebox.showwarning(title="Aviso", message=str(exception))

        self.logger.info("PROCESSANDO COTAÇÕES")
        run_async(job, self.logger, onerror)


       

    def handle_stop(self):
        def job():
            Var.IS_RUNNING = False

        self.logger.info("SOLICITANDO PARADA DO PROCESSAMENTO DE COTAÇÕES, AGUARDE FINALIZAÇÃO")
        run_async(job, self.logger)

    def handle_select_produto(self, *args):
        def job():
            selected_product = self.view.getvalue("lista_produtos")
            if selected_product is None or selected_product == '': return
            
            cd_parametro_superior, x, cd_grp_produto, *args = selected_product.split(' ')
            if cd_parametro_superior is None or cd_grp_produto is None: return
            output = self.get_cotacao_produto_tmp_usecase.execute(
                cd_grp_produto=cd_grp_produto,
                cd_parametro_superior=cd_parametro_superior
            )
            if output is None: return
            self.view.update(
                'cotacoes_por_produto_treeview', 
                list(map(lambda cot: (
                    cot.safra,
                    formatter.format_month(cot.month), 
                    cot.param_dde,
                    cot.value
                ), output.cotacoes))
            )
        
        run_async(job, self.logger)
        
        

    