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


class BehaviorTests(unittest.TestCase):

    def test_eq(self):
        obj1 = Traverser({'item': 'value'})
        obj2 = Traverser({'item': 'value'})
        self.assertEqual(obj1, obj2)
        obj2.item = 'foo'
        self.assertNotEqual(obj1, obj2)

    def test_iter(self):
        list_obj = Traverser([123, [456, 789]])
        self.assertEqual(list(list_obj), [123, Traverser([456, 789])])
        singleton = Traverser({'item': 'value'})
        self.assertEqual(list(singleton), [singleton])

    def test_contains(self):
        list_obj = Traverser([123, [456, 789]])
        self.assertTrue(123 in list_obj)
        self.assertTrue([456, 789] in list_obj)
        self.assertTrue(Traverser([456, 789]) in list_obj)
        self.assertFalse(456 in list_obj)

    def test_len(self):
        self.assertEqual(len(Traverser([123, [456, 789]])), 2)
        self.assertEqual(len(Traverser([])), 0)
        self.assertEqual(len(Traverser({})), 1)

    def test_bool(self):
        self.assertTrue(Traverser([123]))
        self.assertFalse(Traverser([]))
        self.assertTrue(Traverser({}))

    def test_add(self):
        obj = Traverser([{'username': 'jdoe'}])
        sum = obj + {'username': 'any'}
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])
        sum = obj + Traverser({'username': 'any'})
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])

        obj = Traverser({'username': 'jdoe'})
        sum = obj + {'username': 'any'}
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])
        sum = obj + Traverser({'username': 'any'})
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])


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

    def test_append(self):
        obj = Traverser([{'username': 'jdoe'}])
        obj.append({'username': 'any'})
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser([{'username': 'jdoe'}])
        obj.append(Traverser({'username': 'any'}))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])

        obj = Traverser({'username': 'jdoe'})
        obj.append({'username': 'any'})
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser({'username': 'jdoe'})
        obj.append(Traverser({'username': 'any'}))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])

    def test_extend(self):
        obj = Traverser([{'username': 'jdoe'}])
        obj.extend([{'username': 'any'}])
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser([{'username': 'jdoe'}])
        obj.extend(Traverser([{'username': 'any'}]))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])

        obj = Traverser({'username': 'jdoe'})
        obj.extend([{'username': 'any'}])
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser({'username': 'jdoe'})
        obj.extend(Traverser([{'username': 'any'}]))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])


if __name__ == '__main__':
    unittest.main()
