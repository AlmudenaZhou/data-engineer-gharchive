# Index

- [Data Analysis](#data-analysis)
    - [Questions about the data](#questions-about-the-data)
    - [Potential data cleaning approaches for ID-Name columns](#potential-data-cleaning-approaches-for-id-name-columns)
    - [Final transformations](#final-transformations)
- [Spark](#spark)
    - [Steps](#steps)
    - [How to use](#how-to-use)
        - [Dataproc in Google Cloud](#dataproc-in-google-cloud)
        - [Local](#local)

# Data Analysis

In this phase, I conducted an analysis of the data to formulate questions and determine the most suitable transformations based on the data schema and business requirements.

## Questions about the data:

- **Top contributors?** Columns needed: actor_id / actor_login
- **Distribution of event types** Columns needed: type
- **Total number of events** Columns needed: any column

## Potential data cleaning approaches for ID-Name columns:

Here, I discuss the specific case of `actor_login` and `actor_id`, which can be generalized to `org_login`-`org_id` and `repo_name`-`repo_id`.

1. **Creation of a new column using the last `actor_login` for the `actor_id`**
    
    Pros:
    - Mitigates issues with renamed users, ensuring consistency
    - IDs tend more stable over time
    - Simplifies report/dashboard creation by providing a direct conversion
    - Avoids the need for maintaining separate tables for events and users.

    Cons:
    - Adds complexity compared to using the `actor_login` or `actor_id`
    - May introduce complications with backward compatibility, requiring updates to previous records if a user changes their name
    - Scalability problems

1. **Usage of `actor_id` or `actor_login`** (`actor_id` more stable but less interpretable and `actor_login` less stable but more interpretable):

    Pros:
    - Simplicity

    Cons:
    - Potential bias in the data

1. Creation of a table, mapping `actor_id` to the last `actor_login`

    Pros:
    - Offers the most flexibility
    - Solves the backwards compatibility issues
    - Only requires updates for renamed users and inserts for new ones

    Cons:
    - Requires managing two tables
    - Increases storage requirements
    - Additional step of joining tables is necessary to achieve the desired format


Conclusions:

1. If queries are limited to a predefined time range and avoiding bias is crucial, creating a new column can effectively mitigate bias without scalability concerns
2. For less critical results or internal reports, `actor_login` may suffice, while `actor_id` can be used for more robust analysis.
3. In larger projects, maintaining an intermediate table with comprehensive actor information might be beneficial, but it entails additional costs and maintenance


For this project, **I adopted the first approach of creating a new column**:
- Scalability isn't a concern for this one-time dashboard
- Although the second option is superior, I wanted to practice Spark skills.
- The third option involves extra costs and maintenance, which I prefer to avoid.

## Final transformations:

- Drop the payload and other columns due to their unstable key structure
- Eliminate columns irrelevant to the analysis
- Rename the created_at column to action_time
- Add a new column `created_at` with the current timestamp
- Implement new columns for the last name associated with each ID:
    - `last_actor_login` with the last `actor_login` for each `actor_id`
    - `last_org_login` with the last `org_login` for each `org_id`
    - `last_repo_name` with the last `repo_name` for each `repo_id`

# Spark

## Steps:

1. Load the data from the parquet_folder using wildcards for the desired period (Google Storage or locally)
2. Implement the [Final transformations](#final-transformations) to create a new table.
3. Save the new table (BigQuery or locally). The table is partitioned by action_time to accommodate the data retrieved over time intervals. Additionally, it's clustered by last_actor_login to facilitate user-based analysis.


## How to use:

### DataProc in Google Cloud

1. Access the Google Cloud Portal and enable the Dataproc API.
1. Create a cluster. I utilized a Computer Engine for this step.
1. Create a job and fill the fields

For detailed instructions, refer to this video: [Connecting Spark to Big Query](https://www.youtube.com/watch?v=HIm2BOj8C0Q&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=69)


### Local

**Setup**:

Make sure you have the following jars installed and saved in the jars folder within the Spark directory:
- `spark-bigquery-with-dependencies`
- `google-api-client`
- `gcs-connector-hadoop3`


Run the Python script \_\_main__.py with the following arguments:
- `--input (-i)`: path (wildcards can be used) where your data is located
- `--output (-o)`: project_id.dataset_id.table where the data will be saved. The projec_id and the dataset_id(`bq_dataset_name`) must match those specified in the `variables.tf` file in the Terraform folder. The table must not exist.

Note: The temporary folder needed is set as the generic Google Storage bucket gharchive_capstone_project. However, it would be cleaner to create a dedicated bucket. Ensure the Google Storage bucket is already created at runtime.
