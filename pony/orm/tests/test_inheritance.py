from __future__ import absolute_import, print_function, division

import unittest

from pony.orm.core import *
from pony.orm.tests.testutils import *

class TestInheritance(unittest.TestCase):

    def test_0(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            id = PrimaryKey(int)

        self.assertTrue(Entity1._root_ is Entity1)
        self.assertEqual(Entity1._discriminator_attr_, None)
        self.assertEqual(Entity1._discriminator_, None)

    def test_1(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            id = PrimaryKey(int)
        class Entity2(Entity1):
            a = Required(int)
        class Entity3(Entity1):
            b = Required(int)
        class Entity4(Entity2, Entity3):
            c = Required(int)

        self.assertTrue(Entity1._root_ is Entity1)
        self.assertTrue(Entity2._root_ is Entity1)
        self.assertTrue(Entity3._root_ is Entity1)
        self.assertTrue(Entity4._root_ is Entity1)
        self.assertTrue(Entity1._discriminator_attr_ is Entity1.classtype)
        self.assertTrue(Entity2._discriminator_attr_ is Entity1._discriminator_attr_)
        self.assertTrue(Entity3._discriminator_attr_ is Entity1._discriminator_attr_)
        self.assertTrue(Entity4._discriminator_attr_ is Entity1._discriminator_attr_)
        self.assertEqual(Entity1._discriminator_, 'Entity1')
        self.assertEqual(Entity2._discriminator_, 'Entity2')
        self.assertEqual(Entity3._discriminator_, 'Entity3')
        self.assertEqual(Entity4._discriminator_, 'Entity4')
        
    @raises_exception(ERDiagramError, "Multiple inheritance graph must be diamond-like. "
        "Entity Entity3 inherits from Entity1 and Entity2 entities which don't have common base class.")
    def test_2(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = PrimaryKey(int)
        class Entity2(db.Entity):
            b = PrimaryKey(int)
        class Entity3(Entity1, Entity2):
            c = Required(int)

    @raises_exception(ERDiagramError, 'Attribute "Entity2.a" clashes with attribute "Entity3.a" in derived entity "Entity4"')
    def test_3(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            id = PrimaryKey(int)
        class Entity2(Entity1):
            a = Required(int)
        class Entity3(Entity1):
            a = Required(int)
        class Entity4(Entity2, Entity3):
            c = Required(int)

    @raises_exception(ERDiagramError, "Name 'a' hides base attribute Entity1.a")
    def test_4(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            id = PrimaryKey(int)
            a = Required(int)
        class Entity2(Entity1):
            a = Required(int)

    @raises_exception(ERDiagramError, "Primary key cannot be redefined in derived classes")
    def test_5(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = PrimaryKey(int)
        class Entity2(Entity1):
            b = PrimaryKey(int)

    def test_6(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = Discriminator(str)
            b = Required(int)
        class Entity2(Entity1):
            c = Required(int)
        
        self.assertTrue(Entity1._discriminator_attr_ is Entity1.a)
        self.assertTrue(Entity2._discriminator_attr_ is Entity1.a)

    @raises_exception(TypeError, "Discriminator value for entity Entity1 "
                                 "with custom discriminator column 'a' of 'int' type is not set")
    def test_7(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = Discriminator(int)
            b = Required(int)
        class Entity2(Entity1):
            c = Required(int)

    def test_8(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            _discriminator_ = 1
            a = Discriminator(int)
            b = Required(int)
        class Entity2(Entity1):
            _discriminator_ = 2
            c = Required(int)
        db.generate_mapping(create_tables=True)
        with db_session:
            x = Entity1(b=10)
            y = Entity2(b=10, c=20)
        with db_session:
            x = Entity1[1]
            y = Entity1[2]
            self.assertTrue(isinstance(x, Entity1))
            self.assertTrue(isinstance(y, Entity2))
            self.assertEqual(x.a, 1)
            self.assertEqual(y.a, 2)

    def test_9(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            _discriminator_ = '1'
            a = Discriminator(int)
            b = Required(int)
        class Entity2(Entity1):
            _discriminator_ = '2'
            c = Required(int)
        db.generate_mapping(create_tables=True)
        with db_session:
            x = Entity1(b=10)
            y = Entity2(b=10, c=20)
        with db_session:
            x = Entity1[1]
            y = Entity1[2]
            self.assertTrue(isinstance(x, Entity1))
            self.assertTrue(isinstance(y, Entity2))
            self.assertEqual(x.a, 1)
            self.assertEqual(y.a, 2)

    @raises_exception(TypeError, "Incorrect discriminator value is set for Entity2 attribute 'a' of 'int' type: 'zzz'")
    def test_10(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            _discriminator_ = 1
            a = Discriminator(int)
            b = Required(int)
        class Entity2(Entity1):
            _discriminator_ = 'zzz'
            c = Required(int)

    def test_11(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            _discriminator_ = 1
            a = Discriminator(int)
            b = Required(int)
            composite_index(a, b)

    @raises_exception(ERDiagramError, 'Invalid use of attribute Entity1.a in entity Entity2')
    def test_12(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = Required(int)
        class Entity2(db.Entity):
            b = Required(int)
            composite_index(Entity1.a, b)

    def test_13(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = Required(int)
        class Entity2(Entity1):
            b = Required(int)
            composite_index(Entity1.a, b)
        self.assertEqual([ index.attrs for index in Entity2._indexes_ ],
                          [ (Entity2.id,), (Entity2.a, Entity2.b) ])

    def test_14(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            d = Discriminator(str)
            a = Required(int)
        class Entity2(Entity1):
            b = Required(int)
            composite_index(Entity1.d, Entity1.a, b)
        self.assertEqual([ index.attrs for index in Entity2._indexes_ ],
                          [ (Entity2.id,), (Entity2.d, Entity2.a, Entity2.b) ])

    def test_15(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            d = Discriminator(str)
            a = Required(int)
        class Entity2(Entity1):
            b = Required(int)
            composite_index('d', 'id', 'a', 'b')
        self.assertEqual([ index.attrs for index in Entity2._indexes_ ],
                         [ (Entity2.id,), (Entity2.d, Entity2.id, Entity2.a, Entity2.b) ])

    def test_16(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = Required(int)
        class Entity2(Entity1):
            b = Required(int)
            composite_index('classtype', 'id', 'a', b)
        self.assertEqual([ index.attrs for index in Entity2._indexes_ ],
                         [ (Entity2.id,), (Entity2.classtype, Entity2.id, Entity2.a, Entity2.b) ])

    def test_17(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            t = Discriminator(str)
            a = Required(int)
            b = Required(int)
            composite_index(t, a, b)
        class Entity2(Entity1):
            c = Required(int)
        self.assertEqual([ index.attrs for index in Entity1._indexes_ ],
                         [ (Entity1.id,), (Entity1.t, Entity1.a, Entity1.b) ])

    def test_18(self):
        db = Database('sqlite', ':memory:')
        class Entity1(db.Entity):
            a = Required(int)
        class Entity2(db.Entity1):
            b = Required(int)
        class Entity3(Entity1):
            c = Required(int)
        db.generate_mapping(create_tables=True)
        with db_session:
            x = Entity1(a=10)
            y = Entity2(a=20, b=30)
            z = Entity3(a=40, c=50)
        with db_session:
            result = select(e for e in Entity1 if e.b == 30 or e.c == 50)
            self.assertEqual([ e.id for e in result ], [ 2, 3 ])

if __name__ == '__main__':
    unittest.main()
