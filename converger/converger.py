#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class to set up QE calculations for checking convergence

@author: abishekk
"""
import numpy as np
import sys
from input_reader import InputReader

class Converger(object):
    
    def __init__(self, filename, convCriterion='total energy', tol=1e-8):
        # which variable to change for check for convergence
        # eg. ecutwfc, ecutrho, k-points
        self._convergeParam = ''
        # starting value for variable parameter
        self._startValue = []
        # step size for variable parameter
        self._stepSize = []
        # QE input file
        self._inputFile = filename
        # which property to use for checking convergence
        # eg. total energy, fermi energy etc
        self._convergeUsing = str(convCriterion)
        # tolerance 
        self._tolerance = float(tol)
        # array to hold results: parameter, criterion 
        self._results= []
        # bool for keeping track of convergence
        self._notConverged = True
                
        # open input file to check if it exists
        try:
            fileptr = open(self._inputFile,'r')
        except OSError:
            print('Cannot open: ', self._inputFile)
            sys.exit(1)
        else:
            fileptr.close()

        # check if criterion used for convergence is allowed           
        if (self._convergeUsing != 'total energy'):
            raise Exception('Currently, only \'total energy\' is allowed')
        
        # check if tolerance for determining is valid           
        if (self._tolerance <= 0):
            raise Exception('Value for tolerance must be greater than 0')
    
    def start_convergence(self, convParm, startVal, step):
        
        # Set inputs
        # check if convergence parameter is valid string          
        self._convergeUsing = str(convParm)
        if (self._convergeUsing != 'kpoints'):
            raise Exception('Currently, only \'kpoints\' is supported')
        else:
            # set initial values for the k-point grid
            # TO DO: check for non-integer in array
            self._startValue = np.array(startVal)
            self._startValue = self._startValue.astype(int)
            if (len(self._startValue) != 3):
                raise Exception('k-point grid is input as [x,y,z]')
            if (any(i < 0 for i in self._startValue)):
                raise Exception('k-point grid value must be greater than 0')           
            # set step size for k-point grid
            # TO DO: check for non-integer values
            self._stepSize = np.array(step)
            self._stepSize = self._stepSize.astype(int)
            if (len(self._stepSize) != 3):
                raise Exception('k-point grid step is input as [x,y,z]')        
            if (any(i < 0 for i in self._stepSize)):
                raise Exception('k-point grid step must be greater than 0')
              
        # read inputfile
        qeInput = InputReader(self._inputFile)
        qeInput.read_file()
        LineNum = qeInput.find_line_number(self._convergeUsing)
        LinesList = qeInput.get_lines_file()
                
        # modify k-point input card
        if (self._convergeUsing == 'kpoints'):
            modLinesList = self.modify_kpoint_card(LinesList, LineNum)
        
        while self._notConverged:
            # create new inputfile
            self._notConverged = False
            # start job
        
            # parse output file after job finishes
        
            # check convergence
        
        # output, print result
        print('Done!')
    
    def modify_kpoint_card(self,lines,lineNum):
        # k-point convergence requires the k-points to be 
        # generated automatically. Any other method of specifying k-points
        # needs to be changed to automatic mode
        modLines = lines
        kptOption = modLines[lineNum].split()[1]
        if kptOption == 'gamma':
            modLines[lineNum] = 'K_POINTS automatic'
            if lineNum == len(lines)-1 :
                modLines.append('0 0 0 0 0 0')
            else:
                modLines.insert(lineNum+1,'0 0 0 0 0 0')
        elif kptOption == 'automatic':
            modLines[lineNum+1] = '0 0 0 0 0 0'
        else:
            modLines[lineNum] = 'K_POINTS automatic'
            kptNum = int(lines[lineNum+1])
            modLines[lineNum+1] = '0 0 0 0 0 0'
            del modLines[lineNum+2:lineNum+2+kptNum]
        
        return modLines
