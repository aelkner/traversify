import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from traversify import Traverser


class ConstructorTests(unittest.TestCase):

    def test_invalid(self):
        with self.assertRaises(ValueError):
            Traverser(0)
        with self.assertRaises(ValueError):
            Traverser(0.0)
        with self.assertRaises(ValueError):
            Traverser("abc")

    def test_list(self):
        obj = Traverser([])
        self.assertEqual(obj(), [])

    def test_dict(self):
        obj = Traverser({})
        self.assertEqual(obj(), {})

    def test_json(self):
        obj = Traverser("[]")
        self.assertEqual(obj(), [])
        obj = Traverser("{}")
        self.assertEqual(obj(), {})


class TraversalTests(unittest.TestCase):

    def test_singleton(self):
        users = {'username': 'jdoe', 'display_name': 'John Doe'}
        obj = Traverser(users)
        self.assertIsNone(obj.invalid_key)
        self.assertEqual(obj.username, 'jdoe')
        self.assertEqual(obj[0].username, 'jdoe')
        self.assertEqual(obj['display_name'], 'John Doe')
        self.assertEqual(obj[0]['display_name'], 'John Doe')

    def test_ensure_list(self):
        obj = Traverser({'item': 'value'})
        self.assertIsNone(obj.ensure_list('invalid_key'))
        self.assertEqual(obj.ensure_list('item'), ['value'])
        obj = Traverser({'item': ['value']})
        self.assertEqual(obj.ensure_list('item')(), ['value'])


class UpdativeTests(unittest.TestCase):

    def test_setitem(self):
        users = {'username': 'jdoe', 'display_name': 'John Doe'}
        obj = Traverser(users)
        obj.set_to_none = None
        self.assertIsNone(obj.set_to_none)
        obj.id = 123
        self.assertEqual(obj.id, 123)
        obj.roles = ['admin', 'any_user']
        self.assertEqual(obj.roles(), ['admin', 'any_user'])
        obj.list_has_traverser = [Traverser([123]), 456]
        self.assertEqual(obj.list_has_traverser(), [[123], 456])
        obj.dict_has_traverser = {'has_traverser': Traverser([123]), 'no_traverser': 456}
        self.assertEqual(sorted(obj.dict_has_traverser().items()), [('has_traverser', [123]), ('no_traverser', 456)])


if __name__ == '__main__':
    unittest.main()
