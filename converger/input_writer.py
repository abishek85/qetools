#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write QE input file from a list of lines

@author: abishekk
"""

class InputWriter(object):
    """
    Class to write lines to file
    
    Usage:
        fileWrite = InputWriter('modInput.txt',listLines)
        fileWrite.write_lines_to_file()
    """

    def __init__(self, filename, linesList):
        """
        Initialize InputWriter with a file and list of lines to be output
        
        filename: string, name of file to be created
        linesList: list of strings, lines to written to file with '\n' included
        
        Has 2 attributes:
            self.outFile: string, from filename
            self.lines: list of strings, from linesList
        """
        self.outFile = filename
        self.lines = linesList
            
    def write_lines_to_file(self):
        """
        Write all the lines from a list and store them in a file
        """
        with open(self.outFile, 'w') as fileptr:
            fileptr.writelines("%s" % line for line in self.lines)