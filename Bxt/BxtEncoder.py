from json import JSONEncoder


class BxtEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__
