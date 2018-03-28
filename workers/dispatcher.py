#!/usr/bin/env python
import json
import logging

from scanning.lib.log import load_logger
from base import BaseWorker


class DispatcherWorker(BaseWorker):
    ACTIONS = ('start_scan', 'notify')
    NAME = 'Dispatcher worker'

    def handle_job(self, job):
        """
        Handler job pushed to master tube
        """
        action = job.get('action')
        if action not in self.ACTIONS:
            self.logger.debug('Unknown action: {}'.format(action))
            return
        # The name of tube and action are same
        self.queue.put(json.dumps(job), action)
        self.logger.info('Moved job to tube: {}'.format(action))

    def run(self):
        """Run worker"""
        while True:
            job_obj = self.queue.get()
            job = json.loads(job_obj.body)
            self.logger.info('Got job: {}'.format(job))
            try:
                self.handle_job(job)
            except Exception as e:
                self.logger.error(
                    'Error in handling job: {}\nJob details: {}'.format(
                        e, job), extra={'locals': locals()}, exc_info=True)
            self.queue.delete(job_obj)


if __name__ == '__main__':
    load_logger()
    logger = logging.getLogger('dispatcher')
    worker = DispatcherWorker(logger, sub='master_tube')
    worker.run()
