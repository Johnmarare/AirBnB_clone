#!/usr/bin/python3
'''Test Console Module'''

from console import HBNBCommand
from unittest.mock import create_autospec
from uuid import UUID
import models
import unittest
import pycodestyle
import sys
import io
import json
from os import remove
from os.path import isfile
from models.base_model import BaseModel
from datetime import datetime
from io import StringIO


class Test_01_Basic(unittest.TestCase):
    '''Test Console Basic'''

    def setUp(self):
        self.mock_stdin = create_autospec(sys.stdin)
        self.mock_stdout = create_autospec(sys.stdout)
        self.out = StringIO()
        sys.stdout = self.out
        self.c = self.create()
        models.storage._FileStorage__objects.clear()

    def teardown(self):
        sys.stdout = sys.__stdout__
        try:
            remove('file.json')
        except FileNotFoundError:
            pass
        models.storage._FileStorage__objects.clear()
        self.clearIO()

    def clearIO(self):
        self.out.truncate(0)
        self.out.seek(0)

    def create(self, server=None):
        """create console instance"""
        return HBNBCommand(stdin=self.mock_stdin, stdout=self.mock_stdout)

    def _last_write(self, nr=None):
        """:return: last `n` output lines"""
        if nr is None:
            return self.mock_stdout.write.call_args[0][0]
        return "".join(map(lambda c: c[0][0],
                           self.mock_stdout.write.call_args_list[-nr:]))

    def test_01_noinput(self):
        self.assertFalse(self.c.onecmd("\n"))
        self.assertEqual('', self.out.getvalue())

    def test_02_quit(self):
        """test quit command."""
        self.assertTrue(self.c.onecmd("quit"))
        self.assertTrue(self.c.onecmd("quit some random arguments"))
        self.assertFalse(self.c.onecmd("Quit"))
        self.assertEqual('*** Unknown syntax: Quit\n', self.out.getvalue())
        self.clearIO()

    def test_03_EOF(self):
        """test EOF"""
        self.assertTrue(self.c.onecmd("EOF"))
        self.assertFalse(self.c.onecmd("eof"))
        self.assertEqual('*** Unknown syntax: eof\n', self.out.getvalue())
        self.clearIO()

    def test_04_create_fail(self):
        """test create"""
        self.assertFalse(self.c.onecmd('create'))
        self.assertEqual('** class name missing **\n', self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('create someModel'))
        self.assertEqual("** class doesn't exist **\n", self.out.getvalue())
        self.clearIO()

    def test_05_creat_success(self):
        """test create success case
        check if output is a valid uuid"""
        self.assertFalse(self.c.onecmd('create BaseModel'))
        testuuid = self.out.getvalue()[:-1]
        uuid_obj = None
        testRes = False
        self.clearIO()
        try:
            uuid_obj = UUID(testuuid)
            testRes = str(uuid_obj) == testuuid
        except ValueError:
            testRes = False
        self.assertTrue(testRes)

    def test_06_all_no_arg(self):
        """test all command with no arg"""
        self.assertFalse(self.c.onecmd('all'))
        self.assertEqual('[]\n', self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('all'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(ln, list)
        self.assertEqual(len(ln), 1)
        for e in ln:
            self.assertIsInstance(e, str)
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.assertFalse(self.c.onecmd('create State'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('all'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(ln, list)
        self.assertEqual(len(ln), 4)
        for e in ln:
            self.assertIsInstance(e, str)

    def test_07_all_with_arg(self):
        """test all command with arg"""
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('all BaseModel'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(ln, list)
        self.assertEqual(len(ln), 2)
        for e in ln:
            self.assertIsInstance(e, str)
            self.assertTrue(self.checkObjStrType(e, 'BaseModel'))
        self.assertFalse(self.c.onecmd('all User'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(ln, list)
        self.assertEqual(len(ln), 1)
        for e in ln:
            self.assertIsInstance(e, str)
            self.assertTrue(self.checkObjStrType(e, 'User'))
        self.assertFalse(self.c.onecmd('all Amenity'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertEqual(ln, [])

    def test_08_update_not_enough_arg(self):
        """test update cmd fail on not enough arguments"""
        self.assertFalse(self.c.onecmd('update'))
        self.assertEqual('** class name missing **\n', self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('update something'))
        self.assertEqual("** instance id missing **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('update something someid'))
        self.assertEqual("** attribute name missing **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('update something someid someattr'))
        self.assertEqual("** value missing **\n", self.out.getvalue())

    def test_09_update_wrong_arg(self):
        """test update fail on wrong arg"""
        self.assertFalse(self.c.onecmd('update something someid atname atval'))
        self.assertEqual("** class doesn't exist **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('update BaseModel someid atname atval'))
        self.assertEqual("** no instance found **\n", self.out.getvalue())
        self.clearIO()

    def test_10_update_newattr(self):
        """test adding attribute to object"""
        self.c.onecmd('create BaseModel')
        objid = self.out.getvalue()[:-1]
        self.clearIO()
        self.assertFalse(
            self.c.onecmd('update BaseModel ' + objid +
                          ' first_name  "Betty"'))
        self.c.onecmd('all BaseModel')
        self.assertTrue("'first_name': 'Betty'" in self.out.getvalue())
        self.clearIO()
        self.assertFalse(
            self.c.onecmd('update BaseModel ' + objid + ' age  "16"'))
        self.c.onecmd('all BaseModel')
        self.assertTrue("'age': 16" in self.out.getvalue())
        self.clearIO()
        self.assertFalse(
            self.c.onecmd('update BaseModel ' + objid + ' number  "5.0"'))
        self.c.onecmd('all BaseModel')
        self.assertTrue("'number': 5.0" in self.out.getvalue())

if __name__ == '__main__':
    unittest.main()
