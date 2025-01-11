import os
from dotenv import load_dotenv
from google.cloud import pubsub_v1

load_dotenv()

def pull_messages(project_id, subscription_id, timeout=None):
    """
    Pulls messages from a Pub/Sub subscription.

    Args:
        project_id (str): Google Cloud Project ID.
        subscription_id (str): Pub/Sub Subscription ID.
        timeout (int, optional): Timeout for pulling messages. Defaults to None.
    """
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received message: {message.data.decode('utf-8')}")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result(timeout=timeout)
    except Exception as e:
        streaming_pull_future.cancel()
        print(f"Error listening for messages: {e}")

if __name__ == "__main__":
    PROJECT_ID = os.getenv("PROJECT_ID")
    SUBSCRIPTION_ID = os.getenv("PUBSUB_SUBSCRIPTION_ID")
    TIMEOUT = None  # Set a timeout in seconds, or leave as None for indefinite listening

    pull_messages(PROJECT_ID, SUBSCRIPTION_ID, TIMEOUT)
