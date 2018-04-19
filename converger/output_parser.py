#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse QE output files and return the results

@author: abishekk
"""
import sys

class OutputParser(object):
    
    """
    Read output files from finished DFT calculations
    
    Usage eg. 
       opp = OutputParser('qe')
       opp.parse_op_file('si.scf.cg.out')
       opp.get_totenergy()
       opp.get_kpoints()
    """
    
    def __init__(self, dftCode='qe'):
        """
        Initializes an object to read DFT output files
        
        dftCode: string, program name eg. 'qe', 'vasp'
        
        Has 5 attributes:
            self.dftName: string, determined by dftCode
            self._totEnergy: float, stores total energy of the system
            self._kpoints: int, stores k-points used by the system
            self._qeDict: dictionary, translate generic keyword to QE keyword
            self.rydtoev: float, convert energies from Ry to eV 
        """
        self.dftName = dftCode
        self._totEnergy = 0.0
        self._kpoints = 0 
        # to parse QE output files
        self._qeDict = {'total energy':'!', 'kpoints': 'number of k points'}
        # TO DO: Include option to choose units
        self.rydtoev = 13.605698065894
        
    def parse_op_file(self,filename):
        """
        Function that passes control to DFT code-based parser
        
        filename: string, path to output file
        """
        if self.dftName == 'qe':
            self.parse_qe_op_file(filename)
        elif self.dftName == 'vasp':
            print('VASP support not yet implemented')
        else:
            print('DFT program name is not recognized. Check input!')
        
    def parse_qe_op_file(self,filename):
        """
        Parse QE output files and store the results
        """
        # open output file in read-only mode
        try:
            fileptr = open(filename,'r')
            # search file for keywords and extract values
            for line in fileptr:                
                # total energy in eV
                if self._qeDict['total energy'] in line:
                    self._totEnergy = float(line.split()[4])*self.rydtoev
                    
                # total number of k-points
                if self._qeDict['kpoints'] in line:
                    self._kpoints = int(line.split()[4])
            # close file   
            fileptr.close() 
        except OSError:
            print('Cannot open: ', filename)
            sys.exit(1)
                      
    def get_totenergy(self):
        """
        Returns total energy value read from output in eV (float)
        """
        return self._totEnergy
    
    def get_kpoints(self):
        """
        Returns the total number of k-points used for DFT calculation (int)
        """
        return self._kpoints
    