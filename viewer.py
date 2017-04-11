from abc import ABCMeta, abstractmethod


class Viewer(object, metaclass=ABCMeta):
    @abstractmethod
    def circle():
        pass

    @abstractmethod
    def line():
        pass

