"""
Copyright 2013 Parse.ly, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import atexit
import logging
import os
import shutil
import tempfile
import time

from testinstances.exceptions import ProcessNotStartingError, ProcessRunningError

log = logging.getLogger(__name__)
running_instances = {} # keep track of what we've got
instance_tmpdir = tempfile.mkdtemp()

def _cleanup(exiting=False):
    """Stop all running instances and delete the temp dir"""
    global running_instances
    for instance in list(running_instances.values()):
        instance.terminate()
    running_instances = {}
    if exiting:
        shutil.rmtree(instance_tmpdir)
atexit.register(_cleanup, exiting=True)


class ManagedInstance(object):
    """Container for mongo/redis/whatever testing instances"""
    def __init__(self, name, use_gevent=False):
        if name in running_instances:
            raise ProcessRunningError("Process %s is already running!", name)

        self._process = None
        self._root_dir = os.path.join(instance_tmpdir, name)

        self.conn = None
        self.log = logging.getLogger('testinstances.%s' % name)
        self.logfile = os.path.join(instance_tmpdir, '%s.log' % name)
        self.name = name
        self.use_gevent = use_gevent

        os.mkdir(self._root_dir)
        try:
            self._start_process()
        except ProcessNotStartingError:
            shutil.rmtree(self._root_dir)
            os.remove(self.logfile)
            raise
        self._start_log_watcher()
        running_instances[self.name] = self

    def _watcher_threading(self, logfile):
        while True:
            line = logfile.readline().strip()
            if not line:
                continue
            self.log.info(line)

    def _watcher_gevent(self, logfile):
        import gevent.socket
        while True:
            gevent.socket.wait_read(logfile.fileno())
            line = logfile.readline().strip()
            if not line:
                continue
            self.log.info(line)

    def _start_log_watcher(self):
        """Watch the logfile and forward it to python logging"""
        logfile = open(self.logfile, 'r')
        if self.use_gevent:
            import gevent
            self._watch_thread = gevent.spawn(self._watcher_gevent, logfile)
        else:
            import threading
            self._watch_thread = threading.Thread(target=self._watcher_threading,
                                                  args=[logfile])
            self._watch_thread.daemon = True
            self._watch_thread.start()

    def _start_process(self):
        raise NotImplementedError('nope, try a subclass')

    def flush(self):
        """Clear all data in underlying database"""
        raise NotImplementedError("This needs an implementation")

    def get_logs(self):
        """Get the process's logs"""
        return open(self.logfile).read()

    def terminate(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
            shutil.rmtree(self._root_dir)
            os.remove(self.logfile)
        del running_instances[self.name]
