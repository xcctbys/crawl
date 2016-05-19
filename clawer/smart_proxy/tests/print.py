#!/usr/bin/env python  
#coding:utf-8  
import sys
import os
import time
"""
output=sys.stdout
outputfile=open(filename,'w')
sys.stdout=outputfile
outputfile.close()
sys.stdout=output
"""



def printFile(f,output):
    print output;
    f.writelines(output+'\n')
             
if __name__=='__main__':
    f=open('/tmp/crontab_print.log','w')
    for i in range(120):
        time.sleep(1)
        i=str(i)
        printFile(f,i)
    f.close()
