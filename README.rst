Make Integration Tests Easier
=============================

testinstances is a set of managed instance wrappers to make integration testing with redis and mongodb easier. If you
have the binaries on your path, it can handle creating and destroying sandboxed instances for you to test with.

Examples
--------

The API is straightforward and easily embedeed in setup/teardown functions. It also automatically returns a connection
to the instance.:

::

    import unittest

    from testinstances import RedisInstance

    class TestSomeJunk(unittest.TestCase):
      def setUp(self):
        # Set up an instance on port 12345
        self.redis = RedisInstance(12345)

      def tearDown(self):
        self.redis.terminate()

      def test_stuff(self):
        self.redis.conn.set('foo', 'bar')
        self.assertEqual(self.redis.conn.get('foo'), 'bar')

Or, if you wanted to be fancy and avoid the process creation/termination cost for every test case:

::

    import unittest

    from testinstances import MongoInstance

    class TestSomeJunk(unittest.TestCase):
      @classmethod
      def setUpClass(cls):
        # Set up an instance on port 12345
        cls.mongo = MongoInstance(12345)

      @classmethod
      def tearDownClass(cls):
        cls.mongo.terminate()

      def setUp(self):
        # All instance types implement ``flush``
        self.mongo.flush()

      def test_stuff(self):
        collection = self.mongo.conn['someDB']['someCollection']
        collection.insert({'foo': 'bar'})
        self.assertEqual(collection.find({'foo': 'bar'}).next()['foo'], 'bar')

Roadmap
-------

* New Instance Kinds

  * Kafka
  * Zookeeper

* Documentation and ReadTheDocs

* Travis-CI
