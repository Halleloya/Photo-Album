import boto3
import json
import os
import logging
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth

logger = logging.getLogger()
es_host = 'xxxxxxxxx'
es_index = 'photxx'
access_key = 'xxxxxxxxx'
secret_access_key = 'xxxxxxxxxxxxxxx'
#session_token = os.getenv('AWS_SESSION_TOKEN')
region = 'us-east-1'

# Create clients for AWS services
#rek_client = boto3.client('rekognition')

# Establish connection to ElasticSearch
auth = AWSRequestsAuth(aws_access_key=access_key,
                       aws_secret_access_key=secret_access_key,
                       #aws_token=session_token,
                       aws_host=es_host,
                       aws_region=region,
                       aws_service='es')

es = Elasticsearch(host=es_host,
                   port=443,
                   use_ssl=True,
                   connection_class=RequestsHttpConnection,
                   http_auth=auth)

#logger.info("{}".format(es.info()))
print ("es.info:", es.info())

def lambda_handler(event, context):
    """Lambda Function entrypoint handler

    :event: S3 Put event
    :context: Lambda context
    :returns: Number of records processed

    """
    print ("I am triggering 2...")
    processed = 0
    rek_client = boto3.client('rekognition')
    
    for record in event['Records']:
        s3_record = record['s3']

        key = s3_record['object']['key']
        bucket = s3_record['bucket']['name']
        ttamp = record['eventTime']
        print ("I am triggering 3...")
        resp = rek_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=3,
            MinConfidence=90)
        #response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':fileName}})
        print ("I am triggering 4...")    
        labels = []
        for l in resp['Labels']:
            labels.append(l['Name'])
        
        print ("labels are: ", labels)
        print ("es is: ", es)
        message = {'objectKey': key,'bucket': bucket, 'createdTimestamp': ttamp, 'labels': labels}
        print ("message is:", type(message), message)
        res = es.index(index=es_index, doc_type='event',
                       body = message,
                       id=key
                       )

        print ("res are: ", res)
        logger.debug(res)
        processed = processed + 1
        
    response2 = {
                    'statusCode': 200,
                    'headers': { 
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': "*" ,
                        'Access-Control-Allow-Methods': '*',
                        "Access-Control-Allow-Credentials" : True
                    },
                    'body': json.dumps(processed),
                    'isBase64Encoded': False
                }
    logger.info('Successfully processed {} records'.format(processed))
    print ("I am triggered")
    return response2