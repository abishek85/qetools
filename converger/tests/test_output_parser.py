#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for functions in output_parser.py

@author: abishekk
"""
import unittest
import sys

sys.path.insert(0,'../')
from output_parser import *

class TestOutputParserMethods(unittest.TestCase):
    
    def test_parse_qe_op_file(self):
        # case 1
        testOutRead = OutputParser('qe')
        testOutRead.parse_qe_op_file('./out.dummy_qe')
        self.assertEqual(testOutRead.get_kpoints(),42)
        self.assertEqual(testOutRead.get_totenergy(),-1.0*testOutRead.rydtoev)
        
        # case 2
        testOutRead = OutputParser('qe')
        testOutRead.parse_qe_op_file('./si.scf.cg.out')
        self.assertEqual(testOutRead.get_kpoints(),10)
        self.assertEqual(testOutRead.get_totenergy(), \
                         -15.84452726*testOutRead.rydtoev)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOutputParserMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)