
from math import pi

class Test(object):

    def __init__(self, hee_hee):
        self.hee_hee = hee_hee

    def Hee_hee(self):
        return (self.hee_hee * pi)

    def boop(self):
        print(self.Hee_hee())
hEe_hee = Test(1)
hEe_hee.boop()
