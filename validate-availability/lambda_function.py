import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Events')

def lambda_handler(event, context):
    try:
        event_id = event['eventId']
        seats_requested = int(event['seats'])
        
        response = table.get_item(
            Key={'eventId': event_id}
        )
        
        item = response.get('Item')
        
        if not item:
            return {
                **event,
                'available': False,
                'reason': 'Event not found'
            }
        
        available_seats = int(item['availableSeats'])
        
        if available_seats >= seats_requested:
            return {
                **event,
                'available': True,
                'availableSeats': available_seats
            }
        else:
            return {
                **event,
                'available': False,
                'reason': f'Only {available_seats} seats remaining'
            }
            
    except Exception as e:
        raise Exception(f'Validation error: {str(e)}')
