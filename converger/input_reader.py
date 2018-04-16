#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read QE input file and return all the lines as a list

@author: abishekk
"""
import sys

class InputReader:
    # TO DO: Take program type as input to change how the object reads from
    #        the file
    def __init__(self, filename):
        
        # input file
        self._inFile = filename
        # list of lines in file
        self._lines = []
        # dictionary for QE: translate input strings to match what is found in
        # QE input files
        self._qeDict = { 'kpoints'               : 'K_POINTS', 
                         'kinetic energy cutoff' : 'ecutwfc'}
        
        try:
            fileptr = open(self._inFile,'r')
        except OSError:
            print('Cannot open: ', self._inFile)
            sys.exit(1)
        else:
            fileptr.close()
            
    def read_file(self):
        # read all the lines from a file and store them in a list
        with open(self._inFile, 'r') as fileptr:
            self._lines = fileptr.readlines()
            
    def find_line_number(self,findString):
        # find the line number in which the string occurs
        qeString = self._qeDict[findString]
        for line in self._lines:
            if qeString in line:
                stringLineNum = self._lines.index(line)
                
        return stringLineNum
            
    def get_lines_file(self):
        return self._lines