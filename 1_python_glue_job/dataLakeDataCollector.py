import sys
from awsglue.utils import getResolvedOptions
import logging
import boto3
from botocore.exceptions import ClientError
from datetime import date, datetime, timedelta

s3_client = boto3.client('s3')
glue_client = boto3.client('glue')

args = getResolvedOptions(sys.argv, ['s3_output_bucket'])

AWS_S3_BUCKET = args['s3_output_bucket']

def getTableS3Details(s3loc):
    
    try:

        if s3loc.find("s3://") == -1:
            s3Details = {"sizeInMB": 0, "totalFiles": 0}
        else:
            
            bucket, key = s3loc.replace("s3://", "").split("/", 1)
            
            s3 = boto3.resource('s3')
            my_bucket = s3.Bucket(bucket)
            total_size = 0
            files = 0
            for obj in my_bucket.objects.filter(Prefix=key):
                total_size = total_size + obj.size
                files += 1
        
            sizeInMB = total_size/(1024*1024)
            
            s3Details = {"sizeInMB": sizeInMB, "totalFiles": files}
            
        return s3Details
    
    except ClientError as e:
        logging.error(e)
        return False    
 
def writeToS3(tables_data, filetype):

        todays_date = date.today()
        key = "datalake/"+filetype+'/'+'year='+str(todays_date.year)+'/'+'month='+str(todays_date.month)+'/'+'day='+str(todays_date.day)+'/'+filetype+".csv"
        
        response = s3_client.put_object(
            Bucket=AWS_S3_BUCKET, Key=key, Body=tables_data
        )
    
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    
        if status == 200:
            print(f"Successful S3 put_object response. Status - {status}")
        else:
            print(f"Unsuccessful S3 put_object response. Status - {status}")
            

def getTablesData(database_name, region=None):
    
    # list tables
    try:
        # default region : us-east-1
        if region is None:
           
            tableDetails = glue_client.get_tables(
                DatabaseName=database_name)
            
            tableList = tableDetails["TableList"]
            
            i=0
            
            table_data=''
            while i < len(tableList):
                table = tableList[i]
                tableName = table['Name']
                databaseName = table['DatabaseName']
                
                owner=''
                checkOwnerElement = table.get("Owner")
                if checkOwnerElement is not None:
                    owner = table.get("Owner")
                
                createTime =''
                createTimeElement = table.get('CreateTime')
                if createTimeElement is not None:
                    createTime = table['CreateTime']
                    createTime = createTime.strftime("%y/%m/%d %H:%M:%S")
                else :
                    createTime = "70/01/01 00:00:00"
                   
                updateTime=''
                updateTimeElement = table.get('UpdateTime')
                if updateTimeElement is not None:
                    updateTime = table['UpdateTime']
                    updateTime = updateTime.strftime("%y/%m/%d %H:%M:%S")
                else :
                    updateTime = "70/01/01 00:00:00"
                   
                lastAccessTime=''
                checklastAccessTimeElement = table.get("LastAccessTime")
                if checklastAccessTimeElement is not None:
                    lastAccessTime = table['LastAccessTime']
                    lastAccessTime = lastAccessTime.strftime("%y/%m/%d %H:%M:%S")
                else :
                    lastAccessTime = "70/01/01 00:00:00"
                   
                tableType = table['TableType']
        
                retention = table['Retention']
                retention = str(retention)
        
                try:
                    createdBy = table['CreatedBy']
                except KeyError:
                    createdBy = "Unknown"
                
                try: 
                    crawler_name = table["Parameters"]["UPDATED_BY_CRAWLER"]
                except KeyError:
                    crawler_name = "Unknown"
            

                isRegisteredWithLakeFormation = table['IsRegisteredWithLakeFormation']
                isRegisteredWithLakeFormation = str(isRegisteredWithLakeFormation)
                
                storageDesc = table['StorageDescriptor']
                location = storageDesc['Location']
                
                tableS3Details = getTableS3Details(location) 
                
                if tableS3Details:
                    sizeInMB = tableS3Details['sizeInMB']
                    sizeInMB = str(sizeInMB)
                    totalFiles = tableS3Details['totalFiles']
                    totalFiles = str(totalFiles)
                else:
                    sizeInMB = "0"
                    totalFiles = "0"
                
                data = tableName+","+databaseName+","+owner+","+createTime+","+updateTime+","+lastAccessTime+","+tableType+","+retention+","+createdBy+","+isRegisteredWithLakeFormation+','+location+','+sizeInMB+','+totalFiles+','+crawler_name
                table_data = table_data + data + "\n"
                            
                i += 1
            return table_data

    except ClientError as e:
        logging.error(e)
        return False

def getDatabasesData(region=None):
    
    try:
        if region is None:
            glue_client = boto3.client('glue')
            
            databasesList = glue_client.get_databases()
            databasesList = databasesList['DatabaseList']
                
            i=0
            dbNameList = []
  
            while i < len(databasesList):
                databaseDetail = databasesList[i]
                dbName = databaseDetail['Name']
                dbNameList.append(dbName)
                
                i += 1
                
            i=0
            
            databases_data = "DatabaseName,CreateTime, SharedResource, SharedResourceOwner, SharedResourceDatabaseName, Location, Description" +"\n"
            tables_header_data = "TableName,DatabaseName,Owner,CreateTime,UpdateTime,LastAccessTime,TableType,Retention,CreatedBy,IsRegisteredWithLakeFormation,Location,SizeInMBOnS3,TotalFilesOnS3,CrawlerName"+"\n"
            tables_data = ''
            tables_data = tables_data + tables_header_data

            while i < len(dbNameList):
                
                database = glue_client.get_database(Name = dbNameList[i])
                
                database = database['Database']
             
                dbName = database['Name']
            
                sharedResource='No'
                sharedResourceOwner=''
                sharedResourceDatabaseName=''
                checkRemoteDatabase=database.get("TargetDatabase")
                if checkRemoteDatabase is not None:
                    sharedResource = 'Yes' 
                    targetDB = database['TargetDatabase']
                    sharedResourceOwner = targetDB['CatalogId']
                    sharedResourceDatabaseName = targetDB['DatabaseName']
                
                locationUri=''
                checkLocationUriElement = database.get("LocationUri")
                if checkLocationUriElement is not None:
                    locationUri = database['LocationUri']
                
                description=''
                descriptionElement = database.get("Description")   
                if descriptionElement is not None:
                    description = database['Description']
                
                createTime=''
                createTimeElement = database.get("CreateTime")
                if createTimeElement is not None:
                    createTime = database['CreateTime']
                    createTime = createTime.strftime("%y/%m/%d %H:%M:%S")
                
                tables_data=tables_data + getTablesData(dbName)
                
                data = dbName+","+createTime+","+sharedResource+","+sharedResourceOwner+","+sharedResourceDatabaseName+','+locationUri+","+description
                
                databases_data = databases_data + data + "\n"
                
                i += 1
            
            writeToS3(databases_data,'databases')
            writeToS3(tables_data,'tables')
           
    except ClientError as e:
        logging.error(e)
        return False

getDatabasesData()
