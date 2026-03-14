import json
import os


class JSONStorage:
    def __init__(self, file_path="data.json"):
        self.file_path = file_path
        
        # create file if not exists
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)

    def read(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def write(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def add(self, key, value_dict):
        data = self.read()
        data[key] = value_dict
        self.write(data)

    def get(self, key):
        data = self.read()
        return data.get(key, None)

    def update(self, key, new_values):
        data = self.read()

        if key in data:
            data[key].update(new_values)
            self.write(data)
        else:
            print("Key not found")

    def delete(self, key):
        data = self.read()

        if key in data:
            del data[key]
            self.write(data)