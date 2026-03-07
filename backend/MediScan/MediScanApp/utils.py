from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def create_notification(user, title, message, notification_type='info'):
    """
    Create a notification and optionally send real-time push
    
    Args:
        user: User object
        title: Notification title
        message: Notification message
        notification_type: 'reminder', 'warning', or 'info'
    """
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type
    )
    
    # Optional: Send real-time notification via WebSocket (requires Django Channels)
    # send_realtime_notification(user.id, notification)
    
    return notification


def send_realtime_notification(user_id, notification):
    """Send real-time notification via WebSocket (requires Django Channels)"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'send_notification',
            'notification': {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
            }
        }
    )


# Example: Creating notifications in your code
# from .utils import create_notification
# create_notification(request.user, "Dose Reminder", "Time to take your medication!", "reminder")
