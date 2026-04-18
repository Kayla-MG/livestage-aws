import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Events')

def lambda_handler(event, context):
    try:
        event_id = event['eventId']
        seats_requested = int(event['seats'])
        
        table.update_item(
            Key={'eventId': event_id},
            UpdateExpression='SET availableSeats = availableSeats - :seats',
            ExpressionAttributeValues={
                ':seats': seats_requested,
                ':required': seats_requested
            },
            ConditionExpression='availableSeats >= :required'
        )
        
        return {
            **event,
            'seatReserved': True
        }
        
    except Exception as e:
        raise Exception(f'Seat reservation error: {str(e)}')
