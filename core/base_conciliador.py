from abc import ABC, abstractmethod


class BaseConciliador(ABC):

    @abstractmethod
    def carregar_erp(self, arquivo):
        pass


    @abstractmethod
    def carregar_operadora(self, arquivo):
        pass


    @abstractmethod
    def preprocessar(self):
        pass


    @abstractmethod
    def conciliar(self):
        pass


    @abstractmethod
    def gerar_saida(self):
        pass