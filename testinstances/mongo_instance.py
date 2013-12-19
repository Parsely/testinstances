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
import logging
import pymongo
import time

from testinstances import utils
from testinstances.exceptions import ProcessNotStartingError
from testinstances.managed_instance import ManagedInstance

log = logging.getLogger(__name__)

class MongoInstance(ManagedInstance):
    """A managed mongo instance for testing"""
    def __init__(self, port, name='mongo', use_gevent=False):
        """Start mongoinstance on the given port"""
        self.port = port
        ManagedInstance.__init__(self, '%s-%i' % (name, port), use_gevent=use_gevent)

    def _start_process(self):
        """Start the instance process"""
        log.info('Starting mongod on port %i...', self.port)
        self._process = utils.Popen(
            args=["mongod",
                  '--port', str(self.port),
                  '--bind_ip', '127.0.0.1',
                  '--dbpath', self._root_dir,
                  '--nojournal',
                  ],
            stderr=utils.STDOUT,
            stdout=open(self.logfile, 'w'),
            use_gevent=self.use_gevent,
            )

        # Connect to the shiny new instance
        self.conn = None
        fails = 0
        while self.conn is None:
            try:
                conn = pymongo.MongoClient(port=self.port, use_greenlets=self.use_gevent)
                if conn.alive():
                    self.conn = conn
            except:
                if fails == 10:
                    break
                fails += 1
                time.sleep(1)

        if self.conn is None or self._process.poll() is not None:
            raise ProcessNotStartingError("Unable to start mongod in 10 seconds.")

    def flush(self):
        """Flush all data in the db"""
        for dbname in self.conn.database_names():
            if dbname not in ('local', 'admin', 'config'):
                self.conn.drop_database(dbname)
