import pandas as pd
import numpy as np

from convert_data_to_schema import convert_df_to_schema
from download_data import download_gharchive_data
from transform_data import compressed_data_to_list_of_dicts, convert_to_df, expand_dictionary_df_columns



def clean_data_pipeline(year, month, day, hour, load_data_function):
    extended_schema_dtypes = {
        'id': 'object', 
        'type': 'object', 
        'actor_id': np.int64,
        'actor_login': 'object',
        'actor_gravatar_id': 'object',
        'actor_avatar_url': 'object',
        'actor_url': 'object',
        'repo_id': np.int64,
        'repo_name': 'object', 
        'repo_url': 'object', 
        'payload': 'object', 
        'public': 'bool',
        'created_at': 'datetime64[ns, UTC]', 
        'org_id': pd.Int64Dtype(), 
        'org_login': 'object',
        'org_gravatar_id': 'object',
        'org_avatar_url': 'object',
        'org_url': 'object',
        'other': 'object'
        }
    dict_cols = ['actor', 'repo', 'org']

    compressed_data = download_gharchive_data(year, month, day, hour)
    json_decoded_lines = compressed_data_to_list_of_dicts(compressed_data)
    df = convert_to_df(json_decoded_lines)
    new_df = expand_dictionary_df_columns(df, dict_cols)
    cleaned_df = convert_df_to_schema(new_df, extended_schema_dtypes)
    load_data_function(cleaned_df, year, month, day, hour)
