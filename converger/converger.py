#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class to set up QE calculations for checking convergence

@author: abishekk
"""
import numpy as np
import sys
import os
import matplotlib.pyplot as plt

from input_reader import InputReader
from input_writer import InputWriter
from job_launcher import JobLauncher
from output_parser import OutputParser

class Converger(object):
    
    def __init__(self, filename, convCriterion='total energy', \
                 tol=1e-6, dftCode='qe'):
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
        # absolute tolerance 
        self._tolerance = float(tol)
        # array to hold results: parameter, criterion value 
        self._results= []
        # bool for keeping track of convergence
        self._notConverged = True
        # DFT package name
        self._dftPackage = dftCode
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
        lineNum = qeInput.find_line_number(self._convergeUsing)
        linesList = qeInput.get_lines_file()
                
        # modify k-point input card
        if (self._convergeUsing == 'kpoints'):
            modLinesList = self.modify_kpoint_card(linesList, lineNum)
        
        while self._notConverged:
            # create input file for job
            jobStr = self._convergeUsing + '_' + \
                      np.array2string(self._startValue,separator='_')[1:-1]
            workDir = os.getcwd()
            jobPath = workDir + '/' + jobStr
            inpFile = 'in.' + jobStr
            outFile = 'out.' + jobStr
            
            if not os.path.exists(jobPath):
                os.makedirs(jobPath)            
            os.chdir(jobPath)
            
            modLinesList[lineNum+1] = \
                    np.array2string(self._startValue,separator=' ')[1:-1] + \
                    ' 0 0 0\n'
            
            NewInput = InputWriter(inpFile, modLinesList)
            NewInput.write_lines_to_file()
            
            # launch task
            task = JobLauncher('mpirun -np 16 pw.x', inpFile, outFile)
            task.job_run()
            
            # parse output file after job finishes and update results
            readOut = OutputParser(self._dftPackage)
            readOut.parse_op_file(outFile)
            
            # TO DO: make it generic
            self._results.append([readOut.get_kpoints(), \
                                  readOut.get_totenergy()])
            
            # check convergence
            if(len(self._results) >= 2):
                deltaTotEnergy = abs(self._results[-1][1] - \
                                     self._results[-2][1])
            
            if (deltaTotEnergy <= self._tolerance):
                # total energy has converged
                self._notConverged = False
            else:
                # update K-points and repeat calculation
                os.chdir(workDir)
                self._startValue += self._stepSize
                    
        # output, print result
        print('Convergence test completed!')
        if (self._convergeUsing == 'kpoints'):
            print('K-point grid needed for convergence: ' + self._startValue)
        self.plot_results()
            
    
    def modify_kpoint_card(self,lines,lineNum):
        # k-point convergence requires the k-points to be 
        # generated automatically. Any other method of specifying k-points
        # needs to be changed to automatic mode
        modLines = lines.copy()
        kptOption = modLines[lineNum].split()[1]
        if kptOption == 'gamma':
            modLines[lineNum] = 'K_POINTS automatic\n'
            if lineNum == len(lines)-1 :
                modLines.append('0 0 0 0 0 0\n')
            else:
                modLines.insert(lineNum+1,'0 0 0 0 0 0\n')
        elif kptOption == 'automatic':
            modLines[lineNum+1] = '0 0 0 0 0 0\n'
        else:
            modLines[lineNum] = 'K_POINTS automatic\n'
            kptNum = int(lines[lineNum+1])
            modLines[lineNum+1] = '0 0 0 0 0 0\n'
            del modLines[lineNum+2:lineNum+2+kptNum]
        
        return modLines
    
    def plot_results(self,xlabel,ylabel):
        """
        Plot results of convergence tests
        """
        results = np.asarray(self._results)
        plt.plot(results[:,0],results[:,1],'ro-',linewidth=2,markersize=10)
        plt.xlabel(self._convergeUsing)
        plt.ylabel(self._convergeParam)
        plt.title('Convergence tests')
        plt.show()
        