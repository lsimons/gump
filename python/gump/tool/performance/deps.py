#!/usr/bin/python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""    
    Does lots of dependency stuff (for performance tuning) 
"""

import os.path
import sys

from gump import log
from gump.core.gumpinit import gumpinit
from gump.test import getWorkedTestRun
from gump.document.xdocs.documenter import XDocDocumenter
from gump.core.commandLine import handleArgv
from gump.core.run.gumprun import GumpRun
from gump.core.loader.loader import WorkspaceLoader

def deps(run,runs=1):
    
    test='test'
    if not os.path.exists(test): os.mkdir(test)
    
    gtest=os.path.join(test,'gump')
    if not os.path.exists(gtest): os.mkdir(gtest)
    
    xwork=os.path.join(gtest,'xdocs-work')
    if not os.path.exists(xwork): os.mkdir(xwork)
        
    documenter=XDocDocumenter(run,gtest,'http://someplace')
        
    for r in range(runs):   
        print 'Perform run # ' + `r`
        for project in run.getWorkspace().getProjects():
            project.getDirectDependencies()
            project.getDirectDependees()
            project.getFullDependencies()
            project.getFullDependees()
        
def xrun():
    gumpinit()
  
    if len(sys.argv) > 1:
        # Process command line
        (args,options) = handleArgv(sys.argv)
        ws=args[0]
        ps=args[1]    
        
        # get parsed workspace definition
        workspace=WorkspaceLoader(options.isCache()).load(ws)    
        
        # The Run Details...
        run=GumpRun(workspace,ps,options) 
    else:
        run=getWorkedTestRun()    
        
    deps(run,100) 
    
    # bye!
    sys.exit(0)
    
# static void main()
if __name__=='__main__':

    #print 'Profiling....'
    #import profile
    #profile.run('xrun()', 'iprof')
    xrun()
     
