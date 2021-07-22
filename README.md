## Introduction

Over the last number of years, enterprises have accumulated so much of data. Data volumes have increased at an unprecedented rate,
exploding from terabytes to petabytes and sometimes exabytes of data. Increasingly many enterprises are building highly scalable, 
available, secure, and flexible Data Lakes on AWS, that can handle extremely large data sets. Once data lakes are productionized, 
to measure the efficacy of the data lake and communicate the gaps or accomplishments to the business groups, enterprise data teams 
are looking for tools to extract operational insights from the data lake solution. 
Those insights help answer key questions such as 
* when was the last time a table was updated 
* what is the total table count in each of my database 
* what is the projected growth of a given table 
* what is the most frequently queried table vs least queried tables etc.

![Dashboard](/2_assets/dashboard.png)

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

