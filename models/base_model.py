#!/usr/bin/python3
"""This is a BaseModel class that defines
    all common attributes/methods for other classes
"""
import uuid
import datetime


class BaseModel:
    """This is the parent class of all other classes in the project"""

    def __init__(self, *args, **kwargs):
        """
        Args:
            id (str): The goal is to have unique id for each BaseModel
            created_at (aware): datetime - assign with the current datetime
            when an instance is created
            updated_at (aware): datetime - assign with the current datetime
            when an instance is created
            and it will be updated every time you change your object
        """
        self.id = str(uuid.uuid4())  # generate a uuid and convert it to string
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.updated_at = self.created_at

        if kwargs:
            for key, value in kwargs.items():
                if key != '__class__':
                    setattr(self, key, value)
            if 'created_at' in kwargs:
                if isinstance(kwargs['created_at'], str):
                    self.created_at = datetime.datetime.strptime(
                        kwargs['created_at'], "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    self.created_at = kwargs['created_at']
            if 'updated_at' in kwargs:
                if isinstance(kwargs['updated_at'], str):
                    self.updated_at = datetime.datetime.strptime(
                        kwargs['updated_at'], "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    self.updated_at = kwargs['updated_at']

    def __str__(self):
        """returns class name, id and __dict__"""
        class_name = self.__class__.__name__
        return "[{}] ({}) {}".format(class_name, self.id, self.__dict__)

    def save(self):
        """updates the public instance attribute
            updated_at with the current datetime
        """
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)

    def to_dict(self):
        """returns a dictionary
            containing all keys/values of __dict__ of the instance
        """
        class_name = self.__class__.__name__
        formatted_created_at = self.created_at.isoformat()
        formatted_updated_at = self.updated_at.isoformat()

        attribute_dict = {
            "__class__": class_name,
            "id": self.id,
            "created_at": formatted_created_at,
            "updated_at": formatted_updated_at
        }

        attribute_dict.update(self.__dict__)  # add instance specific attribute

        return attribute_dict
