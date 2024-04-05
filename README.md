# data-engineer-gharchive

## Problem Statement

I will be using the data from: https://www.gharchive.org/ to get stadistics of the commits and actions performed on github in a determined datetime. The pipeline will be prepared to perform the etl and the spark process from Google Storage to BigQuery in batch to data stored as well as in "real-time" with hourly triggers.

The stadistical analysis will be done afterwards, considering the data we have at the moment.

Steps:

1. Download the data from the provided link
2. Clean the data structure and homogenize the data following a predefined schema
3. Save the data into a parquet file at a GCS bucket
4. Structure the data with pyspark into a BigQuery table
5. Analyze the BigQuery data in Looker Studio

Extra considerations:
- Steps 1-3 will be orchestrated using Mage and will be considered as the ETL phase.
- All Google Cloud infrastructure will be handled by Terraform (IaC)
- The batch data has been run at 2015-01-01 to 2015-01-03 instead of more current data due to storage, computation, time and costs.
 
## Google credentials

For all the cloud-based steps you will need the credentials.json as secrets.json 

You can see how to download it here: https://cloud.google.com/iam/docs/keys-create-delete

## ETL

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

This will perform the ETL phase.

Setup and notes in: [Mage Setup](mage-gharchive-etl-orchestration/README.md)

For the data in bulk, backfilled has been used. The calls were made individually and dependent of the env variable execution_date to be able to backfill dates we did not have. 

To download data hourly, I have set a trigger hourly that will run the pipeline automatically.

## Terraform

For this proyect we need:

- Mage terraform module to run the ETL through a Cloud Run: https://github.com/mage-ai/mage-ai-terraform-templates/tree/master/gcp-dev
- Google Storage
- Table in BigQuery

If you want to run this by yourself:
- Change the project-id and the variables in every variables.tf
- Ensure you have the credentials in the path of the credentials variable.
- After running the `terraform apply`:
  - Allow unauthenticated users to invoke the service manually: Security => Authentication => 
Allow unauthenticated invocations
  - Networking => Ingress Control => All
  - Add in settings => Git config 

Notes:
- If you are using a free account in GCP, you need to delete load_balancer.tf and output service_ip in the main.tf in the mage module. I have deleted them.
- If the credentials in the variables.tf fails, add the credentials to your computer by running at the terminal:
`export GOOGLE_APPLICATION_CREDENTIALS="secrets.json"`
- If the sql database is created and deleted, you have to wait before you can use the same name again (Error 409) => Change the name in the db.tf google_sql_database_instance name.
- The volume secrets and iam user has been commented due to lack of permissions in the role gcp
- For the apply and the destroy, maybe you will need to run multiple times waiting a bit between each run to give time to deploy/delete the resources dependent on each other.


## Next steps

- The data does not change backwards => check if the parquet already exist before running the pipeline.
- Review latency in the data from the last hour. Run the query at 00?
- Mage CI: 
  - Github actions: https://docs.mage.ai/production/ci-cd/local-cloud/github-actions
  - Github Sync
- Path docker image: "region-docker.pkg.dev/project_id/repository_name/mageai"
- Run a spark job automatically with dataproc and google scheduler in google cloud