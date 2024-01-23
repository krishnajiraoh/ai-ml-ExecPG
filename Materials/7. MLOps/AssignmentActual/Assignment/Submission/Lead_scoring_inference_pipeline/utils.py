'''
filename: utils.py
functions: encode_features, load_model
creator: shashank.gupta
version: 1
'''

###############################################################################
# Import necessary modules
# ##############################################################################

import mlflow
import mlflow.sklearn
import mlflow.pyfunc
import pandas as pd

import sqlite3

import os
import logging

from datetime import datetime

from Lead_scoring_inference_pipeline.constants import *

###############################################################################
# Define the function to train the model
# ##############################################################################


def encode_features(db_file_name,db_path,ONE_HOT_ENCODED_FEATURES,FEATURES_TO_ENCODE):
    '''
    This function one hot encodes the categorical features present in our  
    training dataset. This encoding is needed for feeding categorical data 
    to many scikit-learn models.

    INPUTS
        db_file_name : Name of the database file 
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES : list of the features that needs to be there in the final encoded dataframe
        FEATURES_TO_ENCODE: list of features  from cleaned data that need to be one-hot encoded
        **NOTE : You can modify the encode_featues function used in heart disease's inference
        pipeline for this.

    OUTPUT
        1. Save the encoded features in a table - features

    SAMPLE USAGE
        encode_features()
    '''

    cnx = sqlite3.connect(db_path+db_file_name)
    df = pd.read_sql('select * from interactions_mapped', cnx)
    
    encoded_df = pd.DataFrame(columns=ONE_HOT_ENCODED_FEATURES )
    placeholder_df = pd.DataFrame()

    # One-Hot Encoding using get_dummies for the specified categorical features
    for f in FEATURES_TO_ENCODE:
        if(f in df.columns):
            encoded = pd.get_dummies(df[f])
            encoded = encoded.add_prefix(f + '_')
            print(encoded.columns)
            placeholder_df = pd.concat([placeholder_df, encoded], axis=1)
        else:
            print('Feature not found')
            return df

    # Implement these steps to prevent dimension mismatch during inference
    for feature in encoded_df.columns:
        if feature in df.columns:
            encoded_df[feature] = df[feature]
        if feature in placeholder_df.columns:
            encoded_df[feature] = placeholder_df[feature]
    # fill all null values
    encoded_df.fillna(0, inplace=True)
    
    encoded_df.drop(['app_complete_flag'],axis=1).to_sql(name='features', con=cnx,if_exists='replace',index=False)
    
###############################################################################
# Define the function to load the model from mlflow model registry
# ##############################################################################

def get_models_prediction(db_file_name,db_path,model_name, stage):
    '''
    This function loads the model which is in production from mlflow registry and 
    uses it to do prediction on the input dataset. Please note this function will the load
    the latest version of the model present in the production stage. 

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        model from mlflow model registry
        model name: name of the model to be loaded
        stage: stage from which the model needs to be loaded i.e. production


    OUTPUT
        Store the predicted values along with input data into a table

    SAMPLE USAGE
        load_model()
    '''
    
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)
    cnx = sqlite3.connect(db_path+db_file_name)
    
    with mlflow.start_run(run_name="predict") as run:
        loaded_model = mlflow.sklearn.load_model(model_uri=f"models:/{model_name}/{stage}")
        print(loaded_model)

        # Predict on a Pandas DataFrame.
        X = pd.read_sql('select * from features', cnx)
        predictions_proba = loaded_model.predict_proba(pd.DataFrame(X))
        predictions = loaded_model.predict(pd.DataFrame(X))
        pred_df = X.copy()

        pred_df['app_complete_flag'] = predictions
        pred_df[["Prob of app not complete flag","Prob of app_complete_flag"]] = predictions_proba

        pred_df.to_sql(name='predictions', con=cnx,if_exists='replace',index=False)

        print (pd.DataFrame(predictions_proba,columns=["Prob of app not complete flag","Prob of app_complete_flag"]).head()) 
        
        runID = run.info.run_uuid
        print("Inside MLflow Run with id {}".format(runID))


###############################################################################
# Define the function to check the distribution of output column
# ##############################################################################

def prediction_ratio_check(db_file_name,db_path):
    '''
    This function calculates the % of 1 and 0 predicted by the model and  
    and writes it to a file named 'prediction_distribution.txt'.This file 
    should be created in the ~/airflow/dags/Lead_scoring_inference_pipeline 
    folder. 
    This helps us to monitor if there is any drift observed in the predictions 
    from our model at an overall level. This would determine our decision on 
    when to retrain our model.
    

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be

    OUTPUT
        Write the output of the monitoring check in prediction_distribution.txt with 
        timestamp.

    SAMPLE USAGE
        prediction_col_check()
    '''
    
    cnx = sqlite3.connect(db_path+db_file_name)
    df = pd.read_sql('select * from predictions', cnx)
    
    perc_zeroes = 100 * (df['app_complete_flag'] == 0).sum() / df.shape[0]
    perc_ones = 100 * (df['app_complete_flag'] == 1).sum() / df.shape[0]
    
    text = f"Percentage of Zeroes:{perc_zeroes}, Percentage of Ones: {perc_ones}"
    
    with open('airflow/dags/Lead_scoring_inference_pipeline/prediction_distribution.txt', 'a') as f:
        f.write(text)
    
    
###############################################################################
# Define the function to check the columns of input features
# ##############################################################################


def input_features_check(db_file_name,db_path,ONE_HOT_ENCODED_FEATURES):
    '''
    This function checks whether all the input columns are present in our new
    data. This ensures the prediction pipeline doesn't break because of change in
    columns in input data.

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES: List of all the features which need to be present
        in our input data.

    OUTPUT
        It writes the output in a log file based on whether all the columns are present
        or not.
        1. If all the input columns are present then it logs - 'All the models input are present'
        2. Else it logs 'Some of the models inputs are missing'

    SAMPLE USAGE
        input_col_check()
    '''
    
    cnx = sqlite3.connect(db_path+db_file_name)
    df = pd.read_sql('select * from features', cnx)
    
    flag = all(item in ONE_HOT_ENCODED_FEATURES for item in df.columns)
    if flag == True:
        logging.info('All the models input are present')
    else:
        logging.info('Some of the models inputs are missing')
    
   
