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
    """
    Class to set up and launch convergence tests
    
    Usage:
        kptConv = Converger('in.pw.si', 'total energy', 1e-8, 'qe')
        kptConv.start_convergence('kpoints',[4,4,4], [1,1,1])
    """
    
    def __init__(self, filename, convCriterion='total energy', \
                 tol=1e-6, dftCode='qe'):
        """
        Initialize a convergence study with a sample input script, property 
        used for convergence, tolerance for that criterion, and DFT package to
        be used.
        
        filename: string, DFT input file
        convCriterion: string, property that will be used to determine conv.
        tol: float, absolute tolerance for convCriterion
        dftCode: string, DFT code used in the study eg. 'qe', 'vasp'
        
        Has 9 attributes:
            self.inputFile = string, DFT input file
            self.convergeUsing = string, convergence criterion eg. 
                                 'total energy', 'fermi energy' etc.
            self.tolerance = float, tolerance for determining convergence 
            self.dftPackage = string, name of DFT code to be used
            self.convergeParam = string, variable to change for convergence 
                                 study eg. ecutwfc, ecutrho, k-points
            self.startValue = list, initial value of convergeParam
            self.stepSize = list, increment for convergeParam
            self._results = array, 2 columns: 1 - convergeParam value, 
                            2 - convergeUsing value
            self._notConverged: bool, flag to store if converged solution 
                                obtained
        """
        
        self.inputFile = filename
        self.convergeUsing = str(convCriterion)
        self.tolerance = float(tol)
        self.dftPackage = dftCode
        self.convergeParam = ''
        self.startValue = []
        self.stepSize = []        
        self._results= []
        self._notConverged = True
        
        # open input file to check if it exists
        try:
            fileptr = open(self.inputFile,'r')
        except OSError:
            print('Cannot open: ', self.inputFile)
            sys.exit(1)
        else:
            fileptr.close()

        # check if criterion used for convergence is allowed           
        if (self.convergeUsing != 'total energy'):
            raise Exception('Currently, only \'total energy\' is allowed')
        
        # check if tolerance for determining is valid           
        if (self.tolerance <= 0):
            raise Exception('Value for tolerance must be greater than 0')
    
    def start_convergence(self, convParm, startVal, step):
        """
        Run convergence study with the specified parameter, its initial value, 
        and increment size
        
        convParam: string, convergence is determined w.r.t. this variable eg.
                   'kpoints', 'ke cutoff'
        startVal: list, initial value for convParam eg. 'kpoints' - [4,4,4], 
                  'ke cutoff' - [10]
        step: list, increment for convParam between two runs 
              eg. 'kpoints' = [2,2,2], 'ke cutoff' - [1]
        """
        # check if convergence parameter is valid string          
        self.convergeParam = str(convParm)
        if (self.convergeParam != 'kpoints'):
            raise Exception('Currently, only \'kpoints\' is supported')
        else:
            # set initial values for the k-point grid
            # TO DO: check for non-integer in array
            self.startValue = np.array(startVal)
            self.startValue = self.startValue.astype(int)
            if (len(self.startValue) != 3):
                raise Exception('k-point grid is input as [x,y,z]')
            if (any(i < 0 for i in self.startValue)):
                raise Exception('k-point grid value must be greater than 0')           
            # set step size for k-point grid
            # TO DO: check for non-integer values
            self.stepSize = np.array(step)
            self.stepSize = self.stepSize.astype(int)
            if (len(self.stepSize) != 3):
                raise Exception('k-point grid step is input as [x,y,z]')        
            if (any(i < 0 for i in self.stepSize)):
                raise Exception('k-point grid step must be greater than 0')
              
        # read sample inputfile
        qeInput = InputReader(self.inputFile)
        qeInput.read_file()
        linesList = qeInput.get_lines_file()
        lineNum = qeInput.find_line_number(self.convergeParam)
                
        # modify k-point input card
        # TO DO: make it generic
        if (self.convergeParam == 'kpoints'):
            modLinesList = self.modify_kpoint_card(linesList, lineNum)
        
        while self._notConverged:
            # create input file for job
            # for each value, a separate folder is created and all the files
            # relevant to the run are stored in it
            jobStr = self.convergeParam + '_' + \
                      np.array2string(self.startValue,separator='_')[1:-1]
            workDir = os.getcwd()
            jobPath = workDir + '/' + jobStr
            inpFile = 'in.' + jobStr
            outFile = 'out.' + jobStr
            
            # create job directory
            if not os.path.exists(jobPath):
                os.makedirs(jobPath)            
            os.chdir(jobPath)
            
            # change convParam value
            if (self.convergeParam == 'kpoints'):
                modLinesList[lineNum+1] = \
                np.array2string(self.startValue,separator=' ')[1:-1] + \
                ' 0 0 0\n'
            
            # create new input files with changed convParam
            newInput = InputWriter(inpFile, modLinesList)
            newInput.write_lines_to_file()
            
            # launch task
            task = JobLauncher('mpirun -np 16 pw.x', inpFile, outFile)
            task.job_run()
            
            # parse output file after job finishes and update results
            readOut = OutputParser(self.dftPackage)
            readOut.parse_op_file(outFile)
            
            # store output in results array
            # TO DO: retrieve the relevant convergeParam (make generic)
            self._results.append([readOut.get_kpoints(), \
                                  readOut.get_totenergy()])
            
            # check convergence
            if(len(self._results) >= 2):
                deltaTotEnergy = abs(self._results[-1][1] - \
                                     self._results[-2][1])
            
            if (deltaTotEnergy <= self.tolerance):
                # total energy has converged
                self._notConverged = False
            else:
                # update convParam and set up new calculation
                os.chdir(workDir)
                self.startValue += self.stepSize
                    
        # print, plot result
        print('Convergence test completed!')
        if (self.convergeParam == 'kpoints'):
            print('K-point grid needed for convergence: ' + self.startValue)
        self.plot_results()
              
    # TO DO: make it DFT package independent
    def modify_kpoint_card(self,lines,lineNum):
        """ 
        Modify k-point card to generate k-points automatically
        
        Note: k-point convergence requires the k-points to be generated 
        automatically. Any other method of specifying k-points needs to be 
        changed to automatic mode.
        
        lines: list of strings, lines of sample input
        lineNum: int, line number at which k-point card begins
        
        returns: modLines, list of strings containing modified k-point card
        """
        modLines = lines.copy()
        # kptOption can be 'gamma', 'automatic', or a list of k-points
        kptOption = modLines[lineNum].split()[1]
        
        if kptOption == 'gamma':
            # add a line with k-point grid since gamma takes no params
            modLines[lineNum] = 'K_POINTS automatic\n'
            if lineNum == len(lines)-1 :
                modLines.append('0 0 0 0 0 0\n')
            else:
                modLines.insert(lineNum+1,'0 0 0 0 0 0\n')
        elif kptOption == 'automatic':
            modLines[lineNum+1] = '0 0 0 0 0 0\n'
        else:
            # the list of k-points specified has to be deleted
            modLines[lineNum] = 'K_POINTS automatic\n'
            kptNum = int(lines[lineNum+1])
            modLines[lineNum+1] = '0 0 0 0 0 0\n'
            del modLines[lineNum+2:lineNum+2+kptNum]
        
        return modLines
    
    def plot_results(self):
        """
        Plot results of convergence tests
        """
        results = np.asarray(self._results)
        plt.plot(results[:,0],results[:,1],'ro-',linewidth=2,markersize=10)
        plt.xlabel(self.convergeParam)
        plt.ylabel(self.convergeUsing)
        plt.title('Convergence test')
        plt.show()
        