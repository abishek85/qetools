#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 10:58:22 2018

@author: abishekk
"""

# Unit tests for input reader class
import sys
import unittest

sys.path.insert(0,'../')
from input_reader import *

class TestInputReaderMethods(unittest.TestCase):
    
    def test_get_lines_file(self):
        """
        Unit test for get_lines_file
        """
        # case 1
        inReader = InputReader('hello.txt')
        inReader.read_file()
        linesRead = inReader.get_lines_file()
        
        self.assertEqual(len(linesRead), 1)
        self.assertEqual(linesRead[0], 'Hello World!\n')
        
        # case 2
        inReader = InputReader('in.pw.si')
        inReader.read_file()
        linesRead = inReader.get_lines_file()
        
        self.assertEqual(len(linesRead), 26)
        self.assertEqual(linesRead[-2], 'K_POINTS automatic\n')

    def test_find_line_number(self):
        """
        Unit test for find_line_number
        """
        # case 1
        inReader = InputReader('in.pw.si')
        inReader.read_file()        
        linesRead = inReader.get_lines_file()
        
        self.assertEqual(inReader.find_line_number('kpoints'),24)
        self.assertEqual(
                inReader.find_line_number('kinetic energy cutoff'),11)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInputReaderMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)