#!/usr/bin/python3
"""file storage class"""

import json
from models.base_model import BaseModel
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.user import User


class FileStorage:
    """
    defines file storage class that serializes instances to a JSON file
    and also deserializes JSON file to instances
    """
    __file_path = "file.json"
    __objects = {}  # it will store all objects

    def all(self):
        """
        returns the dictionary __objects
        """
        return self.__objects

    def new(self, obj):
        """
        sets in __objects the obj with key <obj class name>.id
        """
        class_name = obj.__class__.__name__
        self.__objects[f"{class_name}.{obj.id}"] = obj

    def save(self):
        """
        serializes __objects to the JSON file (path: __file_path)
        """
        obj_dict = {}
        for key, obj in self.__objects.items():
            obj_dict[key] = obj.to_dict()
        with open(self.__file_path, "w") as file:
            json.dump(obj_dict, file)

    def reload(self):
        """
        deserializes the JSON file to __objects
        only if the JSON file (__file_path) exists
        """
        clslist = {
            'BaseModel': BaseModel,
            'State': State,
            'City': City,
            'Amenity': Amenity,
            'Place': Place,
            'Review': Review,
            'User': User
        }
        try:
            with open(self.__file_path, "r") as file:
                obj_dict = json.load(file)
                for key, value in obj_dict.items():
                    class_name, obj_id = key.split(".")
                    self.__objects[key] = globals()[class_name](**value)
        except FileNotFoundError:
            pass
