#!/usr/bin/python3
"""Review model"""

from models.base_model import BaseModel


class Review(BaseModel):
    """class Review inherits from BaseModel"""
    place_id = ""
    user_id = ""
    text = ""
