import zlib
import pandas as pd
import json


def compressed_data_to_list_of_dicts(compressed_data):
    decompressed_data = zlib.decompress(compressed_data, 16 + zlib.MAX_WBITS)

    decoded_lines = decompressed_data.decode('utf-8').split('\n')
    decoded_lines = filter(lambda x: x != '', decoded_lines) 

    json_decoded_lines = [json.loads(line) for line in decoded_lines]
    return json_decoded_lines


def convert_to_df(json_decoded_lines):
    df = pd.DataFrame(json_decoded_lines)

    df.created_at = pd.to_datetime(df.created_at)
    return df



def expand_dictionary_df_columns(df, dict_cols):
    expanded_data = {}
    for col in dict_cols:
        ind_col_df = df[col].apply(pd.Series, dtype='object')
        ind_col_df = ind_col_df.add_prefix(col + '_') 
        expanded_data.update(ind_col_df)

    expanded_df = pd.DataFrame(expanded_data)

    not_dict_cols_df = df.loc[:, ~df.columns.isin(dict_cols)]
    result_df = pd.concat([not_dict_cols_df, expanded_df], axis=1)

    return result_df
