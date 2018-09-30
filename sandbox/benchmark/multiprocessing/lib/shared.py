# coding; utf-8


class SharedDataInterface(object):
    def get(self, key):
        raise NotImplementedError()

    def set(self, key, value, ctype):
        raise NotImplementedError()

    def create(self, key, position, value):
        raise NotImplementedError()

    def commit(self, key=None):
        raise NotImplementedError()
