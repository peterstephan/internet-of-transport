###################################################################################
####
#### Title:       Google Maps Distance Matrix API to AWS S3 Bucket
#### 
#### Description: This Python script is developed to be used in an AWS Lambda to
####              get travel time data from the Google Maps Distance Matrix API
####              on a scheduled (cron) basis
####
#### AWS Lambda settings:
####    trigger:  setup a CloudWatch event on a schedule basis, say every 5/10/15/30/60 minutes etc
####    runtime:  Python 2.7
####    handler:  google_dm_api_to_aws_s3.save_to_bucket
####
###################################################################################

import boto3 # Boto is the Amazon Web Services (AWS) SDK for Python
import json
import logging
from botocore.vendored import requests ## Boto requests (URL request) library
from datetime import datetime
from datetime import timedelta

def save_to_bucket(event, context):
    # Get date-time in current time zone
    time_zone = 10 # Brisbane UTC +10:00 hours - change this to your time zone
    date_time_now = datetime.now() + timedelta(hours=time_zone) # Get current date-time in local time zone
    date_time_now_str = str(date_time_now) # convert to a Python string
    
    ## Re-format the datetime
    dt_str = date_time_now_str[:16] #left 16 characters
    dt_str = dt_str.replace(' ','') # replace spaces with nothing (i.e. remove spaces)
    dt_str = dt_str.replace(':','') # replace : with nothing (i.e. remove : characters)
    dt_str = dt_str.replace('-','') # resulting format: yyyymmddhhmm
    
    ## Google Maps API key
    google_api_key = "YOUR_API_KEY" # Register for a Google Maps API Key and insert it here. Link: https://cloud.google.com/maps-platform/

    ## Construct the URL to query
    # Refer to here for documentation on the Google Maps Distance Matrix API:
    # https://developers.google.com/maps/documentation/distance-matrix/start
    # Example URL: https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=Washington,DC&destinations=New+York+City,NY&key=YOUR_API_KEY
    google_maps_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?' # JSON API response used (not XML)
    google_maps_url += '&origins=Camp+Hill,QLD,Australia' #Origin set to Camp Hill, QLD, Australia
    google_maps_url += '&destinations=Brisbane+CBD,QLD,Australia' # Destination set to Brisbane CBD, QLD, Australia
    google_maps_url += '&units=metric' # Metric or Imperial
    google_maps_url += '&departure_time=now' # Departure time set as the current time (now)
    google_maps_url += '&mode=driving' # Other options: driving, walking, bicycling, transit
    google_maps_url += '&traffic_model=best_guess' # Other options: pessimistic, optimistic
    google_maps_url += '&key=' + google_api_key # Your API key will be included in the URL here

    ## AWS CloudWatch Logger
    # Used to log some information in AWS CloudWatch
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('google_maps_url: {}'.format(google_maps_url))
    
    ## Query (request) the data from the URL
    result = requests.get(google_maps_url)
    
    ## Parse the URL response into a Python JSON Object
    jsonstr = result.content
    jsonobj = json.loads(jsonstr)
    
    ## Extract out the data elements of interest
    request_status = jsonobj['status']
    origin_address = jsonobj['origin_addresses'][0]
    origin_address = origin_address.replace(',','')
    destination_address = jsonobj['destination_addresses'][0]
    destination_address = destination_address.replace(',','')
    distance_value_m = float(jsonobj['rows'][0]['elements'][0]['distance']['value']) #units=metres
    distance_value_km = float(distance_value_m /1000) #units=km's
    
    ## Duration in Traffic
    # N.B. using "duration_in_traffic" field, NOT 'duration'.
    duration_value_sec = float(jsonobj['rows'][0]['elements'][0]['duration_in_traffic']['value']) #units=seconds
    duration_value_min = float(duration_value_sec / 60) #units=minutes
    duration_value_hr = float(duration_value_min / 60) #units=hours
    speed_kmph = float(distance_value_km / duration_value_hr)  #units=kilometers per hour
    
    ## CSV-formatted Data String
    # This generates a 2 row Comma Separated Value (CSV) formatted string with the data
    # CSV header row:
    string = "datetime,request_status,origin_address,destination_address,distance_km,duration_min,speed_kmph\n" # Note \n means new line
    # CSV data row:
    string += "{0},{1},{2},{3},{4},{5},{6}".format(dt_str,request_status,origin_address,destination_address,distance_value_km,duration_value_min,speed_kmph)
    encoded_string = string.encode("utf-8") # Encode the string utf-8

    ## S3 Bucket Details
    bucket_name = "S3_BUCKET_NAME"
    file_name = "log_"+ str(dt_str) +".txt" # filename is based on the datetime string yyyymmddhhmm
    s3_folder =  "google_travel_times/" # this can be changed to whatever S3 Bucket location you'd like
    s3_path = s3_folder + file_name

    ## Connect to S3 Bucket
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string)
    
    ## Return a response
    return {
        "statusCode": 200,
        "body": string
    }

