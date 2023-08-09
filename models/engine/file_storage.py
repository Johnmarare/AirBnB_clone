#!/usr/bin/python3
"""serialization and deserialization of instances and JSON files"""
import json
from models.base_model import BaseModel


class FileStorage:
    """
        serializes instances to a JSON file and deserializes JSON file to instances
    """
    __file_path = "file.json"
    __objects = {}

    def all(self):
        """Returns the dictionary __objects"""
        return FileStorage.__objects
    
    def new(self, obj):
        """sets in __objects the obj with key <obj class name>.id"""
        class_name = obj.__class__.__name__
        key = "{}.{}".format(class_name, obj.id)
        FileStorage.__objects[key] = obj

    def save(self):
        """serializes __objects to the JSON file (path: __file_path)"""
        with open(FileStorage.__file_path, "w") as f:
            temp = {}
            temp.update(FileStorage.__objects)
            for key, value in temp.items():
                temp[key] = value.to_dict()
            json.dump(temp, f)
    
    def reload(self):
        """
        deserializes the JSON file to __objects (only if the JSON file (__file_path) exists;
        otherwise, do nothing.
        If the file does not exist, no exception should be raised)
        """
        try:
        # Open JSON file for reading
            with open(FileStorage.__file_path, "r") as f:
                # Load from file
                data = json.load(f)
                # Iterate through loaded data and recreate instances
                for key, value in data.items():
                    class_name = value['__class__']
                    # get the class from its name
                    main_class = eval(class_name)
                    # create an instance using the dictionary
                    instance = main_class(**value)
                    FileStorage.__objects[key] = instance
                # debugging
                print("Reloaded objects", FileStorage.__objects)
        except FileNotFoundError:
            pass
