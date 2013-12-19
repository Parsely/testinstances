import mock
import os
import tempfile
import unittest

from testinstances import managed_instance, MongoInstance, RedisInstance
from testinstances.exceptions import ProcessRunningError
from testinstances.managed_instance import ManagedInstance

class ManagedInstanceTests(unittest.TestCase):

    def tearDown(self):
        managed_instance._cleanup()

    def test_cleanup(self):
        """Test _cleanup kills all instance kinds"""
        redis = RedisInstance(10101)
        mongo = MongoInstance(10102)
        self.assertEqual(len(managed_instance.running_instances), 2)

        managed_instance._cleanup(exiting=True)
        self.assertEqual(len(managed_instance.running_instances), 0)
        self.assertFalse(os.path.exists(managed_instance.instance_tmpdir))

        # It's module-wide so reset this for future tests
        managed_instance.instance_tmpdir = tempfile.mkdtemp()

    def test_exceptions(self):
        """Test there are no default implementations in ManagedInstance

        Doesn't do much but get us test coverage.
        """
        self.assertRaises(NotImplementedError,
                          lambda: ManagedInstance('foo1'))
        with mock.patch.multiple(ManagedInstance,
                                 _start_process=mock.DEFAULT,
                                 _start_log_watcher=mock.DEFAULT) as mocks:
            instance = ManagedInstance('foo2')
            instance._process = mock.MagicMock()
            self.assertRaises(NotImplementedError, lambda: instance.flush())
            open(instance.logfile, 'w').write('ohai') # so can delete
            instance.terminate()

    def test_multiple_instances(self):
        """Test we can start multiple instance, but not with the same name"""
        inst1 = MongoInstance(10101)
        inst2 = MongoInstance(10102)
        self.assertRaises(ProcessRunningError, lambda: MongoInstance(10101))
        inst1.terminate()
        inst2.terminate()


if __name__ == '__main__':
    unittest.main()
