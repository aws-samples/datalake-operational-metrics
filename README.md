## Introduction

Over the last number of years, enterprises have accumulated so muchmassive amounts of data.
Data volumes have increased at an unprecedented rate, exploding from terabytes to petabytes and
sometimes exabytes of data. Increasingly, many enterprises are building highly scalable,
available, secure, and flexible data lakes on AWS that can handle extremely large datasets. After
data lakes are productionized, to measure the efficacy of the data lake and communicate the gaps
or accomplishments to the business groups, enterprise data teams need tools to extract
operational insights from the data lake solution. Those insights help answer key questions such
as:
* when was the last time a table was updated 
* what is the total table count in each of my database 
* what is the projected growth of a given table 
* what is the most frequently queried table vs least queried tables etc.

![Dashboard](/2_assets/dashboard.png)

## Deploy your resources
To make it easier to get started, we created a CloudFormation template that automatically sets up a few key components of the solution: 

*	An AWS Glue job (Python program) that is triggered based on a schedule
*	The AWS Identity and Access Management (IAM) role required by the AWS Glue job so the job can collect and store details about databases and tables in the Data Catalog
*	A new S3 bucket for the AWS Glue job to store the data files
*	A new database in the Data Catalog for storing our metrics data tables

The source code for the AWS Glue job and the CloudFormation template are available in the GitHub repo.

You must first download the AWS Glue Python code from GitHub and upload it to an existing S3 bucket. The path of this file needs to be provided when running the CloudFormation stack. 

Launch the stack using cloudformation [script:](/0_cloudformation/dataCollector.yaml)

## Solution Overview

![Architecture](/2_assets/arch.png)

* A Data collector python [program](/1_python_glue_job/dataLakeDataCollector.py) executes on schedule and collects metadata details about databases and tables from the enterprise data catalog. 
* Following key data attributes are collected for each table and database in your Glue data catalog.
![Data_Fields](/2_assets/data_fields.png)

* The program reads each tables file location and computes 
  * Number of files on s3
  * Size on S3 (in MB)
* All of this data for tables and databases is stored in s3 bucket for downstream analysis. 
* The program executes every day and creates new files partitioned by year, month and day on s3. 
* We will crawl the above data created in step 4 using a Glue Crawler.
* The Glue crawler creates external database and tables for our generated dataset for downstream analysis.
* Using Amazon Athena, we can query the extracted data.
* We will use Amazon QuickSight to build our Operational Metrics Dashboard and gain insights on our Data Lake. 

Note: For simplicity, this program crawls and collects data from the catalog for us-east-1 region only. 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

