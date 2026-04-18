import json
import boto3
from datetime import datetime

sqs = boto3.client('sqs')

NOTIFICATION_QUEUE_URL = 'https://sqs.eu-west-1.amazonaws.com/323748450739/livestage-notification-queue'
ANALYTICS_QUEUE_URL = 'https://sqs.eu-west-1.amazonaws.com/323748450739/livestage-analytics-queue'

def lambda_handler(event, context):
    try:
        user_id = event.get('userId', 'unknown')
        event_id = event.get('eventId', 'unknown')
        booking_id = event.get('bookingId', 'unknown')
        booking_status = event.get('bookingStatus', 'UNKNOWN')
        reason = event.get('reason', 'No reason provided')
        amount = event.get('amountCharged', 0)

        if booking_status == 'CONFIRMED':
            message = {
                'type': 'BOOKING_CONFIRMED',
                'userId': user_id,
                'bookingId': booking_id,
                'eventId': event_id,
                'amountCharged': amount,
                'timestamp': datetime.utcnow().isoformat()
            }
            notification_type = 'BOOKING_CONFIRMED'
        else:
            message = {
                'type': 'BOOKING_FAILED',
                'userId': user_id,
                'bookingId': booking_id,
                'eventId': event_id,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
            notification_type = 'BOOKING_FAILED'

        sqs.send_message(
            QueueUrl=NOTIFICATION_QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        sqs.send_message(
            QueueUrl=ANALYTICS_QUEUE_URL,
            MessageBody=json.dumps(analytics_message := {
                'type': 'BOOKING_EVENT',
                'userId': user_id,
                'eventId': event_id,
                'bookingId': booking_id,
                'status': notification_type,
                'timestamp': datetime.utcnow().isoformat()
            })
        )

        print(f"[{datetime.utcnow().isoformat()}] {notification_type}: Messages sent to SQS queues")

        return {
            **event,
            'notificationSent': True,
            'notificationType': notification_type
        }

    except Exception as e:
        raise Exception(f'Notification error: {str(e)}')
