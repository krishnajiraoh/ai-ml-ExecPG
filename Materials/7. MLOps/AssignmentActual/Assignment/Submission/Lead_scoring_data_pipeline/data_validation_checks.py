"""
Import necessary modules
############################################################################## 
"""

import pandas as pd
import sqlite3

###############################################################################
# Define function to validate raw data's schema
# ############################################################################## 

def raw_data_schema_check(DATA_DIRECTORY,raw_data_schema):
    '''
    This function check if all the columns mentioned in schema.py are present in
    leadscoring.csv file or not.

   
    INPUTS
        DATA_DIRECTORY : path of the directory where 'leadscoring.csv' 
                        file is present
        raw_data_schema : schema of raw data in the form oa list/tuple as present 
                          in 'schema.py'

    OUTPUT
        If the schema is in line then prints 
        'Raw datas schema is in line with the schema present in schema.py' 
        else prints
        'Raw datas schema is NOT in line with the schema present in schema.py'

    
    SAMPLE USAGE
        raw_data_schema_check
    '''
    df = pd.read_csv(f"{DATA_DIRECTORY}",index_col=[0])
        
    if set(df.columns) == set(raw_data_schema):
        print("Raw datas schema is in line with the schema present in schema.py")
    else:
        print("Raw datas schema is NOT in line with the schema present in schema.py")
   

###############################################################################
# Define function to validate model's input schema
# ############################################################################## 

def model_input_schema_check(DB_FILE_NAME,DB_PATH,model_input_schema):
    '''
    This function check if all the columns mentioned in model_input_schema in 
    schema.py are present in table named in 'model_input' in db file.

   
    INPUTS
        DB_FILE_NAME : Name of the database file
        DB_PATH : path where the db file should be present
        model_input_schema : schema of models input data in the form oa list/tuple
                          present as in 'schema.py'

    OUTPUT
        If the schema is in line then prints 
        'Models input schema is in line with the schema present in schema.py'
        else prints
        'Models input schema is NOT in line with the schema present in schema.py'
    
    SAMPLE USAGE
        raw_data_schema_check
    '''
    
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
    df = pd.read_sql('select * from interactions_mapped', cnx)
    
    print(df.columns)
    print(model_input_schema)
    
    flag = all(item in df.columns for item in model_input_schema)
    if flag == True:
        print('Models input schema is in line with the schema present in schema.py')
    else:
        print('Models input schema is NOT in line with the schema present in schema.py')
        
    
    
