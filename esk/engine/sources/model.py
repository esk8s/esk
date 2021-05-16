import abc


class ESKSource(metaclass=abc.ABCMeta):
    def __init__(self, backends):
        pass

    @abc.abstractmethod
    def create_secret(self, path: str, file_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def update_secret(self, full_file_path: str):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_secret(self, full_file_path: str):
        raise NotImplementedError
