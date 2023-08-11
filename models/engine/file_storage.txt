#!/usr/bin/python3
"""class FileStorage"""

import json
from models.base_model import BaseModel


class FileStorage:
    """
        serializes instances to a JSON file and
        deserializes JSON file to instances
    """
    __file_path = "file.json"
    __objects = {}

    def all(self):
        """returns the dictionary __objects"""
        return self.__objects

    def new(self, obj):
        """sets in __objects the obj with key"""
        class_name = obj.__class__.__name__
        key = "{}.{}".format(class_name, obj.id)
        self.__objects[key] = obj

    def save(self):
        """serializes __objects to the Json file"""
        objdict = {}
        for key, obj in self.__objects.items():
            objdict[key] = obj.to_dict()
        with open(self.__file_path, "w", encoding="utf-8") as file:
            json.dump(objdict, file)

    def reload(self):
        """
            deserializes the JSON file to __objects
            only if the JSON file (__file_path) exists
        """
        try:
            with open(self.__file_path, "r", encoding="utf-8") as file:
                objdict = json.load(file)
                for key, value in objdict.items():
                    class_name = value.get("__class__")
                    obj_id = value.get("id")
                    if class_name and obj_id:
                        instance = globals().get(class_name)(**value)
                        self.__objects[key] = instance
        except FileNotFoundError:
            pass
