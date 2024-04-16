# data-engineer-gharchive

## Index

- [Problem Statement](#problem-statement)
- [Google credentials](#google-credentials)
- [ETL](#etl)
- [Mage orchestrator](#mage-orchestrator)
- [Terraform](#terraform)
- [Spark](#spark)
- [Dashboard and results](#dashboard-and-results)
- [Next steps](#next-steps)

## Problem Statement

I want to know the top contributors in a date and analyze the type of actions the users perform the most, apart from commits. 

For this, I used the data from [GH Archive](https://www.gharchive.org/), which stores information of all the events performed in GitHub, aggregated into hourly archives.

From the technical point of view, I need a more cleaned version of raw data in a data lake and processed data in a data warehouse that can be used to make the dashboard.

The pipeline needs to be prepared for performing the processing in batch, for historical data (days, months,...) and in "real-time" with hourly triggers.

All Google Cloud infrastructure has been handled using Terraform (IaC).

### Workflow summary:
1. ETL phase orchestrated with Mage:
    1. Download the data from the provided link 
    1. Clean the data structure and homogenize the data following a predefined schema
    1. Save the data into a parquet file at a GCS bucket
1. Structure the data with pyspark into a BigQuery table
1. Analyze the BigQuery data in Looker Studio

## Google credentials

For all the cloud-based steps, google requires credentials. Follow these steps to prepare them for the project:

1. Download credentials.json following the instructions here: https://cloud.google.com/iam/docs/keys-create-delete
1. Rename the json into `secrets.json`
1. Save it into the terraform folder

## ETL

To run manually the ETL, in the terminal from data-engineer-gharchive folder run:

`python etl --year=2015 --month=1 --day=1 --hour=15`

### Phases of the ETL:

1. Download last hour data from gharchive => .json.gzip [download_data.py](etl/download_data.py)
1. Compressed data to a list of dictionaries [transform_data](etl/transform_data.py)
1. List of dictionaries to dataframe [transform_data](etl/transform_data.py)
1. Columns with fixed json keys are expanded into more columns: ['actor', 'repo', 'org'] [transform_data](etl/transform_data.py)
1. Check and convert the input data into the predefined schema: [convert_data_to_schema](etl/convert_data_to_schema.py)
    1. Delete extra columns
    1. Add missing columns
    1. Check and change columns to dtype
1. Save it to parquet locally ([manual ETL](etl/__main__.py)) or into a GCS bucket ([mage ETL](https://github.com/AlmudenaZhou/mage-gharchive-etl-orchestration))

Note:
org_id is an integer that can be Null => Needs an integer nullable => pd.Int64Dtype() 

All the workflow in: [ETL notebook](etl/data_pipeline.ipynb)

## Mage orchestrator

This will perform the ETL phase.

Setup and notes in: [Mage Setup](mage-gharchive-etl-orchestration/README.md)

For the data in bulk, backfilled has been used. The calls were made individually and dependent of the env variable execution_date to be able to backfill dates we did not have. 

To download data hourly, I have set a trigger hourly that will run the pipeline automatically.
 

## Terraform

### Resources to deploy:

- Mage terraform module to run the ETL through a Cloud Run: https://github.com/mage-ai/mage-ai-terraform-templates/tree/master/gcp-dev
- Google Storage
- Table in BigQuery

### If you want to run this by yourself:
1. Change the project-id and the variables in every variables.tf
1. Ensure you have the credentials in the path of the credentials variable.
1. After running the `terraform apply`:
    1. Allow unauthenticated users to invoke the service manually: Security => Authentication => Allow unauthenticated invocations
    1. Networking => Ingress Control => All
    1. Add in settings => Git config 

### Notes:
- If you are using a free account in GCP, you need to delete load_balancer.tf and output service_ip in the main.tf in the mage module. I have deleted them.
- If the credentials in the variables.tf fails, add the credentials by running at the terminal:
`export GOOGLE_APPLICATION_CREDENTIALS="secrets.json"`
- If the sql database is created and deleted, you have to wait before you can use the same name again (Error 409) => Change the name in the db.tf google_sql_database_instance name.
- The volume secrets and iam user has been commented due to lack of permissions in the role gcp
- For the apply and the destroy, maybe you will need to run multiple times waiting a bit between each run to give time to deploy/delete the resources dependent on each other.

## Spark

I read the parquet files generated at the [ETL phase](#etl) at the Google Storage Bucket, transform it using pyspark and load it into a BigQuery table.

Transformations:
- Columns deletion
- New `created_at` column with the inserting datetime and renamed the previous one as `action_time`
- New columns with the last name for each id for actors, repositories and organizations

All the process, included the data analysis and why I chose that transformations, is documented [here](spark/README.md).


## Dasboard and results

In this phase, I used Looker Studio connected to the BigQuery table to create the dashboard.

![image](img/dashboard.png)

There are 218.9 mil events registered that day

The top category is PushEvent, or commits, by far from the second one, create a new repository.

We have the top 5 contributors: kinlane, KenanSulayman, mirror-updates, opencm and qdm.

The table `ACTION TYPE BY ACTOR` has the PushEvent type filtered. It shows some curious facts like opncm created and deleted several repositories that day.

## Next steps

- The data does not change backwards => check if the parquet already exist before running the pipeline.
- Review the latency in the data from the last hour to ensure minimal loss of information and minimal wait time to confirm data completion.
- Mage CI/CD: 
  - GitHub actions: https://docs.mage.ai/production/ci-cd/local-cloud/github-actions
  - GitHub Sync
- Path docker image: "region-docker.pkg.dev/project_id/repository_name/mageai"
- Run a spark job automatically with dataproc and google scheduler in google cloud hourly
- Check if the data has been already uploaded to the BigQuery table and avoid processing again if it exists.
