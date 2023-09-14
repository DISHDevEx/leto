from temporary_directory import TemporaryDirectory as td
from file import file as f

print("hi")


with td() as temp:
    f(temp)


