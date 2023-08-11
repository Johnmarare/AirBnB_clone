#!/usr/bin/python3

"""Defines the HBnB console"""

import cmd
import models
from models.base_model import BaseModel
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.user import User
from datetime import datetime
from shlex import shlex
"""entry point for hbnb console"""


class HBNBCommand(cmd.Cmd):
    """ hbnb shell """
    prompt = '(hbnb) '
    clslist = {'BaseModel': BaseModel, 'State': State, 'City': City,
               'Amenity': Amenity, 'Place': Place, 'Review': Review,
               'User': User}

    def emptyline(self):
        """empty line"""
        pass

    def do_create(self, clsname=None):
        """Creates a new instance of BaseModel, saves it and prints the id"""
        if not clsname:
            print('** class name missing **')
        elif not self.clslist.get(clsname):
            print('** class doesn\'t exist **')
        else:
            obj = self.clslist[clsname]()
            models.storage.save()
            print(obj.id)

    def do_show(self, arg):
        """Show instance based on id"""
        clsname, objid = None, None
        args = arg.split(' ')
        if len(args) > 0:
            clsname = args[0]
        if len(args) > 1:
            objid = args[1]
        if not clsname:
            print('** class name missing **')
        elif not objid:
            print('** instance id missing **')
        elif not self.clslist.get(clsname):
            print("** class doesn't exist **")
        else:
            k = clsname + "." + objid
            obj = models.storage.all().get(k)
            if not obj:
                print('** no instance found **')
            else:
                print(obj)

    def do_destroy(self, arg):
        """destroy instance based on id
        """
        clsname, objid = None, None
        args = arg.split(' ')
        if len(args) > 0:
            clsname = args[0]
        if len(args) > 1:
            objid = args[1]
        if not clsname:
            print('** class name missing **')
        elif not objid:
            print('** instance id missing **')
        elif not self.clslist.get(clsname):
            print("** class doesn't exist **")
        else:
            k = clsname + "." + objid
            obj = models.storage.all().get(k)
            if not obj:
                print('** no instance found **')
            else:
                del models.storage.all()[k]
                models.storage.save()

    def do_all(self, arg):
        """Prints all instances based or not on the class name
        """
        if not arg:
            print([str(v) for k, v in models.storage.all().items()])
        else:
            if not self.clslist.get(arg):
                print("** class doesn't exist **")
                return False
            print([str(v) for k, v in models.storage.all().items()
                   if type(v) is self.clslist.get(arg)])

    def do_update(self, arg):
        """Updates an instance based on the class name and id
        """
        clsname, objid, attrname, attrval = None, None, None, None
        updatetime = datetime.now()
        args = arg.split(' ', 3)
        if len(args) > 0:
            clsname = args[0]
        if len(args) > 1:
            objid = args[1]
        if len(args) > 2:
            attrname = args[2]
        if len(args) > 3:
            attrval = list(shlex(args[3]))[0].strip('"')
        if not clsname:
            print('** class name missing **')
        elif not objid:
            print('** instance id missing **')
        elif not attrname:
            print('** attribute name missing **')
        elif not attrval:
            print('** value missing **')
        elif not self.clslist.get(clsname):
            print("** class doesn't exist **")
        else:
            k = clsname + "." + objid
            obj = models.storage.all().get(k)
            if not obj:
                print('** no instance found **')
            else:
                if hasattr(obj, attrname):
                    attrval = type(getattr(obj, attrname))(attrval)
                else:
                    attrval = self.getType(attrval)(attrval)
                setattr(obj, attrname, attrval)
                obj.updated_at = updatetime
                models.storage.save()

    def do_quit(self, arg):
        """Quit command to exit the program
        """
        return True

    def do_EOF(self, arg):
        """EOF to exit the program
        """
        return True

    def default(self, line):
        """handle class commands"""
        ln = line.split('.', 1)
        if len(ln) < 2:
            print('*** Unknown syntax:', ln[0])
            return False
        clsname, line = ln[0], ln[1]
        if clsname not in list(self.clslist.keys()):
            print('*** Unknown syntax: {}.{}'.format(clsname, line))
            return False
        ln = line.split('(', 1)
        if len(ln) < 2:
            print('*** Unknown syntax: {}.{}'.format(clsname, ln[0]))
            return False
        mthname, args = ln[0], ln[1].rstrip(')')
        if mthname not in ['all', 'count', 'show', 'destroy', 'update']:
            print('*** Unknown syntax: {}.{}'.format(clsname, line))
            return False
        if mthname == 'all':
            self.do_all(clsname)
        elif mthname == 'count':
            print(self.count_class(clsname))
        elif mthname == 'show':
            self.do_show(clsname + " " + args.strip('"'))
        elif mthname == 'destroy':
            self.do_destroy(clsname + " " + args.strip('"'))
        elif mthname == 'update':
            lb, rb = args.find('{'), args.find('}')
            d = None
            if args[lb:rb + 1] != '':
                d = eval(args[lb:rb + 1])
            ln = args.split(',', 1)
            objid, args = ln[0].strip('"'), ln[1]
            if d and type(d) is dict:
                self.handle_dict(clsname, objid, d)
            else:
                from shlex import shlex
                args = args.replace(',', ' ', 1)
                ln = list(shlex(args))
                ln[0] = ln[0].strip('"')
                self.do_update(" ".join([clsname, objid, ln[0], ln[1]]))

    def handle_dict(self, clsname, objid, d):
        """handle dictionary update"""
        for k, v in d.items():
            self.do_update(" ".join([clsname, objid, str(k), str(v)]))

    def postloop(self):
        """print new line after each loop"""
        print()

    @staticmethod
    def count_class(clsname):
        """count number of objects of type clsname"""
        c = 0
        for k, v in models.storage.all().items():
            if type(v).__name__ == clsname:
                c += 1
        return (c)

    @staticmethod
    def getType(attrval):
        """return the type of the input string"""
        try:
            int(attrval)
            return (int)
        except ValueError:
            pass
        try:
            float(attrval)
            return (float)
        except ValueError:
            return (str)


if __name__ == "__main__":
    HBNBCommand().cmdloop()
