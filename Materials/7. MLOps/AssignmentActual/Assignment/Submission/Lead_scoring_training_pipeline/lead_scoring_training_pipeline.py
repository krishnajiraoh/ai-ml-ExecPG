##############################################################################
# Import necessary modules
# #############################################################################
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta

import importlib.util

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

utils = module_from_file("utils", "airflow/dags/Lead_scoring_training_pipeline/utils.py")
constants = module_from_file("constants", "airflow/dags/Lead_scoring_training_pipeline/constants.py")


###############################################################################
# Define default arguments and DAG
# ##############################################################################
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


ML_training_dag = DAG(
                dag_id = 'Lead_scoring_training_pipeline',
                default_args = default_args,
                description = 'Training pipeline for Lead Scoring System',
                schedule_interval = '@monthly',
                catchup = False
)

###############################################################################
# Create a task for encode_features() function with task_id 'encoding_categorical_variables'
# ##############################################################################
op_encoding_categorical_variables = PythonOperator(task_id='encoding_categorical_variables', 
                            python_callable=utils.encode_features,
                            op_kwargs={'db_path': constants.DB_PATH , 'db_file_name': constants.DB_FILE_NAME,
                                      'ONE_HOT_ENCODED_FEATURES': constants.ONE_HOT_ENCODED_FEATURES, 'FEATURES_TO_ENCODE' : constants.FEATURES_TO_ENCODE},
                            dag=ML_training_dag)

###############################################################################
# Create a task for get_trained_model() function with task_id 'training_model'
# ##############################################################################
op_training_model = PythonOperator(task_id='training_model', 
                            python_callable=utils.get_trained_model,
                            op_kwargs={'db_path': constants.DB_PATH , 'db_file_name': constants.DB_FILE_NAME},
                            dag=ML_training_dag)


###############################################################################
# Define relations between tasks
# ##############################################################################
op_encoding_categorical_variables.set_downstream(op_training_model)