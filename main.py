class Student:
    def __init__(self, name):
        self.name = name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        try:
            self._name = name
        except Exception as e:
            print(e)
    def show(self):
        print(f"The student's name is {self.name}")

s1 = Student('Rajesh')
s1.show()
s1.name = 'Raju'
s1.show()