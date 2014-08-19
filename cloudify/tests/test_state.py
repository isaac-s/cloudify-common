
import threading
import unittest
from Queue import Queue


from cloudify.state import ctx, current_ctx

from cloudify.mocks import MockCloudifyContext


class TestCurrentContextAndCtxLocalProxy(unittest.TestCase):

    def test_basic(self):
        self.assertRaises(RuntimeError, current_ctx.get)
        self.assertRaises(RuntimeError, lambda: ctx.node_id)
        value = MockCloudifyContext(node_id='1')
        current_ctx.set(value)
        self.assertEqual(value, current_ctx.get())
        self.assertEqual(value.node_id, ctx.node_id)
        current_ctx.clear()
        self.assertRaises(RuntimeError, current_ctx.get)
        self.assertRaises(RuntimeError, lambda: ctx.node_id)

    def test_threads(self):
        num_iterations = 1000
        num_threads = 10
        for _ in range(num_iterations):
            queues = [Queue() for _ in range(num_threads)]

            def run(queue, value):
                try:
                    self.assertRaises(RuntimeError, current_ctx.get)
                    self.assertRaises(RuntimeError, lambda: ctx.node_id)
                    current_ctx.set(value)
                    self.assertEqual(value, current_ctx.get())
                    self.assertEqual(value.node_id, ctx.node_id)
                    current_ctx.clear()
                    self.assertRaises(RuntimeError, current_ctx.get)
                    self.assertRaises(RuntimeError, lambda: ctx.node_id)
                except Exception, e:
                    queue.put(e)
                else:
                    queue.put('ok')

            threads = []
            for index, queue in enumerate(queues):
                value = MockCloudifyContext(node_id=str(index))
                threads.append(threading.Thread(target=run,
                                                args=(queue, value)))

            for thread in threads:
                thread.start()

            for queue in queues:
                self.assertEqual('ok', queue.get())