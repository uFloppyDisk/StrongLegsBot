import json


class JSON:
    def __init__(self):
        pass

    @staticmethod
    def returndict(strjson):
        return json.loads(strjson)
