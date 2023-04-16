import logging
from service.dde_client_service import DdeClientService

class TestBroadcastCommunicationUsecase:
    
    MAXIMUM_ATTEMPT_AMOUNT = 40

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        

    def execute(self, application, topic, parameter):
        attemps = 0
        value = None
        self.dde_client_service = DdeClientService(application)
        output = ''
        while attemps < self.MAXIMUM_ATTEMPT_AMOUNT and value is None:
            
            value = self.dde_client_service.get_data(
                application,
                topic,
                parameter
            )

            info = f'Tentativa ({attemps + 1}/{self.MAXIMUM_ATTEMPT_AMOUNT}): Value: {value}'

            self.logger.info(info)
            output += f'{info}\n'
            attemps += 1

        if value is None: 
            self.logger.info("Falha ao buscar valor no broadcast")

        return output

        