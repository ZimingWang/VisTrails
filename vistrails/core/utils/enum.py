############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""enum helps create enumeration classes.

"""

def enum(className, enumValues, doc = None):
    """enum(className: str, enumValues: [str], doc = None) -> class.
    Creates a new enumeration class. For example:

    >>> import enum
    >>> Colors = enum.enum('Colors',
                           ['Red', 'Green', 'Blue'],
                           "Enumeration of primary colors")

    will create a class that can be used as follows:

    >>> x = Colors.Red
    >>> y = Colors.Blue
    >>> x == y
    False
    >>> z = Colors.REd
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    AttributeError: type object 'Colors' has no attribute 'REd'
    >>> z = Colors.Red
    >>> z == x
    True
    >>> x.__doc__
    'Enumeration of primary colors'
    
    """                  
    def __init__(self, v):
        self.__v = v
        
    def str(v):
        return the_enum.st[v]
    
    def __str__(self):
        return the_enum.str(self.__v)
    
    def __repr__(self):
        return className + "." + the_enum.str(self.__v)
    
    def __eq__(self, other):
        try:
            return (self.__v == other.__v and 
                    self.__className == other.__className)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)
        
    the_enum = type(className, (object, ),
                   {'__init__': __init__,
                    'str': staticmethod(str),
                    '__str__': __str__,
                    '__repr__': __repr__,
                    'st': enumValues,
                    '__className': className,
                    '__eq__': __eq__,
                    '__doc__': doc})
    for (v, x) in zip(enumValues, range(len(enumValues))):
        setattr(the_enum, v, the_enum(x))
    return the_enum

################################################################################

import unittest

class TestEnum(unittest.TestCase):

    def test1(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertEquals(e1.v1, e1.v1)
        self.assertEquals(e1.v2, e1.v2)
        self.assertEquals(e1.v3, e1.v3)
        self.assertNotEquals(e1.v1, e1.v2)
        self.assertNotEquals(e1.v1, e1.v3)
        self.assertNotEquals(e1.v2, e1.v3)
        self.assertNotEquals(e1.v2, e1.v1)
        self.assertNotEquals(e1.v3, e1.v1)
        self.assertNotEquals(e1.v3, e1.v2)

    def test2(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        e2 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertEquals(e1.v1, e2.v1)

    def test3(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertNotEquals(e1.v1, 5)

if __name__ == '__main__':
    unittest.main()
