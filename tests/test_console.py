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

    def test_11_update_default_attr(self):
        """test update cmd on existing attribute"""
        self.c.onecmd('create Place')
        objid = self.out.getvalue()[:-1]
        self.clearIO()
        self.assertFalse(
            self.c.onecmd('update Place ' + objid +
                          ' name  "San Francisco"'))
        self.c.onecmd('all Place')
        self.assertTrue("'name': 'San Francisco'" in self.out.getvalue())
        self.clearIO()
        self.assertFalse(
            self.c.onecmd('update Place ' + objid +
                          ' latitude  "90.0"'))
        self.c.onecmd('all Place')
        self.assertTrue("'latitude': 90.0" in self.out.getvalue())
        self.clearIO()
        self.assertFalse(
            self.c.onecmd('update Place ' + objid +
                          ' max_guest  "5"'))
        self.c.onecmd('all Place')
        self.assertTrue("'max_guest': 5" in self.out.getvalue())
        self.clearIO()

    def test_12_update_too_many_arg(self):
        """test update cmd on too many arguments"""
        self.c.onecmd('create BaseModel')
        objid = self.out.getvalue()[:-1]
        self.clearIO()
        self.assertFalse(
            self.c.onecmd('update BaseModel ' + objid + ' age  "16"' +
                          'number "15.0"'))
        self.c.onecmd('all BaseModel')
        self.assertTrue("'number': 16.0" not in self.out.getvalue())
        self.clearIO()

    def test_13_show_fail(self):
        """test show fail"""
        self.c.onecmd('create BaseModel')
        bmid = self.out.getvalue()[:-1]
        self.c.onecmd('create BaseModel')
        self.clearIO()
        self.c.onecmd('create User')
        usid = self.out.getvalue()[:-1]
        self.clearIO()
        self.assertFalse(self.c.onecmd('show'))
        self.assertEqual("** class name missing **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('show something'))
        self.assertEqual("** instance id missing **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('show something someid'))
        self.assertEqual("** class doesn't exist **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('show BaseModel 1234'))
        self.assertEqual("** no instance found **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('show BaseModel ' + usid))
        self.assertEqual("** no instance found **\n", self.out.getvalue())
        self.clearIO()

    def test_14_show_success(self):
        """test show success"""
        self.c.onecmd('create BaseModel')
        bmid = self.out.getvalue()[:-1]
        self.c.onecmd('create BaseModel')
        self.clearIO()
        self.c.onecmd('create User')
        usid = self.out.getvalue()[:-1]
        self.clearIO()
        self.assertFalse(self.c.onecmd('show BaseModel ' + bmid))
        self.assertTrue(bmid in self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('show User ' + usid))
        self.assertTrue(usid in self.out.getvalue())
        self.clearIO()

    def test_15_destroy_fail(self):
        """test destroy fail"""
        self.c.onecmd('create BaseModel')
        bmid = self.out.getvalue()[:-1]
        self.c.onecmd('create BaseModel')
        self.clearIO()
        self.c.onecmd('create User')
        usid = self.out.getvalue()[:-1]
        self.clearIO()
        self.assertFalse(self.c.onecmd('destroy'))
        self.assertEqual("** class name missing **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('destroy something'))
        self.assertEqual("** instance id missing **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('destroy something someid'))
        self.assertEqual("** class doesn't exist **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('destroy BaseModel 1234'))
        self.assertEqual("** no instance found **\n", self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('destroy BaseModel ' + usid))
        self.assertEqual("** no instance found **\n", self.out.getvalue())
        self.clearIO()

    def test_16_destroy_success(self):
        """test destroy success cases"""
        self.c.onecmd('create BaseModel')
        bmid = self.out.getvalue()[:-1]
        self.c.onecmd('create BaseModel')
        self.clearIO()
        self.c.onecmd('create User')
        usid = self.out.getvalue()[:-1]
        self.clearIO()
        self.assertFalse(self.c.onecmd('destroy BaseModel ' + bmid))
        self.c.onecmd('all BaseModel')
        self.assertFalse(bmid in self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('destroy User ' + usid))
        self.assertFalse(usid in self.out.getvalue())
        self.clearIO()

    def test_51_method_fail_simple(self):
        '''test call method fail'''
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.'))
        self.assertEqual('*** Unknown syntax: BaseModel.\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.x'))
        self.assertEqual('*** Unknown syntax: BaseModel.x\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.y()'))
        self.assertEqual('*** Unknown syntax: BaseModel.y()\n',
                         self.out.getvalue())
        self.clearIO()

    def test_52_method_all_success(self):
        '''test call method all success'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.all()'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(ln, list)
        self.assertEqual(len(ln), 2)
        for e in ln:
            self.assertIsInstance(e, str)
            self.assertTrue(self.checkObjStrType(e, 'BaseModel'))
        self.assertFalse(self.c.onecmd('User.all()'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(ln, list)
        self.assertEqual(len(ln), 1)
        for e in ln:
            self.assertIsInstance(e, str)
            self.assertTrue(self.checkObjStrType(e, 'User'))
        self.assertFalse(self.c.onecmd('Amenity.all()'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertEqual(ln, [])

    def test_53_method_all_fail(self):
        '''test call method all failure'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('Amenity.all'))
        self.assertEqual('*** Unknown syntax: Amenity.all\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('A.all()'))
        self.assertEqual('*** Unknown syntax: A.all()\n',
                         self.out.getvalue())
        self.clearIO()

    def test_54_method_count(self):
        '''test call method count'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.count()'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertEqual(ln, 2)
        self.assertFalse(self.c.onecmd('User.count()'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertEqual(ln, 1)
        self.assertFalse(self.c.onecmd('Amenity.count()'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertEqual(ln, 0)
        self.assertFalse(self.c.onecmd('BaseModel.count("a")'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertEqual(ln, 2)
        self.assertFalse(self.c.onecmd('BaseModel.count(3)'))
        ln = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertEqual(ln, 2)

    def test_55_method_count_fail(self):
        '''test call method count fail'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('Amenity.count'))
        self.assertEqual('*** Unknown syntax: Amenity.count\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('A.count()'))
        self.assertEqual('*** Unknown syntax: A.count()\n',
                         self.out.getvalue())
        self.clearIO()

    def test_56_method_show_success(self):
        '''test call method show success'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.all()'))
        output = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('User.all()'))
        output += json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(output[0], str)
        self.assertTrue(self.checkObjStrType(output[0], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[1], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[2], 'User'))
        lst = [['BaseModel', output[0].split(' ', 2)[1][1:-1]],
               ['BaseModel', output[1].split(' ', 2)[1][1:-1]],
               ['User', output[2].split(' ', 2)[1][1:-1]]]
        for e in lst:
            testcmd = e[0] + '.show(' + e[1] + ')'
            self.assertFalse(self.c.onecmd(testcmd))
            ln = self.out.getvalue()
            self.clearIO()
            self.assertTrue(self.checkObjStrType(ln, e[0]))

    def test_57_method_show_failure(self):
        '''test call method show failure'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('Amenity.show'))
        self.assertEqual('*** Unknown syntax: Amenity.show\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('A.show()'))
        self.assertEqual('*** Unknown syntax: A.show()\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.show("1234")'))
        self.assertEqual('** no instance found **\n',
                         self.out.getvalue())
        self.clearIO()

    def test_58_method_destroy_success(self):
        '''test call method destroy success'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.all()'))
        output = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('User.all()'))
        output += json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(output[0], str)
        self.assertTrue(self.checkObjStrType(output[0], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[1], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[2], 'User'))
        lst = [['BaseModel', output[0].split(' ', 2)[1][1:-1]],
               ['BaseModel', output[1].split(' ', 2)[1][1:-1]],
               ['User', output[2].split(' ', 2)[1][1:-1]]]
        for e in lst:
            testcmd = e[0] + '.destroy(' + e[1] + ')'
            self.assertFalse(self.c.onecmd(testcmd))
            ln = self.out.getvalue()
            self.clearIO()

    def test_59_method_destroy_failure(self):
        '''test call method destroy failure'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('Amenity.destroy'))
        self.assertEqual('*** Unknown syntax: Amenity.destroy\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('A.destroy()'))
        self.assertEqual('*** Unknown syntax: A.destroy()\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.destroy("1234")'))
        self.assertEqual('** no instance found **\n',
                         self.out.getvalue())
        self.clearIO()

    def test_60_method_upd_attr_success(self):
        '''test call method upd attr success'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.all()'))
        output = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('User.all()'))
        output += json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(output[0], str)
        self.assertTrue(self.checkObjStrType(output[0], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[1], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[2], 'User'))
        lst = [['BaseModel', output[0].split(' ', 2)[1][1:-1]],
               ['BaseModel', output[1].split(' ', 2)[1][1:-1]],
               ['User', output[2].split(' ', 2)[1][1:-1]]]
        for e in lst:
            testcmd = e[0] + '.update(' + e[1] + ', "test", "test")'
            self.assertFalse(self.c.onecmd(testcmd))
            ln = self.out.getvalue()
            self.clearIO()

    def test_61_method_upd_attr_failure(self):
        '''test call method upd attr failure'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('Amenity.update'))
        self.assertEqual('*** Unknown syntax: Amenity.update\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('A.update()'))
        self.assertEqual('*** Unknown syntax: A.update()\n',
                         self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd(
            'BaseModel.update("1234-1234", "test", "test")'))
        self.assertEqual('** no instance found **\n',
                         self.out.getvalue())
        self.clearIO()

    def test_62_method_upd_dict_success(self):
        '''test call method upd dict success'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd('BaseModel.all()'))
        output = json.loads(self.out.getvalue())
        self.clearIO()
        self.assertFalse(self.c.onecmd('User.all()'))
        output += json.loads(self.out.getvalue())
        self.clearIO()
        self.assertIsInstance(output[0], str)
        self.assertTrue(self.checkObjStrType(output[0], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[1], 'BaseModel'))
        self.assertIsInstance(output[1], str)
        self.assertTrue(self.checkObjStrType(output[2], 'User'))
        lst = [['BaseModel', output[0].split(' ', 2)[1][1:-1]],
               ['BaseModel', output[1].split(' ', 2)[1][1:-1]],
               ['User', output[2].split(' ', 2)[1][1:-1]]]
        for e in lst:
            testcmd = e[0] + '.update(' + e[1] + ", {'test': 'test'})"
            self.assertFalse(self.c.onecmd(testcmd))
            ln = self.out.getvalue()
            self.clearIO()

    def test_63_method_upd_dict_failure(self):
        '''test call method upd dict failure'''
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create BaseModel'))
        self.assertFalse(self.c.onecmd('create User'))
        self.clearIO()
        self.assertFalse(self.c.onecmd(
            'BaseModel.update("1234-1234", {"test", "test"})'))
        self.assertEqual('** no instance found **\n',
                         self.out.getvalue())
        self.clearIO()

    @staticmethod
    def checkObjStrType(e, t):
        """check if e is a string representation of type 't'"""
        return (e[e.find('['): e.find(']') + 1] == '[' + t + ']')


if __name__ == '__main__':
    unittest.main()
