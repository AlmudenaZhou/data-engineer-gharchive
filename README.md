# data-engineer-gharchive

## etl

To run manually the etl, in the terminal from data-engineer-gharchive folder run:

`python etl --year=2015 --month=1 --day=1 --hour=15`

Phases of the etl:
- Download last hour data from gharchive => .json.gzip
- Compressed data to a list of dictionaries
- List of dictionaries to dataframe
- Columns with fixed json keys are expanded into more columns: ['actor', 'repo', 'org']
- Check and convert the input data into the predefined schema:
  - Delete extra columns
  - Add missing columns
  - Check and change columns to dtype
- Save it to parquet locally (manual etl) or into a GCS bucket (mage etl)

Note:
org_id is an integer that can be Null => Needs an integer nullable => pd.Int64Dtype() 

All the workflow in: [ETL notebook](etl/data_pipeline.ipynb)

## Mage orchestrator

Setup and notes in: [Mage Setup](mage-gharchive-etl-orchestration/README.md)

For the data in bulk, backfilled has been used. The calls were made individually and dependent of the env variable execution_date to be able to backfill dates we did not have. 

To download data hourly, I have set a trigger hourly that will run the pipeline automatically.


## Next steps

- The data does not change backwards => check if the parquet already exist before running the pipeline.
- Review latency in the data from the last hour. Run the query at 00?
- Mage CI: 
  - Github actions: https://docs.mage.ai/production/ci-cd/local-cloud/github-actions 
