class BlankClass(object):
    '''This is a Blank class for CS162.'''
    pass

t = BlankClass()

class ClassWithAttr(object):
    x1 = 1
    x2 = 2

my_attr = ClassWithAttr()
my_attr.x3 = 3

#help(t)
# Prints the class docstring and a summary of all inherited methods/attributes.
"""
class BlankClass(builtins.object)
    This is a Blank class for CS162.

    Data descriptors defined here:

    __dict__
        dictionary for instance variables
    __weakref__
"""

print(type(t))
# Returns the type (class) of the object.
# Output: <class '__main__.BlankClass'>

print(dir(t))
# Returns a list of all attributes and methods available on the object,
# including inherited dunder methods from object.
# Output: ['__class__', '__delattr__', '__dict__', ... '__weakref__']

print(hash(t))
# Returns the integer hash value of the object (based on its memory address by default).
# Output: 152230520635  (varies each run)

print(id(t))
# Returns the unique memory address of the object as an integer.
# Output: 2435688330160  (varies each run)

print(hasattr(my_attr, 'x3'))
# Checks whether the object has the named attribute. Returns True/False.
# Output: True  (x3 was added to my_attr above)

print(getattr(my_attr, 'x3'))
# Retrieves the value of the named attribute from the object.
# Output: 3

print(delattr(my_attr, 'x3'))
# Deletes the named attribute from the object. Returns None.
# Output: None

print(vars(my_attr))
# Returns the instance's __dict__ — only instance-level attributes (not class-level).
# x3 is instanse level-attribute x1/x2 are class attributes so they don't appear here.
# Output: {'x3': 3}

print(bool(t))
# Returns the boolean value of the object.
# Any object is True by default unless __bool__ or __len__ returns False/0.
# Output: True
