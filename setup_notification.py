import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Project and resource details
PROJECT_ID = "testdicom-445700"
DATASET_ID = "xray-dataset"
DICOM_STORE_ID = "xray-dicom-store"
LOCATION = "us-central1"
SERVICE_ACCOUNT_KEY_PATH = "/Users/bilalshihab/dev/healthcare_ai/keys/testdicom-445700-76e08775608e.json"
PUBSUB_TOPIC_ID = "dicom-upload-topic"

# Set GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY_PATH

def create_notification_config(project_id, location, dataset_id, dicom_store_id, pubsub_topic_id):
    """Creates or updates a DICOM store's notification configuration."""
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_PATH)
    service = build('healthcare', 'v1', credentials=credentials)

    name = f"projects/{project_id}/locations/{location}/datasets/{dataset_id}/dicomStores/{dicom_store_id}"
    pubsub_topic = f"projects/{project_id}/topics/{pubsub_topic_id}"

    body = {
        "notificationConfig": {
            "pubsubTopic": pubsub_topic
        }
    }

    request = service.projects().locations().datasets().dicomStores().patch(
        name=name,
        updateMask="notificationConfig",
        body=body
    )

    try:
        response = request.execute()
        print(f"Notification config updated successfully: {response}")
        return response
    except Exception as e:
        print(f"Error updating notification config: {e}")
        return None

def main():
    response = create_notification_config(PROJECT_ID, LOCATION, DATASET_ID, DICOM_STORE_ID, PUBSUB_TOPIC_ID)
    if response:
        print("Notification config successfully set up. DICOM uploads will now trigger Pub/Sub messages.")
    else:
        print("Failed to set up notification config. Check logs for errors.")

if __name__ == "__main__":
    main()