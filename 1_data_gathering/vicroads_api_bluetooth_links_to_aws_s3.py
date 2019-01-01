###################################################################################
####
#### Title:       VicRoads Bluetooth Links API to AWS S3 Bucket
#### 
#### Description: This Python script is developed to be used in an AWS Lambda to
####              get Bluetooth travel time and congestion data from the VicRoads API
####              on a scheduled (cron) basis. http://api.vicroads.vic.gov.au/
####
#### AWS Lambda settings:
####    trigger:  setup a CloudWatch event on a scheduled basis, say every 5/10/15/30/60 minutes etc
####    runtime:  Python 2.7
####    handler:  vicroads_api_bluetooth_links_to_aws_s3.save_to_bucket
####
###################################################################################

import boto3
import csv
import json
import logging
from botocore.vendored import requests ## Boto requests (URL request) library
from datetime import datetime
from datetime import timedelta

def save_to_bucket(event, context):
    ## Get date-time in current time zone
    time_zone = 11 #Melbourne UTC +11:00 hours
    date_time_now = datetime.now() + timedelta(hours=time_zone)
    date_time_now_str = str(date_time_now)
    
    ## Re-format the date-time
    dt_str = date_time_now_str[:16]
    dt_str = dt_str.replace(' ','')
    dt_str = dt_str.replace(':','')
    dt_str = dt_str.replace('-','') #Fomrat: yyyymmddhhmm
    
    ## VicRoads API key
    vicroads_api_key = "YOUR_API_KEY"
    
    ## Construct URL to query
    """
    Docs: http://api.vicroads.vic.gov.au/#examples
    ----
    http://api.vicroads.vic.gov.au/vicroads/wfs?
    service=wfs&
    version=2.0.0&    - 1.1.0 or 2.0.0 are most widely used
    request=GetFeature&
    typeNames=vicroads:bluetooth_links&    - Layer name, separate multiple with comma
    outputformat=application/json&    - Also supports 'csv', 'shape-zip' (Shapefile), 'GML2', 'GML3'
    srsname=EPSG:4326&
    bbox=144.87,-38.64,145.64,-37.71&   - Optional bounding box filter
    cql_filter=congestion>5&    - Optional attribute or spatial filter using CQL
    sortby=reportedtime+D&    - Optional sort, +D (Descending) or +A (Ascending)
    count=10    - Optional, leave it off to return everything
    """
    url_to_query = 'http://api.vicroads.vic.gov.au/vicroads/wfs?'
    url_to_query += 'service=wfs&'
    url_to_query += 'version=2.0.0&' # 1.1.0 or 2.0.0 are most widely used
    url_to_query += 'request=GetFeature&'
    url_to_query += 'typeNames=vicroads:bluetooth_links&' # Layer name, separate multiple with comma
    url_to_query += 'outputformat=application/json&' # Supports 'application/json' 'csv', 'shape-zip' (Shapefile), 'GML2', 'GML3'
    url_to_query += 'srsname=EPSG:4326&'
    #url_to_query += 'bbox=144.87,-38.64,145.64,-37.71&' #Optional bounding box filter
    #url_to_query += 'cql_filter=congestion>5&' # Optional attribute or spatial filter using CQL
    #url_to_query += 'sortby=reportedtime+D&' # Optional sort, +D (Descending) or +A (Ascending)
    #url_to_query += 'count=4&' # Optional, leave it off to return everything
    url_to_query += 'AUTH=' + vicroads_api_key

    ## CloudWatch Logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('url_to_query: {}'.format(url_to_query))
    
    ## Query (request) the URL
    result = requests.get(url_to_query)
    
    ## Get JSON Response
    jsonstr = result.content
    jsonobj = json.loads(jsonstr)
    
    ## Parse out elements...
    jsonobj_features = jsonobj['features']
    string = "timestamp,linkid,name,direction,congestion,delay,excess_delay,travel_time,score,trend\n"
    for feature in jsonobj_features:
        timestamp = feature['properties']['timestamp'] 
        linkid = feature['properties']['linkid']
        name = feature['properties']['name']
        name = name.replace(",","")
        direction = feature['properties']['direction']
        congestion = feature['properties']['congestion'] 
        delay = feature['properties']['delay'] 
        excess_delay = feature['properties']['excess_delay'] 
        travel_time = feature['properties']['travel_time'] 
        score = feature['properties']['score'] 
        trend = feature['properties']['trend'].replace(",","|") #NB has commas in it so replace
        ## Concatenate the CSV string..
        string += str(timestamp) + ','
        string += str(linkid) + ',' 
        string += str(name) + ','  
        string += str(direction) + ',' 
        string += str(congestion) + ','  
        string += str(delay) + ','
        string += str(excess_delay) + ','
        string += str(travel_time) + ','
        string += str(score) + ','  
        string += str(trend) + ','  
        string += "\n"
        
    encoded_string = string.encode("utf-8")
    
    ## S3 Bucket Details
    bucket_name = "S3_BUCKET_NAME" # Update with your bucket name
    file_name = "bt_data_"+ str(dt_str) +".csv"
    s3_folder =  "vicroads_api/bluetooth_links/" # Update with your S3 folder
    s3_path = s3_folder + file_name

    ## Connect to S3 Bucket
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string) 
    
    ## Return a response
    return {
        "statusCode": 200,
        "body": string
    }
       
