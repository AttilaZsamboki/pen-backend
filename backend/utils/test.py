# Python program to demonstrate
# inheritance in inner class


class A:
    def __init__(self, x):
        self.num = x

    def display(self):
        print('In Parent Class')

    # this is inner class


class Inner(A):
    def __init__(self):
        super().__init__("Hello")

    def display1(self):
        print('Inner Of Parent Class' + self.num)
        self.display()


# creating child class object
p = Inner()
p.display1()
