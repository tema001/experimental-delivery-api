from abc import abstractmethod, ABCMeta

from shared.domain.entity import Entity


class GenericRepository(metaclass=ABCMeta):

    @abstractmethod
    def get_by_id(self, _id: int):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError
