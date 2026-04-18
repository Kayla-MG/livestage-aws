import json
import boto3
import uuid

stepfunctions = boto3.client('stepfunctions')

STATE_MACHINE_ARN = 'arn:aws:states:eu-west-1:323748450739:stateMachine:livestage-booking-machine'

def lambda_handler(event, context):
    try:
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            body = event
        
        booking_input = {
            'bookingId': str(uuid.uuid4()),
            'userId': body['userId'],
            'eventId': body['eventId'],
            'seats': body['seats']
        }
        
        response = stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(booking_input)
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Booking started successfully',
                'bookingId': booking_input['bookingId'],
                'executionArn': response['executionArn']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
