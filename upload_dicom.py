import os
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from pydicom import dcmread
from dotenv import load_dotenv
from google.cloud import pubsub_v1

load_dotenv()


def publish_message(project_id, topic_id, message):
    """
    Publishes a message to a Pub/Sub topic.

    Args:
        project_id (str): Google Cloud Project ID.
        topic_id (str): Pub/Sub Topic ID.
        message (str): Message to publish.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    print(f"Publishing to topic path: {topic_path}")


    # Publish the message
    future = publisher.publish(topic_path, message.encode("utf-8"))
    print(f"Published message to {topic_id}: {message}")


def get_sop_instance_uid(dicom_file_path):
    try:
        dicom_data = dcmread(dicom_file_path)
        return dicom_data.SOPInstanceUID, dicom_data.StudyInstanceUID
    except Exception as e:
        print(f"Error extracting DICOM metadata: {e}")
        return None, None

def dicom_file_exists(project_id, dataset_id, dicom_store_id, sop_instance_uid, location="us-central1"):
    """
    Checks if a DICOM file with a specific SOP Instance UID exists in the DICOM store and returns its StudyInstanceUID if found.

    Args:
        project_id (str): Google Cloud Project ID.
        dataset_id (str): Healthcare Dataset ID.
        dicom_store_id (str): DICOM Store ID.
        sop_instance_uid (str): SOP Instance UID of the DICOM file.
        location (str): Location of the dataset (default: us-central1).

    Returns:
        tuple: (exists (bool), study_instance_uid (str or None))
    """
    dicom_instances_url = f"https://healthcare.googleapis.com/v1/projects/{project_id}/locations/{location}/datasets/{dataset_id}/dicomStores/{dicom_store_id}/dicomWeb/instances"

    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("SERVICE_ACCOUNT_KEY_PATH"),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    credentials.refresh(Request())
    token = credentials.token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/dicom"
    }

    response = requests.get(dicom_instances_url, headers=headers, params={"SOPInstanceUID": sop_instance_uid})

    if response.status_code == 204:
        # Handle 204 response: No matching instances found
        print(f"No instances found for SOPInstanceUID {sop_instance_uid}.")
        return False, None

    elif response.status_code == 200:
        try:
            instances = response.json()
            print("Instances response:", instances)

            for instance in instances:
                # Accessing values within the JSON structure correctly
                retrieved_sop_uid = instance.get("00080018", {}).get("Value", [None])[0]
                if retrieved_sop_uid == sop_instance_uid:
                    study_instance_uid = instance.get("0020000D", {}).get("Value", [None])[0]
                    print(f"Conflict detected: SOPInstanceUID {sop_instance_uid} exists in StudyInstanceUID {study_instance_uid}.")
                    return True, study_instance_uid
        except Exception as e:
            print(f"Error parsing response: {e}")

    else:
        # Handle other HTTP errors
        print(f"Failed to fetch instances. Status code: {response.status_code}, Response: {response.text}")

    return False, None


def delete_dicom_instance(project_id, dataset_id, dicom_store_id, study_instance_uid, location="us-central1"):
    """
    Deletes a specific DICOM study by StudyInstanceUID.

    Args:
        project_id (str): Google Cloud Project ID.
        dataset_id (str): Healthcare Dataset ID.
        dicom_store_id (str): DICOM Store ID.
        study_instance_uid (str): StudyInstanceUID of the DICOM study.
        location (str): Location of the dataset (default: us-central1).
    """
    dicom_study_url = f"https://healthcare.googleapis.com/v1/projects/{project_id}/locations/{location}/datasets/{dataset_id}/dicomStores/{dicom_store_id}/dicomWeb/studies/{study_instance_uid}"

    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("SERVICE_ACCOUNT_KEY_PATH"),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    credentials.refresh(Request())
    token = credentials.token

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.delete(dicom_study_url, headers=headers)

    if response.status_code == 200:
        print(f"Deleted study with StudyInstanceUID {study_instance_uid}.")
    else:
        print(f"Failed to delete study. Status code: {response.status_code}, Response: {response.text}")

def upload_dicom_file(project_id, dataset_id, dicom_store_id, dicom_file_path, location="us-central1", overwrite=False):
    print("Entered upload_dicom_file function")  # Start tracing here

    sop_instance_uid, study_instance_uid_local = get_sop_instance_uid(dicom_file_path)
    print(f"Extracted SOPInstanceUID: {sop_instance_uid}, StudyInstanceUID: {study_instance_uid_local}")

    if not sop_instance_uid:
        print("Failed to extract SOP Instance UID. Skipping upload.")
        return

    exists, study_instance_uid_remote = dicom_file_exists(project_id, dataset_id, dicom_store_id, sop_instance_uid, location)
    print(f"DICOM file exists check: {exists}")


    if exists:
        print(f"Conflict detected: SOP Instance UID {sop_instance_uid} already exists in the DICOM store (StudyInstanceUID: {study_instance_uid_remote}).")
        if overwrite:
            if study_instance_uid_remote:
                print(f"Overwriting existing instance with SOP Instance UID {sop_instance_uid} (StudyInstanceUID: {study_instance_uid_remote}).")
                delete_dicom_instance(project_id, dataset_id, dicom_store_id, study_instance_uid_remote, location)
            else:
                print("Could not retrieve StudyInstanceUID for deletion. Skipping overwrite.")
                return
        else:
            print("Skipping upload due to conflict.")
            return

    try:
        dicom_store_url = f"https://healthcare.googleapis.com/v1/projects/{project_id}/locations/{location}/datasets/{dataset_id}/dicomStores/{dicom_store_id}/dicomWeb/studies"

        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("SERVICE_ACCOUNT_KEY_PATH"),
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        credentials.refresh(Request())
        token = credentials.token

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/dicom"
        }

        with open(dicom_file_path, "rb") as dicom_file:
            dicom_data = dicom_file.read()

        response = requests.post(dicom_store_url, headers=headers, data=dicom_data)

        if response.status_code == 200:
            print("DICOM file uploaded successfully.")
            message = f"New DICOM file uploaded: SOPInstanceUID={sop_instance_uid}, StudyInstanceUID={study_instance_uid_local}"

            print("About to publish message")
            publish_message(project_id, os.getenv("PUBSUB_TOPIC_ID"), message)
            print("Message published")


        elif response.status_code == 409:
            print(f"Failed to upload DICOM file due to conflict (Status code: 409). This should have been handled by the overwrite logic.")
            print("Response:", response.text)
        else:
            print(f"Failed to upload DICOM file. Status code: {response.status_code}")
            print("Response:", response.text)

    except Exception as e:
        print(f"An error occurred during upload: {e}")

if __name__ == "__main__":
    PROJECT_ID = os.getenv("PROJECT_ID")
    DATASET_ID = os.getenv("DATASET_ID")
    DICOM_STORE_ID = os.getenv("DICOM_STORE_ID")
    LOCATION = os.getenv("LOCATION")
    SERVICE_ACCOUNT_KEY_PATH = os.getenv("SERVICE_ACCOUNT_KEY_PATH")
    DICOM_FILE_PATH = "/Users/bilalshihab/dev/healthcare_ai/0004.DCM"  # You might want to make this configurable as well
    OVERWRITE = True

    if os.path.exists(DICOM_FILE_PATH):
        upload_dicom_file(PROJECT_ID, DATASET_ID, DICOM_STORE_ID, DICOM_FILE_PATH, LOCATION, overwrite=OVERWRITE)
    else:
        print("DICOM file not found. Please check the file path.")