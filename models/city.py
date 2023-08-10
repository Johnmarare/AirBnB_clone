#!/usr/bin/python3
"""Write a class city that inherits from BaseModel"""

from models.base_model import BaseModel


class City(BaseModel):
    """City class is a subclass(child) of BaseModel"""
    state_id = ""
    name = ""
