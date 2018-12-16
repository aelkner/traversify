import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from traversify import Traverser, Comparator


class MockResponse(object):
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


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

    def test_response_object_with_json_method(self):
        obj = Traverser(MockResponse('[]'))
        self.assertEqual(obj, [])


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

    def test_traversal_to_traverser_node(self):
        obj = Traverser({'item': {'key': 'value'}})
        self.assertEqual(obj.item, {'key': 'value'})
        self.assertEqual(obj.item.__class__.__name__, 'Traverser')
        self.assertEqual(obj.__dict__['item'], {'key': 'value'})
        self.assertEqual(obj.__dict__['item'].__class__.__name__, 'Traverser')


class BehaviorTests(unittest.TestCase):

    def test_ide_support(self):
        obj = Traverser({'item': 'value', 'item_list': [1, 2]})
        self.assertEqual(obj.__dict__['item'], 'value')
        self.assertEqual(obj.item, 'value')
        self.assertEqual(obj.__dict__['item_list'], [1, 2])
        self.assertEqual(obj.__dict__['item_list'].__class__.__name__, 'Traverser')
        self.assertEqual(obj.item_list, [1, 2])
        self.assertEqual(obj.item_list.__class__.__name__, 'Traverser')
        obj.new_list = [3, 4]
        self.assertEqual(obj.__dict__['new_list'], [3, 4])
        self.assertEqual(obj.__dict__['new_list'].__class__.__name__, 'Traverser')
        self.assertEqual(obj.new_list, [3, 4])
        self.assertEqual(obj.new_list.__class__.__name__, 'Traverser')

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

    def test_add_to_singleton(self):
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

    def test_setitem_updates_attributes_dict_correctly(self):
        obj = Traverser({})
        obj.new_attr = 'orig_value'
        self.assertEqual(obj.new_attr, 'orig_value')
        obj.new_attr = 'new_value'
        self.assertEqual(obj.new_attr, 'new_value')

    def test_setitem_needing_recursive_unwrap(self):
        obj = Traverser({})
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

    def test_append_to_singleton(self):
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

    def test_extend_singleton(self):
        obj = Traverser({'username': 'jdoe'})
        obj.extend([{'username': 'any'}])
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser({'username': 'jdoe'})
        obj.extend(Traverser([{'username': 'any'}]))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])


class ComparatorTests(unittest.TestCase):

    def test_blacklist(self):
        id_comparator = Comparator(blacklist='id')
        left = {'id': 1, 'username': 'jdoe'}
        right = {'username': 'jdoe'}
        self.assertTrue(id_comparator(left, right))
        self.assertTrue(id_comparator(Traverser(left), Traverser(right)))

    def test_whitelist(self):
        username_comparator = Comparator(whitelist='username')
        left = {'id': 1, 'username': 'jdoe'}
        right = {'username': 'jdoe'}
        self.assertTrue(username_comparator(left, right))
        self.assertTrue(username_comparator(Traverser(left), Traverser(right)))

    def test_eq_with_comparator(self):
        id_comparator = Comparator(blacklist='id')
        left = Traverser({'id': 1, 'username': 'jdoe'}, comparator=id_comparator)
        right = Traverser({'username': 'jdoe'})
        self.assertTrue(left == right)
        self.assertFalse(right == left)

    def test_prune(self):
        id_comparator = Comparator(blacklist='id')
        obj = {'id': 1, 'username': 'jdoe'}
        id_comparator.prune(obj)
        self.assertTrue(obj == {'username': 'jdoe'})

    def test_traverser_prune_no_comparator(self):
        obj = Traverser({'id': 1, 'username': 'jdoe'})
        obj.prune()
        self.assertTrue(obj() == {'id': 1, 'username': 'jdoe'})

    def test_traverser_prune_with_comparator(self):
        id_comparator = Comparator(blacklist='id')
        obj = Traverser({'id': 1, 'username': 'jdoe'}, comparator=id_comparator)
        obj.prune()
        self.assertTrue(obj() == {'username': 'jdoe'})


if __name__ == '__main__':
    unittest.main()
