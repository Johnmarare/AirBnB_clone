#!/usr/bin/python3

import cmd


class HBNBCommand(cmd.Cmd):
    """defines a class called HBNBCommand
    that inherits from the cmd.Cmd class.
    """
    prompt = "(hbnb) "

    def do_quit(self, arg):
        """Quit command to exit the program"""
        return True

    def do_EOF(self, arg):
        """Exit the program using Ctrl+D"""
        print("")  # Print a new line before exiting
        return True

    def emptyline(self):
        """Do nothing on empty line"""
        pass


if __name__ == '__main__':
    HBNBCommand().cmdloop()
