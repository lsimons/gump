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

    MySQL Statistics gathering/manipulation
    
"""

import types
import MySQLdb
import MySQLdb.cursors

from gump import log
  
class DbHelper:
    """
    	MySQL Statistics Database Interface
    """

    def __init__(self,conn,database='gump'):
        self.conn=conn
        self.database=database
        
    def __del__(self):
        if self.conn:
            self.conn.close()
            self.conn=None
            
    def value(self,value):
        """
        Escape and Quote a Value
        """
        escaped_encoded = ''
        
        if isinstance(value,types.StringTypes):
            escaped_encoded = "'" 
            escaped_encoded += MySQLdb.escape_string(value).replace("\\","\\\\").replace("'","\\'")
            escaped_encoded += "'"            
        else:
            escaped_encoded = value
            
        return escaped_encoded
 
    def generateSelect(self,table_name,column_name,entity_name):
        """
        Generate a select statement, index is a single name
        """ 
        statement="SELECT * FROM %s.%s WHERE %s='%s'" % (self.database, table_name, column_name, entity_name) 
        return statement
        
    def select(self,table_name,column_name,entity_name,columns):
        statement=self.generateSelect(table_name,column_name,entity_name)
        settings = {}
        cursor = None
        try:
            try:
                cursor = self.conn.cursor()
                log.debug('SQL: ' + statement)
                affected=cursor.execute(statement)
                log.debug('SQL affected: ' + `affected`)
            
                row = cursor.fetchall()[0] # Ought be only one...
          
                # Extract values
                for column in columns:
                    if row.has_key(column) and row[column]:
                        settings[column]=row[column]
                        #print 'Extracted %s -> %s' % ( column, row[column])
                              
            except Exception, details:
                if cursor: self.logWarnings(cursor)
                log.error('SQL Error on [%s] : %s' % (statement, details), exc_info=1)                
                raise
        finally:
            if cursor: cursor.close()         

        return settings

    def set(self,table_name,column_name,entity_name,settings):
        
        # Unfortunately affected is returning 0 even when
        # there is a match.
        
        # Attempt an update (and ensure we affected something)
        #updated=(self.update(table_name,column_name,entity_name,settings) > 0)
            
        #if not updated:
        #   # Attempt an insert if not update occured (i.e no match)
        #    self.insert(table_name,settings)
        
        # Gak -- but see above.
        self.delete(table_name,column_name,entity_name)
        self.insert(table_name,settings)
            
        return
            
    def generateInsert(self,table_name,settings): 
        """ 
        Perform an SQL INSERT 
        """
        statement = "INSERT INTO %s.%s (" % (self.database, table_name)
        keys=settings.keys()
        statement += ", ".join(keys)
        statement += ") VALUES ("
        statement += ", ".join([str(settings[key]) for key in keys])
        statement += ")"
        return statement
        
    def insert(self,table_name,settings): 
        """       
        Take a dictionary of settings (column names/types) and 
        perform an insert.        
        """
        statement=self.generateInsert(table_name,settings)
        affected = 0
        cursor = None
        try:
            try:
                cursor = self.conn.cursor()
                log.debug('SQL: ' + statement)
                affected = cursor.execute(statement)   
                log.debug('SQL Affected: ' + `affected`)                        
            except Exception, details:
                if cursor: self.logWarnings(cursor)    
                log.error('SQL Error on [%s] : %s' % (statement, details), exc_info=1)
                raise
        finally:
            if cursor: cursor.close() 
        return affected 

    def generateUpdate(self,table_name,column_name,entity_name,settings): 
        """   
        Take a dictionary of settings (column names/types) and 
        generate an update statement. Note: The index is a single name.        
        """
        statement = "UPDATE %s.%s SET " % (self.database, table_name)
        keys=settings.keys()
        keys.remove(column_name)
        statement += ", ".join([key + '=' + str(settings[key]) for key in keys])
        statement += " WHERE %s='%s'" % (column_name, entity_name)
        return statement
            
    def update(self,table_name,column_name,entity_name,settings): 
        """   
        Take a dictionary of settings (column names/types) and 
        perform an update. Note: The index is a single name.        
        """
        statement = self.generateUpdate(table_name,column_name,entity_name,settings)
        affected = 0
        cursor = None
        try:
            try:
                cursor = self.conn.cursor()
                log.debug('SQL: ' + statement)
                affected = cursor.execute(statement)  
                log.debug('SQL Affected: ' + `affected` + ':' + `result`)
            except Exception, details:
                if cursor: self.logWarnings(cursor)    
                log.error('SQL Error on [%s] : %s' % (statement, details), exc_info=1)
                raise              
        finally:
            if cursor: cursor.close() 
        return affected 

    def generateDelete(self,table_name,column_name,entity_name):       
        """ 
        Perform an SQL DELETE 
        Index is single name
        """
        statement = "DELETE FROM %s.%s WHERE %s='%s'" \
                        % (self.database, table_name, column_name, entity_name)
        return statement

    def delete(self,table_name,column_name,entity_name):       
        """ 
        Perform an SQL DELETE 
        Index is single name
        """
        statement = self.generateDelete(table_name,column_name, entity_name)
        affected = 0
        cursor = None
        try:
            try:
                cursor = self.conn.cursor()
                log.debug('SQL: ' + statement)
                affected = cursor.execute(statement)       
                log.debug('SQL Affected: ' + `affected`)              
            except Exception, details:
                if cursor: self.logWarnings(cursor)    
                log.error('SQL Error on [%s] : %s' % (statement, details), exc_info=1)
                raise                
        finally:
            if cursor: cursor.close()     
        return affected 
        
    def logWarnings(self,cursor):
        if cursor.messages:
            for (message, details) in cursor.messages:
                log.warning('SQL Warning:' + str(message) + ':' + str(details))
            
