import json


class JsonHandler:
    @classmethod
    def load_json(cls, path):
        with open(path) as json_file:
            data = json.load(json_file)
        return data
