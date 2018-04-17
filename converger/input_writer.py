#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write QE input file from a list of lines

@author: abishekk
"""

class InputWriter(object):

    def __init__(self, filename, linesList):
        
        # input file
        self._outFile = filename
        # list of lines to be written to the file
        self._lines = linesList
            
    def write_lines_to_file(self):
        # write all the lines from a list and store them in a file
        with open(self._outFile, 'w') as fileptr:
            fileptr.writelines("%s" % line for line in self._lines)