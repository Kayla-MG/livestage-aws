import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Bookings')

def lambda_handler(event, context):
    try:
        booking = {
            'bookingId': event['bookingId'],
            'userId': event['userId'],
            'eventId': event['eventId'],
            'seats': int(event['seats']),
            'amountCharged': event.get('amountCharged', 0),
            'currency': event.get('currency', 'EUR'),
            'paymentStatus': event.get('paymentStatus', 'SUCCESS'),
            'status': 'CONFIRMED',
            'createdAt': datetime.utcnow().isoformat()
        }
        
        table.put_item(Item=booking)
        
        return {
            **event,
            'bookingStatus': 'CONFIRMED',
            'confirmedAt': booking['createdAt']
        }
        
    except Exception as e:
        raise Exception(f'Booking confirmation error: {str(e)}')
