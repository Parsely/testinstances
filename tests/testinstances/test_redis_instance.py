import mock
import os
import redis
import unittest

from testinstances import managed_instance, RedisInstance
from testinstances.exceptions import ProcessNotStartingError

class RedisInstanceTests(unittest.TestCase):

    def tearDown(self):
        managed_instance._cleanup()

    def test_start_stop(self):
        """Test starting and stopping an instance"""
        instance = RedisInstance(10101)
        self.assertIsNotNone(instance.conn.info())

        instance.terminate()
        self.assertRaises(redis.ConnectionError, lambda: instance.conn.info())

    @mock.patch('testinstances.utils.Popen')
    def test_failure(self, *args):
        """Test an instance that refuses to start"""
        self.assertRaises(ProcessNotStartingError, lambda: RedisInstance(10101))

    def test_flush(self):
        """Test flushing the instance"""
        instance = RedisInstance(10101)

        instance.conn.set('foo', 'bar')
        self.assertEqual(instance.conn.get('foo'), 'bar')

        instance.flush()
        self.assertFalse(instance.conn.exists('foo'))

        instance.terminate()

    def test_get_logs(self):
        """Test getting the instance logs"""
        instance = RedisInstance(10101)
        logs = instance.get_logs()
        self.assertGreater(len(logs), 1000)
        instance.terminate()

    def test_load_dumpfile(self):
        """Test loading a dumpfile"""
        here = os.path.split(os.path.abspath(__file__))[0]
        dumpfile = os.path.join(here, './resources/dump.rdb')
        instance = RedisInstance(10101, dumpfile=dumpfile)
        self.assertEqual(instance.conn.get('foo'), 'bar')
        instance.terminate()

    def test_gevent(self):
        """Test starting redis with gevent."""
        instance = RedisInstance(10101, use_gevent=True)
        self.assertEqual(len(managed_instance.running_instances), 1)
        instance.flush()
        instance.terminate()


if __name__ == '__main__':
    unittest.main()
