class Age:
    def __get__(self, obj, objtype):
        return obj._age
    
    def __set__(self, obj, value):
        if value < 0:
            raise ValueError("Age cannot be negative")
        obj.age = value
        
        
class Person:
    age = Age()