# Index

- [Simple Data Analysis](#simple-data-analysis)
    - [Possible useful questions for the data](#possible-useful-questions-for-the-data)
        - [Possibilities for the top contributors](#possibilities-for-the-top-contributors)
    - [Things to do](#things-to-do)
- [Spark](#spark)

# Simple Data Analysis

I will consider the schema and the questions I want to answer in the dashboard to plan the steps to perform in spark

## Possible useful questions for the data:

- **Top contributors?** Columns needed: actor_id / actor_login -> new column with the last actor_login for the actor_id?
- **N commits by hour?** Columns needed: type and created_at
- **N actions by hour?** Columns needed: any column and create_at
- **% organization by day?** Columns needed: org_id and created_at


### Possible cleaning for id-name columns:

I will describe the specific case of `actor_login` and `actor_id`, but will be extrapolated for `org_login`-`org_id` and `repo_name`-`repo_id`.

1. New column with the last `actor_login` for the `actor_id`?

    Pros:
    - Avoid problems with renamed users (we don't know if for the same `actor_id` always the same `actor_login`)
    - ids generally more stable
    - Easier in terms of using it for the report/dashboard. Direct conversion.
    - Easier than having two tables: one for the events and another for the users.

    Cons:
    - More complexity than using the `actor_login` or `actor_id`
    - Use the last one have problems with backwards compability. You have to change all the previous records if someone change their name.
    - Bad scalability

1. Return `actor_id` or `actor_login` (first more stable but less interpretable and the second less stable but more interpretable):

    Pros:
    - Most simple

    Cons:
    - Biased

1. Make another table with the `actor_id` - last `actor_login` (you need to join the tables for the dashboard)

    Pros:
    - Most flexible
    - Solves the backwards compatibility
    - Only needs to update renamed users and insert new ones

    Cons:
    - 2 tables
    - More storage
    - Having to join the tables afterwards to end up with the first table option


Conclusions:

1. If the majority of queries or the only one is to a table of a predefined time (not all the history) this can be a good option to avoid bias without having problems with the scalability. 
2. For results that the risk of being biased are not a problem (`actor_login`) or for an internal report where you can look for the name of the person afterwards (`actor_id`)
3. A more real project, having an intermediate table with all the actor information (inserting rows for new users and also for each updated information, user history) -> get the simplified table


In this project, I will use the **first approach**, new column.
- The scalability is not a problem, I will only run the dashboard once and for a few days of data. 
- I don't choose the 2 (`actor_login` or `actor_id`) because I want to practice a bit of Spark, but I consider that this would be the best option in this case. 
- I don't want the extra cost and maintenance of the third one.

## Things to do:

- drop the `payload` and `other` columns: json with unstable keys
- drop columns that are not useful for the analysis
- `created_at` changed the name to `action_time`
- Add new column `created_at` with the current timestamp
- new columns with the last name by id:
    - `last_actor_login` with the last `actor_login` for each `actor_id`
    - `last_org_login` with the last `org_login` for each `org_id`
    - `last_repo_name` with the last `repo_name` for each `repo_id`

# Spark

## Steps:

1. Load the data from the parquet_folder using wildcards for the period you want (Google Storage or locally)
2. Perform the [Things to do](#things-to-do) to create a new table
3. Save the new table (BigQuery or locally)


## How to use:

### DataProc in Google Cloud

1. Enter Google Cloud Console, Dataproc API and habilitate it.
1. Create a cluster. I create a Computer Engine.
1. Create a job filling correctly the fields

The complete steps are explain in this video: [Connecting Spark to Big Query](https://www.youtube.com/watch?v=HIm2BOj8C0Q&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=69)


### Local

**Setup**:
You need to have installed the following jars:
- spark-bigquery-with-dependencies
- google-api-client
- gcs-connector-hadoop3
And save them in the jars folder at the spark folder


run the python \__main.__.py with the args:
- `--input (-i)`: path (wildcards can be used) where your data is located
- `--output (-o)`: project_id.dataset_id.table where the data will be saved. The projec_id and the dataset_id(`bq_dataset_name`) has to be the same as the ones specified at `variables.tf` in the terraform folder. The table must not exist.

I left the temporary folder needed as the generic gs bucket gharchive_capstone_project, since it's already been created. However, it would be cleaner to create one specifically for that. Important, the gs bucket it must be already created at pyspark code runtime.
