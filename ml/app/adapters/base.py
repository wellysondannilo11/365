from abc import ABC,abstractmethod
class Adapter(ABC):
    name='base'
    @abstractmethod
    def fetch(self,*args,**kwargs):...
