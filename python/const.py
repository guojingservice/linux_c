#!/bin/env python
#-*- coding: utf-8 -*-

import sys

class Const(object):
    class ConstError(TypeError): pass

    def __setattr__(self, key, value):
        if self.__dict__.has_key(key):
            raise self.ConstError, "Changing const.%s" % key
        else:
            self.__dict__[key] = value
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        else:
            return None

sys.modules[__name__] = Const()
