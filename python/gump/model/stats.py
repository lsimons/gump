#!/usr/bin/env python

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
    Statistics gathering/manipulation
"""

import time
import os
import sys
import logging
import anydbm

import gump
from gump.core.config import *
from gump.model.state import *

#
# Durations (in 'runs')
#
INSIGNIFICANT_DURATION=5
SIGNIFICANT_DURATION=30

class Statistics:
    """Statistics Holder"""
    def __init__(self,name):
        self.name=name
        self.successes=0
        self.failures=0
        self.prereqs=0
        self.first=-1
        self.last=-1
        self.currentState=STATE_UNSET
        self.previousState=STATE_UNSET
        self.startOfState=-1        
        self.sequenceInState=0
        self.lastModified=0
                
    #           
    # FOG is (at pressent) effectively the
    # 'odds of success' (based off historical results).
    #
    # We ought find a way to factor in durations and
    # age into this
    #
    def getFOGFactor(self):
        return self.getHistoricalOddsOfSuccess()        
        
    #           
    # 'odds of success' (based off historical results).
    #
    def getHistoricalOddsOfSuccess(self):
        good=self.successes or 0
        bad=(self.failures+self.prereqs) or 0
        total=(good+bad) or 1
        return float(good)/float(total)
        
    def getLastModified(self):
        return (self.lastModified)
        
    def nameKey(self):
        return self.getKeyBase() + '-name'
        
    def successesKey(self):
        return self.getKeyBase() + '-successes'
        
    def failuresKey(self):
        return self.getKeyBase() + '-failures'
        
    def prereqsKey(self):
        return self.getKeyBase() + '-prereqs'
        
    def firstKey(self):
        return self.getKeyBase() + '-first'
        
    def lastKey(self):
        return self.getKeyBase() + '-last'
        
    def lastModifiededKey(self):
        return self.getKeyBase() + '-last-updated'
        
    def currentStateKey(self):
        return self.getKeyBase() + '-current-state'
        
    def previousStateKey(self):
        return self.getKeyBase() + '-previous-state'
        
    def startOfStateKey(self):
        return self.getKeyBase() + '-start-state' 
               
    def sequenceInStateKey(self):
        return  self.getKeyBase() + '-seq-state'
        
    def update(self,statable):        
        #
        # Update based off current run
        #
        if statable.isSuccess():

            self.successes += 1
            self.last = default.time
            
            # A big event...
            if not self.first:
                self.first=self.last
            elif statable.isFailed():
                self.failures += 1    
            elif statable.isPrereqFailed():                        
                self.prereqs  += 1
            
        elif statable.isFailed():
            self.failures += 1
            
        elif statable.isPrereqFailed():
            self.prereqs += 1
            
        #
        # Deal with states & changes...
        #
        lastCurrentState=self.currentState
        
        # Update the state to now
        self.currentState=statable.getState()
        
        # See if it changed, and track...
        if lastCurrentState==self.currentState:      
            self.sequenceInState += 1            
        else:
            self.previousState=lastCurrentState  
            self.startOfState = default.time                
            self.sequenceInState = 1
           
    def dump(self, indent=0, output=sys.stdout):
        gump.utils.dump(self)
             
            
class Statable:
    def __init__(self): pass
    
    # Stats are loaded separately and cached on here,
    # hence they may exist on an object at all times.
    def hasStats(self):
        return hasattr(self,'stats')
        
    def setStats(self,stats):
        self.stats=stats
        
    def getStats(self):
        if not self.hasStats():
            raise RuntimeError, "Statistics not calculated/updated/available [yet]: " \
                    + self.getName()
        return self.stats
        
    