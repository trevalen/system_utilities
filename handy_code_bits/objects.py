#! /usr/bin/env python


import re


class DottedDict(dict):
    '''
    Override for the dict object to allow referencing of keys as attributes, i.e. dict.key
    '''
    def __init__(self, *args, **kwargs):
        super(DottedDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    if isinstance(value, dict):
                        value = DottedDict(**value)
                    self[key] = value

        if kwargs:
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    value = DottedDict(**value)
                self[key] = value

        # Catch for case of importing values in the .items() format
        if self.items() and not self.__dict__.items():
            for key, value in self.items():
                self.__setitem__(key, value)

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        # Do this to match python default behavior
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, key, value):
        if self._is_valid_identifier_(key):
            self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if self._is_valid_identifier_(key):
            super(DottedDict, self).__setitem__(key, value)
            self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DottedDict, self).__delitem__(key)
        del self.__dict__[key]

    def _is_valid_identifier_(self, identifier):
        '''
        Test the key name for valid identifier status as considered by the python lexer.
        https://stackoverflow.com/questions/10120295/valid-characters-in-a-python-class-name
        '''
        python_keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
            'while', 'with', 'yield'
        ]
        if identifier not in python_keywords and re.match('[a-zA-Z_][a-zA-Z0-9_]*', identifier):
            return True
        raise SyntaxError('Key name is not a valid identifier or is reserved keyword.')


class DynamicObject(object):
    '''
    self._properties declared in derived class __init__ allows support for the lazy loading of
    properties on the class as needed instead of full execution to populate properties on class
    init. Will perform auto discovery for propeties using a _get_{property} naming scheme,
    otherwise must prove a mapping in the _properties dict to the setter function.

    self._properties is now a required dict in all __init__ methods of derived classes.
    '''

    def __getattr__(self, name):
        '''
        Override of default property lookup to implement dynamic property loading.
        '''
        if name[0] == '_':
            return self.__getattribute__(name)

        # Check the class properties map for a redirect of a property
        if name in self._properties:
            return self._map_property(name)

        # Auto discover a _get_{property} function and use this to populate property
        target_function_name = '_get_{0}'.format(name)
        if hasattr(self, target_function_name):
            return getattr(self, target_function_name)()

        raise AttributeError(
            '{0} is not a valid property of {1}'.format(name, self.__class__.__name__)
        )

    def _map_property(self, name):
        '''
        Check for existence of property of class, it not present, look it up in the _properties
        dict and exec the mapped functionality for the property.
        '''
        if name not in self.__dict__:
            result = self._properties[name]()
            self.__dict__[name] = result
        return getattr(self, name)
