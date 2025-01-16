# DICOM Store Uploader and Pub/Sub Subscriber and AI Analysis

This project demonstrates how to upload DICOM files to a Google Cloud Healthcare API DICOM store, check for existing instances, handle conflicts, and subscribe to Pub/Sub notifications triggered by DICOM uploads.

## Overview

The project consists of three main components:

-   **`setup_notification.py`**: Sets up the notification configuration for a DICOM store to send messages to a Pub/Sub topic upon DICOM instance creation.
-   **`upload_dicom.py`**: Uploads DICOM files to the specified DICOM store. It checks for existing instances using the SOP Instance UID, handles conflicts by either skipping or overwriting, and publishes a message to a Pub/Sub topic upon successful upload.
-   **`subscriber.py`**: Subscribes to a Pub/Sub topic to receive notifications about new DICOM uploads. It acknowledges each message after processing.

## AI Analysis (Coming Soon!)

This project will soon be extended to include AI-powered analysis of uploaded DICOM images. Stay tuned for updates on this exciting new feature!

## Prerequisites

Before running the scripts, ensure you have the following:

-   A Google Cloud Project with the Healthcare API enabled.
-   A DICOM store created in your project.
-   A Pub/Sub topic created in your project.
-   A service account with the necessary permissions to access the Healthcare API and Pub/Sub.
-   Python 3.7 or later installed.
-   The required Python packages installed. You can install them using pip:

pip install google-cloud-pubsub google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv pydicom


## Setup

1. **Environment Variables**:
    -   Rename the `.env.example` file to `.env`.
    -   Fill in the `.env` file with your Google Cloud project details, DICOM store information, Pub/Sub topic ID, and the path to your service account key file.

    ```
    PROJECT_ID="your-gcp-project-id"
    DATASET_ID="your-healthcare-dataset-id"
    DICOM_STORE_ID="your-dicom-store-id"
    LOCATION="your-dataset-location"
    SERVICE_ACCOUNT_KEY_PATH="path/to/your/service_account_key.json"
    PUBSUB_TOPIC_ID="your-pubsub-topic-id"
    ```

2. **Service Account Key**:
    -   Download your service account key file from the Google Cloud Console and place it in the path specified by `SERVICE_ACCOUNT_KEY_PATH` in your `.env` file.

## Usage

### Setting Up Notification Configuration

Run `setup_notification.py` to configure your DICOM store to send notifications to your Pub/Sub topic:

python setup_notification.py


This script will update the DICOM store's notification configuration.

### Uploading DICOM Files

To upload a DICOM file, run `upload_dicom.py`. The script will check if the DICOM instance already exists in the store. If it does, and the `OVERWRITE` flag is set to `True`, it will delete the existing instance before uploading the new one.

python upload_dicom.py


You can modify the `DICOM_FILE_PATH` variable in `upload_dicom.py` to specify the path to the DICOM file you want to upload.

### Subscribing to Pub/Sub Notifications

Run `subscriber.py` to start listening for messages on your Pub/Sub topic:

python subscriber.py


This script will continuously listen for messages and print them to the console. It will also acknowledge each message after processing.

## Error Handling

-   The scripts include error handling for common issues such as missing environment variables, invalid DICOM files, and API errors.
-   `upload_dicom.py` checks for existing DICOM instances and handles conflicts based on the `OVERWRITE` flag.
-   `subscriber.py` handles timeouts and gracefully stops the subscriber.

