#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse QE output files and return the results

@author: abishekk
"""

class OutputParser(object):
    
    """
    Read output files from finished DFT calculations
    
    Usage eg. 
       opp = OutputParser()
       opp.parse_op_file('si.scf.cg.out')
       opp.get_totenergy()
       opp.get_kpoints()
    """
    
    def __init__(self):
        self._totEnergy = 0.0
        self._kpoints = 0
        # Dictionary to translate generic keyword to code specific keyword
        # the list can be expanded if a metric other than the total energy 
        # is the convergence criterion
        # Dictionary to parse QE output files
        self._qeDict = {'total energy':'!', 'kpoints': 'number of k points'}
        # TO DO: Include option to choose units
        self.rydtoev = 13.605698065894
        
    def parse_qe_op_file(self,filename):
        # open output file in read-only mode
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
                
    def get_totenergy(self):
        return self._totEnergy
    
    def get_kpoints(self):
        return self._kpoints
