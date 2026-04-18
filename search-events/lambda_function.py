import json
import boto3
import time
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Events')

cache = {}
CACHE_TTL = 60

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters') or {}
        genre = query_params.get('genre')
        name = query_params.get('name')
        
        cache_key = f"search_{genre}_{name}"
        current_time = time.time()
        
        if cache_key in cache:
            cached_data = cache[cache_key]
            if current_time - cached_data['timestamp'] < CACHE_TTL:
                print(f"CACHE HIT: Returning cached search results for key {cache_key}")
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'X-Cache': 'HIT'
                    },
                    'body': json.dumps(cached_data['data'])
                }
        
        print(f"CACHE MISS: Querying DynamoDB for key {cache_key}")
        start_time = time.time()
        
        if genre:
            response = table.scan(
                FilterExpression=Attr('genre').eq(genre)
            )
        elif name:
            response = table.scan(
                FilterExpression=Attr('name').contains(name)
            )
        else:
            response = table.scan()
        
        db_duration = time.time() - start_time
        items = response['Items']
        
        for item in items:
            for key, value in item.items():
                if str(type(value)) == "<class 'decimal.Decimal'>":
                    item[key] = str(value)
        
        cache[cache_key] = {
            'data': items,
            'timestamp': current_time
        }
        
        print(f"CACHE MISS: DynamoDB query took {db_duration:.3f}s. Result cached.")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-Cache': 'MISS'
            },
            'body': json.dumps(items)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
