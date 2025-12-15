from plyer import notification


def notify_stock(stocks):
    message = '\n'.join(stocks['products'])
    notification.notify(
        app_name="Apple PickUp Status - Shubh",
        title=f"✅✅ {stocks['storeName']}",
        message=message,
        timeout=10
    )

def complete_notify():
    notification.notify(
        app_name="script ran",
        title="script ran",
        message= 'run complete',
        timeout=10
    )

def notify_error():
    notification.notify(
        title="⚠️⚠️ Error found",
        message='script end with error',
        timeout=10
    )