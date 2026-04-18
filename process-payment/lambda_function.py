import json
import random

def lambda_handler(event, context):
    try:
        seats = int(event.get('seats', 1))
        price_per_seat = 65
        amount = seats * price_per_seat
        
        success = random.random() > 0.3
        
        if not success:
            raise Exception('Payment declined by provider')
        
        return {
            **event,
            'paymentStatus': 'SUCCESS',
            'amountCharged': amount,
            'currency': 'EUR'
        }
        
    except Exception as e:
        raise Exception(f'Payment error: {str(e)}')
