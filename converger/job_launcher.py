#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 11:51:44 2018

@author: abishekk
"""

import os
import sys
import subprocess
import time

class JobLauncher(object):
    """
    Class to launch and monitor jobs on a cluster
    
    Usage:
        jobMgr= JobLauncher('mpirun -np 16  pw.x','in.pw.si','out.pw.si')
        jobMgr.job_run()
    """
    def __init__(self, cmd, inputFile, outputFile, pbsParams=None):
        """
        Initializes an object to launch and monitor jobs
        
        cmd: string, mpirun, options, and executable
             eg. mpirun -np 16 pw.x
        inputFile: string, path and name of the input file to be used
        outputFile: string, path and name for the output file that will be 
                    generated by the run
        pbsParams: string, PBS options for running the job
        
        Has 6 attributes:
            self.cmdStr: string, determined by cmd
            self.inFile: string, determined by inputFile
            self.outFile: string, determined by outputFile
            self.pbsParams: string, determined by pbsParams
            self._jobId: integer, job id returned by the queue manager
            self._workDir: string, path of the current working directory
        """
        
        self.cmdStr = cmd
        self.inFile = inputFile
        self.outFile = outputFile
        self.pbsParams = pbsParams
        self._jobId = None
        self._workDir = os.getcwd()
                
        try:
            fileptr = open(self.inFile,'r')
        except OSError:
            print('Cannot open: ', self.inFile)
            sys.exit(1)
        else:
            fileptr.close()
            
        if self.pbsParams == None:
            self.pbsParams = ''

    def job_run(self):
        """
        Submit job to the queue using PBS and wait for the job to finish
        """
        # process commands for running the job
        self.cmdStr = self.cmdStr + ' < ' + self.inFile + \
                       ' > ' + self.outFile
                       
        # submit job to the queue
        # TO DO: Launch from PBS script
        submitCmd = "echo '" + self.cmdStr + "' | " + "qsub -V -d " + \
                     self._workDir + " " + self.pbsParams + " -"
        
        # TO DO: Error checking to make sure job launches and runs            
        jobSubmit = subprocess.Popen(submitCmd, shell=True, \
                                     stdout=subprocess.PIPE)
        
        # qsub returns job ID to stdout
        self._jobId = jobSubmit.communicate()[0].rstrip()
        
        # wait for job to finish 
        self.job_wait()
    
    def job_wait(self):
        """
        Waits for submitted job to finish execution. Uses self._jobId. 
        """
        # TO DO: check if job runs properly
        while True:
            jobStatus = subprocess.Popen('qstat -j ' + self._jobId, \
                                         shell=True, stdout=subprocess.PIPE)
            qstatMsg = jobStatus.communicate()[0]
            
            # If job has completed, qstat outputs 'Following jobs do not exist'
            if "not exist" in qstatMsg:
                break
            else: 
                # sleep and requery qstat
                time.sleep(10) # wait for 10 s
                
  