def load_to_parquet(cleaned_df, year, month, day, hour):
    cleaned_df.to_parquet(f'data/{year}-{month:02d}-{day:02d}-{hour}.parquet')
