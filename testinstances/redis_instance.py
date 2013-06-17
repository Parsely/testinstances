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

import logging
import os
import redis
import shutil
import subprocess
import sys
import time

from testinstances.exceptions import ProcessNotStartingError
from testinstances.managed_instance import ManagedInstance

log = logging.getLogger(__name__)

class RedisInstance(ManagedInstance):
    """A managed redis instance for testing"""
    def __init__(self, port, name='redis', dumpfile=None):
        """Start redis instance on the given port and inside root_dir"""
        self.port = port
        self.dumpfile = os.path.abspath(dumpfile) if dumpfile else None
        super(RedisInstance, self).__init__('%s-%i' % (name, port))


    def _start_process(self):
        """Start the instance process"""
        log.info('Starting redis-server on port %i...', self.port)
        if self.dumpfile:
            log.info('Loading dumpfile %s...', self.dumpfile)
            shutil.copyfile(
                self.dumpfile,
                os.path.join(self._root_dir, os.path.basename(self.dumpfile))
            )
        self._process = subprocess.Popen(
            args=["redis-server",
                  '--port', str(self.port),
                  '--bind', '127.0.0.1',
                  '--dir', self._root_dir,
                  ],
            stderr=subprocess.STDOUT,
            stdout=open(self.logfile, 'w'),
            )

        # Connect to the shiny new instance
        self.conn = None
        fails = 0
        while self.conn is None:
            try:
                conn = redis.StrictRedis(port=self.port)
                if conn.info()['loading'] == 0: # make sure dump is loaded
                    self.conn = conn
            except:
                if fails == 10:
                    break
                fails += 1
                time.sleep(1)

        if self.conn is None or self._process.poll() is not None:
            log.critical('Unable to start redis-server in 10 seconds')
            raise ProcessNotStartingError("Unable to start redis-server")

    def flush(self):
        """Flush all data in all dbs"""
        self.conn.flushall()
