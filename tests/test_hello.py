import unittest

class TestHelloFeature(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual("Hello, World!", "Hello, World!")

    def test_hello_empty(self):
        self.assertEqual("Hello, ", "Hello, " + "")

    def test_hello_name(self):
        name = "Alice"
        self.assertEqual(f"Hello, {name}!", "Hello, Alice!")

if __name__ == '__main__':
    unittest.main()