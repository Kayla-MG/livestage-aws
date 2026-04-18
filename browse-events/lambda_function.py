import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Events')

cache = {}
CACHE_TTL = 60

def lambda_handler(event, context):
    try:
        cache_key = 'all_events'
        current_time = time.time()
        
        if cache_key in cache:
            cached_data = cache[cache_key]
            if current_time - cached_data['timestamp'] < CACHE_TTL:
                print(f"CACHE HIT: Returning cached events. Age: {current_time - cached_data['timestamp']:.2f}s")
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'X-Cache': 'HIT'
                    },
                    'body': json.dumps(cached_data['data'])
                }
        
        print("CACHE MISS: Fetching from DynamoDB")
        start_time = time.time()
        response = table.scan()
        items = response['Items']
        db_duration = time.time() - start_time
        
        for item in items:
            for key, value in item.items():
                if str(type(value)) == "<class 'decimal.Decimal'>":
                    item[key] = str(value)
        
        cache[cache_key] = {
            'data': items,
            'timestamp': current_time
        }
        
        print(f"CACHE MISS: DynamoDB query took {db_duration:.3f}s. Result cached for {CACHE_TTL}s")
        
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
