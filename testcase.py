#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest


class MyTestCase(unittest.TestCase):
    def test_db_init(self):
        from utils.dbInterface import init_db

        init_db()


if __name__ == '__main__':
    unittest.main()
