import requests


class reqcapture:
    def __init__(self):
        pass

    @staticmethod
    def returnrequestdata(url, params=None):
        return requests.get(url, params)

    @staticmethod
    def returnjson(r):
        return r.json()
