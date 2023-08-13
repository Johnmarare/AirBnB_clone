#!/usr/bin/python3
"""Unittests for Amenity class"""

import unittest
import models
from models.amenity import Amenity
from datetime import datetime
from time import sleep
import os


class Test_Amenity(unittest.TestCase):
    """Test casess for Amenity class"""

    def setUp(self):
        """Set up the env before each test case"""
        self.amenity = Amenity()

    def tearDown(self):
        """Clean up the test env after each test case if needed"""
        self.amenity = None

    def test_init_with_arguments(self):
        """Test initialization with arguments"""
        data = {
            'id': '123',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00',
            'name': 'Test'
        }
        self.amenity = Amenity(**data)

        # Verify that the attributes are set correctly
        self.assertEqual(self.amenity.id, '123')
        self.assertEqual(self.amenity.created_at,
                         datetime.fromisoformat('2023-01-01T00:00:00'))
        self.assertEqual(self.amenity.updated_at,
                         datetime.fromisoformat('2023-01-01T00:00:00'))
        self.assertEqual(self.amenity.name, 'Test')

    def test_init_without_arguments(self):
        """Test initialization without arguments"""
        self.amenity = Amenity()

        # Verify that the attributes are set correctly
        self.assertIsNotNone(self.amenity.id)
        self.assertIsNotNone(self.amenity.created_at)
        self.assertIsNotNone(self.amenity.updated_at)
        self.assertEqual(self.amenity.created_at, self.amenity.updated_at)

    def test_args(self):
        """Testing args which was unused"""
        am = Amenity(None)
        self.assertNotIn(None, am.__dict__.values())

    def test_with_kwargs(self):
        """Testing with kwargs"""
        date = datetime.now()
        tform = date.isoformat()
        am = Amenity(id="123", created_at=tform, updated_at=tform)
        self.assertEqual(am.id, "123")
        self.assertEqual(am.created_at, date)
        self.assertEqual(am.updated_at, date)

    def test_kwargs_None(self):
        """Testing with kwargs at None"""
        with self.assertRaises(TypeError):
            Amenity(id=None, created_at=None, updated_at=None)

    def test_with_args_and_kwargs(self):
        """ testing with both args and kwargs"""
        date = datetime.now()
        tform = date.isoformat()
        am = Amenity(id="123", created_at=tform, updated_at=tform)
        self.assertEqual(am.id, "123")
        self.assertEqual(am.created_at, date)
        self.assertEqual(am.updated_at, date)

    def test_attrubutes_initialization(self):
        """tests initialization of attributes"""
        self.assertEqual(self.amenity.name, "")
        self.assertTrue(hasattr(self.amenity, "id"))
        self.assertTrue(hasattr(self.amenity, "created_at"))
        self.assertTrue(hasattr(self.amenity, "updated_at"))

    def test_id_is_str(self):
        """checks the id data type"""
        self.assertEqual(str, type(Amenity().id))

    def test_id_is_unique(self):
        """test if ids generated are unique"""
        user1 = Amenity()
        user2 = Amenity()
        self.assertNotEqual(user1.id, user2.id)

    def test_created_at_datetime(self):
        """Checks if the attribute is a datetime object"""
        self.assertEqual(datetime, type(Amenity().created_at))

    def test_created_at_timestamp(self):
        """checks if the timestamp is different"""
        user1 = Amenity()
        sleep(0.05)
        user2 = Amenity()
        self.assertLess(user1.created_at, user2.created_at)

    def test_updated_at_datetime(self):
        """Checks if attribute is a datetime object"""
        self.assertEqual(datetime, type(Amenity(). updated_at))

    def test_updated_at_timestamp(self):
        """Checks if the timestamp is different"""
        user1 = Amenity()
        sleep(0.05)
        user2 = Amenity()
        self.assertLess(user1.updated_at, user2.updated_at)

    def test_instance_storage(self):
        """checks if storage and retrival were successful"""
        self.assertIn(Amenity(), models.storage.all().values())

    def test__str__(self):
        """tests the string representation"""
        am1 = Amenity()
        am2 = Amenity()
        self.assertNotEqual(am1.__str__(), am2.__str__())

    def test_str_method(self):
        """tests the str method"""
        amenity_string = str(self.amenity)
        self.assertIn("[Amenity]", amenity_string)
        self.assertIn("id", amenity_string)
        self.assertIn("created_at", amenity_string)
        self.assertIn("updated_at", amenity_string)

    def test_save(self):
        """tests the effectivity of timestamp updates"""
        am = Amenity()
        sleep(0.1)
        update = am.updated_at
        am.save()
        self.assertLess(update, am.updated_at)

    def test_two_saves(self):
        """tests the effectivity of different timestamps updates"""
        am = Amenity()
        sleep(0.1)
        upadte1 = am.updated_at
        am.save()
        update2 = am.updated_at
        self.assertLess(upadte1, update2)
        sleep(0.1)
        am.save()
        self.assertLess(update2, am.updated_at)

    def test_save_updates_file(self):
        """check that updates are updated and stored correctly"""
        am = Amenity()
        am.save()
        amid = "Amenity." + am.id
        with open("file.json", "r") as file:
            self.assertIn(amid, file.read())

    def test_save_method(self):
        """tests the save method"""
        updated_at_1 = self.amenity.updated_at
        self.amenity.save()
        updated_at_2 = self.amenity.updated_at
        self.assertNotEqual(updated_at_1, updated_at_2)

    def test_to_dict(self):
        """Tests the expected output"""
        expected_dict = {
            'id': self.amenity.id,
            'created_at': self.amenity.created_at.isoformat(),
            'updated_at': self.amenity.updated_at.isoformat(),
            '__class__': 'Amenity'
        }
        self.assertEqual(self.amenity.to_dict(), expected_dict)

    def test_to_dict_type(self):
        """verifys the class returns a dictionary"""
        am = Amenity()
        self.assertTrue(dict, type(am.to_dict()))

    def test_different_to_dict(self):
        """check that the class produces 2 diff dict for diff instances"""
        am1 = Amenity()
        sleep(0.05)
        am2 = Amenity()
        self.assertNotEqual(am1.to_dict(), am2.to_dict())

    def test_to_dict_has_correct_keys(self):
        """check that the dict contains the right keys"""
        am = Amenity()
        self.assertIn("id", am.to_dict())
        self.assertIn("__class__", am.to_dict())
        self.assertIn("created_at", am.to_dict())
        self.assertIn("updated_at", am.to_dict())

    def test_to_dict_created_at_format(self):
        """checks the ISO formatted string"""
        am = self.amenity.to_dict()
        created_at = am["created_at"]
        self.assertEqual(created_at, self.amenity.created_at.isoformat())

    def test_to_dict_updated_at_format(self):
        """checks the ISO formatted string"""
        am = self.amenity.to_dict()
        updated_at = am["updated_at"]
        self.assertEqual(updated_at, self.amenity.updated_at.isoformat())


if __name__ == "__main__":
    unittest.main()
