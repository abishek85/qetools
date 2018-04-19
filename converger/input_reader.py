#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read QE input file and return all the lines as a list

@author: abishekk
"""
import sys

class InputReader(object):
    """
    Class to read sample input file and store it as a list. 
    
    Usage: 
        ipp = InputReader('in.pw.si','qe')
        ipp.read_file()
        lineNum = ipp.find_line_number('kpoints')
        lineList = ipp.get_lines_file()
    """
    
    def __init__(self, filename, dftName='qe'):
        """
        Initializes object to read sample DFT input file
        
        filename: string, input file name
        dftName: string, name of DFT code being used eg. 'qe', 'vasp'
        
        Has 4  attributes:
            self.inFile: string, from filename
            self.dftCode: string, from dftName
            self._lines: list of strings, stores lines in input file
            self._qeDict: dictionary, translate generic keyword to code key
        """
        
        self.inFile = filename
        self.dftCode = dftName
        self._lines = []
        # Dictionary for each DFT code
        # dictionary for QE: translate input strings to match QE format
        self._qeDict = { 'kpoints'               : 'K_POINTS', 
                         'kinetic energy cutoff' : 'ecutwfc'}
        
        # check if inFile exists
        try:
            fileptr = open(self.inFile,'r')
        except OSError:
            print('Cannot open: ', self.inFile)
            sys.exit(1)
        else:
            fileptr.close()
            
    def read_file(self):
        """ 
        Read all the lines from a file and store them in a list
        """
        with open(self.inFile, 'r') as fileptr:
            self._lines = fileptr.readlines()
            
    def find_line_number(self,findString):
        """
        Find the line number in which an input string occurs
        
        findString: string, search for the string in input file
        
        returns: int, line number of search string and None if not found
        """
        #  TO DO: check if findString is valid input
        stringLineNum = None
        
        if self.dftCode == 'qe':
            codeDict = self._qeDict
        else:
            print("Support for other codes yet to be implemented")
               
        # find the line number in which the string occurs
        searchStr = codeDict[findString]
        for line in self._lines:
            if searchStr in line:
                stringLineNum = self._lines.index(line)
                
        return stringLineNum
            
    def get_lines_file(self):
        """
        Return copy of the lines list. 
        """
        return self._lines.copy()