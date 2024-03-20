import argparse

from complete_pipeline import clean_data_pipeline
from to_parquet import load_to_parquet


def main(params):
    year = int(params.year)
    month = int(params.month)
    day = int(params.day)
    hour = int(params.hour)

    clean_data_pipeline(year, month, day, hour, load_data_function=load_to_parquet)
    



if __name__ == '__main__':

    # --year=2015 --month=1 --day=1 --hour=15
    parser = argparse.ArgumentParser(description='etl ghdata to parquet')

    parser.add_argument('--year', required=True, help='year at the created_at')
    parser.add_argument('--month', required=True, help='month at the created_at')
    parser.add_argument('--day', required=True, help='day at the created_at')
    parser.add_argument('--hour', required=True, help='hour at the created_at')

    args = parser.parse_args()

    main(args)
