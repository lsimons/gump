#!/usr/bin/python

# Copyright 2004 The Apache Software Foundation
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

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


"""
	An configure builder (uses ./configure to build projects)
"""

import os.path
import sys

from gump import log
from gump.core.run.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.util import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
from gump.util.note import Annotatable
from gump.util.work import *

from gump.util.tools import *

from gump.core.model.workspace import *
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.stats import *
from gump.core.model.state import *


###############################################################################
# Classes
###############################################################################

class ConfigureBuilder(gump.core.run.gumprun.RunSpecific):
    
    def __init__(self,run):
        """
        A configure 'builder'
        """
        gump.core.run.gumprun.RunSpecific.__init__(self,run)

    def buildProject(self,project,languageHelper,stats):
        """
        Run a project's configure script (doesn't support Windows, yet)
        """
        
        workspace=self.run.getWorkspace()
                 
        log.info('Run Project\'s configure script: #[' + `project.getPosition()` + '] : ' + project.getName())
                
        #
        # Get the appropriate build command...
        #
        cmd=self.getConfigureCommand(project)

        if cmd:
            # Execute the command ....
            cmdResult=execute(cmd,workspace.tmpdir)
    
            # Update Context    
            work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
            project.performedWork(work)
            project.setBuilt(True)
                    
            # Update Context w/ Results  
            if not cmdResult.state==CMD_STATE_SUCCESS:
                reason=REASON_BUILD_FAILED
                if cmdResult.state==CMD_STATE_TIMED_OUT:
                    reason=REASON_BUILD_TIMEDOUT
                project.changeState(STATE_FAILED,reason)
                        
            else:                         
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)
   
    def getConfigureCommand(self,project):
        """ Return the command object for a <configure entry """
        configure=project.configure
           
        # Where to run this:
        basedir = configure.getBaseDirectory() or project.getBaseDirectory()

        # The script
        scriptfile=os.path.abspath(os.path.join(basedir, 'configure'))
        
        cmd=Cmd(scriptfile,'buildscript_'+project.getModule().getName()+'_'+project.getName(),\
            basedir)    
        
        return cmd
        
        
    def preview(self,project,languageHelper,stats):        
        """
        Preview what this would do
        """
        command=self.getConfigureCommand(project) 
        command.dump()
