from __future__ import unicode_literals, absolute_import

import unittest

from py4j.java_gateway import JavaGateway, is_instance_of
from py4j.protocol import Py4JJavaError
from py4j.tests.java_gateway_test import (
    start_example_app_process, safe_shutdown, sleep)


class IteratorTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
        self.p.join()
        sleep()

    def testIterator(self):
        scanner = self.gateway.jvm.java.util.Scanner("")
        scanner.close()
        try:
            next(scanner)
            self.fail("next() should have thrown an exception")
        except Py4JJavaError as e:
            self.assertTrue(is_instance_of(
                self.gateway, e.java_exception, "java.lang.IllegalStateException"))

        scanner = self.gateway.jvm.java.util.Scanner("")
        self.assertEqual(list(scanner), [])


if __name__ == "__main__":
    unittest.main()
