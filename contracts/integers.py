from pyteal import *


# This is an example of an array of integer using bytes
def contract():
    return Int(1)


if __name__ == "__main__":
    print(compileTeal(contract(), Mode.Application, version=4))
