import mock
import unittest

from testinstances import managed_instance, MongoInstance
from testinstances.exceptions import ProcessNotStartingError

class MongoInstanceTests(unittest.TestCase):

    def tearDown(self):
        managed_instance._cleanup()

    def test_start_stop(self):
        """Test starting and stopping an instance"""
        instance = MongoInstance(10101)
        self.assertTrue(instance.conn.alive())

        instance.terminate()
        self.assertFalse(instance.conn.alive())

    @mock.patch('testinstances.utils.Popen')
    def test_failure(self, *args):
        """Test an instance that refuses to start"""
        self.assertRaises(ProcessNotStartingError, lambda: MongoInstance(10101))


    def test_flush(self):
        """Test flushing the instance"""
        instance = MongoInstance(10101)
        collection = instance.conn['someDb']['someCollection']

        collection.insert({'foo': 'bar'})
        self.assertEqual(
            collection.find({'foo': 'bar'}).next()['foo'],
            'bar'
        )

        instance.flush()
        self.assertEqual(collection.find({'foo': 'bar'}).count(), 0)

        instance.terminate()

    def test_get_logs(self):
        """Test getting the instance logs"""
        instance = MongoInstance(10101)
        logs = instance.get_logs()
        self.assertGreater(len(logs), 1000)
        instance.terminate()

    def test_gevent(self):
        """Test starting mongo with gevent."""
        instance = MongoInstance(10101, use_gevent=True)
        self.assertEqual(len(managed_instance.running_instances), 1)
        instance.flush()
        instance.terminate()


if __name__ == '__main__':
    unittest.main()
