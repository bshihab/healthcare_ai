import os
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

# Load environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bilalshihab/dev/healthcare_ai/keys/testdicom-445700-76e08775608e.json"

PROJECT_ID = "testdicom-445700"
SUBSCRIPTION_ID = "dicom-upload-sub"
TIMEOUT = 60.0  # Adjust as needed

def callback(message):
    print(f"Received message: {message.data.decode('utf-8')}")
    # Add any additional processing logic here
    message.ack()

def main():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    with subscriber:
        try:
            # Keep the main thread alive to listen for messages
            streaming_pull_future.result(timeout=TIMEOUT)
        except TimeoutError:
            print("Timeout occurred, stopping the subscriber.")
            streaming_pull_future.cancel()

if __name__ == "__main__":
    main()