import unittest
from books_and_readers.main import BRDatabase


def fun(x):
    return x + 1


class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(fun(3), 4)

    def test_DB(self):
        self.assertEqual(fun(4), 5)
