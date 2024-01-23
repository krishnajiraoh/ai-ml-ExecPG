##############################################################################
# Import necessary modules
# #############################################################################

from airflow import DAG
from airflow.operators.python import PythonOperator

import importlib.util

from datetime import datetime, timedelta

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

utils = module_from_file("utils", "airflow/dags/Lead_scoring_data_pipeline/utils.py")
constants = module_from_file("constants", "airflow/dags/Lead_scoring_data_pipeline/constants.py")
data_validation_checks = module_from_file("data_validation_checks", "airflow/dags/Lead_scoring_data_pipeline/data_validation_checks.py")
schema = module_from_file("schema", "airflow/dags/Lead_scoring_data_pipeline/schema.py")

significant_categorical_level = module_from_file("significant_categorical_level", "airflow/dags/Lead_scoring_data_pipeline/mapping/significant_categorical_level.py")
city_tier_mapping = module_from_file("city_tier_mapping", "airflow/dags/Lead_scoring_data_pipeline/mapping/city_tier_mapping.py")


###############################################################################
# Define default arguments and DAG
# ##############################################################################

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


ML_data_cleaning_dag = DAG(
                dag_id = 'Lead_Scoring_Data_Engineering_Pipeline',
                default_args = default_args,
                description = 'DAG to run data pipeline for lead scoring',
                schedule_interval = '@daily',
                catchup = False
)

###############################################################################
# Create a task for build_dbs() function with task_id 'building_db'
# ##############################################################################
op_create_db = PythonOperator(task_id='building_db', 
                            python_callable=utils.build_dbs,
                            op_kwargs={'db_path': constants.DB_PATH , 'db_file_name': constants.DB_FILE_NAME},
                            dag=ML_data_cleaning_dag)

###############################################################################
# Create a task for raw_data_schema_check() function with task_id 'checking_raw_data_schema'
# ##############################################################################
op_checking_raw_data_schema = PythonOperator(task_id='checking_raw_data_schema', 
                            python_callable=data_validation_checks.raw_data_schema_check,
                            op_kwargs={'DATA_DIRECTORY': constants.DATA_DIRECTORY, 'raw_data_schema' : schema.raw_data_schema},
                            dag=ML_data_cleaning_dag)
###############################################################################
# Create a task for load_data_into_db() function with task_id 'loading_data'
# #############################################################################
op_loading_data = PythonOperator(task_id='loading_data', 
                            python_callable=utils.load_data_into_db,
                            op_kwargs={'db_path': constants.DB_PATH , 'db_file_name': constants.DB_FILE_NAME, 'data_directory': constants.DATA_DIRECTORY },
                            dag=ML_data_cleaning_dag)

###############################################################################

# Create a task for map_city_tier() function with task_id 'mapping_city_tier'
# ##############################################################################
op_mapping_city_tier = PythonOperator(task_id='mapping_city_tier', 
                            python_callable=utils.map_city_tier,
                            op_kwargs={'db_path': constants.DB_PATH , 'db_file_name': constants.DB_FILE_NAME, 'city_tier_mapping': city_tier_mapping.city_tier_mapping },
                            dag=ML_data_cleaning_dag)

###############################################################################
# Create a task for map_categorical_vars() function with task_id 'mapping_categorical_vars'
op_mapping_categorical_vars = PythonOperator(task_id='mapping_categorical_vars', 
                            python_callable=utils.map_categorical_vars,
                            op_kwargs={'db_path': constants.DB_PATH , 'db_file_name': constants.DB_FILE_NAME, 'list_platform': significant_categorical_level.list_platform, 'list_medium': significant_categorical_level.list_medium, 'list_source': significant_categorical_level.list_source },
                            dag=ML_data_cleaning_dag)

# ##############################################################################

###############################################################################
# Create a task for interactions_mapping() function with task_id 'mapping_interactions'
op_mapping_interactions = PythonOperator(task_id='mapping_interactions', 
                            python_callable=utils.interactions_mapping,
                            op_kwargs={'db_path': constants.DB_PATH , 'db_file_name': constants.DB_FILE_NAME, 'INTERACTION_MAPPING': constants.INTERACTION_MAPPING, 'INDEX_COLUMNS_TRAINING': constants.INDEX_COLUMNS_TRAINING, 'INDEX_COLUMNS_INFERENCE': constants.INDEX_COLUMNS_INFERENCE, 'NOT_FEATURES' : constants.NOT_FEATURES },
                            dag=ML_data_cleaning_dag)
# ##############################################################################

###############################################################################
# Create a task for model_input_schema_check() function with task_id 'checking_model_inputs_schema'
op_checking_model_inputs_schema = PythonOperator(task_id='checking_model_inputs_schema', 
                            python_callable=data_validation_checks.model_input_schema_check,
                            op_kwargs={'DB_PATH': constants.DB_PATH , 'DB_FILE_NAME': constants.DB_FILE_NAME, 'model_input_schema': schema.model_input_schema },
                            dag=ML_data_cleaning_dag)
# ##############################################################################

###############################################################################
# Define the relation between the tasks
# ##############################################################################

op_create_db.set_downstream(op_checking_raw_data_schema)
op_checking_raw_data_schema.set_downstream(op_loading_data)
op_loading_data.set_downstream(op_mapping_city_tier)
op_mapping_city_tier.set_downstream(op_mapping_categorical_vars)
op_mapping_categorical_vars.set_downstream(op_mapping_interactions)
op_mapping_interactions.set_downstream(op_checking_model_inputs_schema)
