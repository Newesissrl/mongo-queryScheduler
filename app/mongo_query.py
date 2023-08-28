import csv
import os
import json
from datetime import datetime
from pymongo import MongoClient
from bson import json_util
from google.cloud import storage




# MongoDB connection settings
mongo_connection_string = os.environ.get("MONGO_CONNECTION_STRING")
collection_name = os.environ.get("MONGO_COLLECTION")
use_pipeline_from = os.environ.get("USE_PIPELINE_FROM")

# Check if variable USE_PIPELINE_FROM is set to "file"
if (use_pipeline_from) == "file":
    # Check if variable PIPELINE_FILENAME exists
    if "PIPELINE_FILENAME" in os.environ:
        pipeline_filename = os.environ["PIPELINE_FILENAME"]
    else:
        pipeline_filename = "pipeline"

# Connect to MongoDB
client = MongoClient(mongo_connection_string)
db = client.get_default_database()  # Get the default database from the connection string
collection = db[collection_name]

# Execute the aggregation pipeline
#query = collection.aggregate(pipeline)
if use_pipeline_from=="variable":
    pipeline_query = os.environ.get("PIPELINE_QUERY")
    print(f"pipeline from ENV is: {pipeline_query}")
    final_pipeline = (pipeline_query)
elif use_pipeline_from=="file":
    print(f"pipeline file is: {pipeline_filename}")
    # MongoDB aggregation pipeline loaded from ConfigMap
    #pipeline_file_path = "/app/queries/pipeline.txt"
    pipeline_file_path = f"/app/queries/{pipeline_filename}"
    with open(pipeline_file_path) as pipeline_tmp:
        pipeline_file = pipeline_tmp.read()
        print(f"pipeline from file is: {pipeline_file}")
        final_pipeline = (pipeline_file)

query = collection.aggregate(eval(final_pipeline))

result = list(query)

print(f"result from pipeline is: {result}")

# Create a unique filename using the current date and time
current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
# Check if variable OVERRIDE_NAME exists
if "OVERRIDE_NAME" in os.environ:
    custom_name = os.environ["OVERRIDE_NAME"]
    file_prefix = f"result_{collection_name}_{custom_name}"
else:
    file_prefix = f"result_{collection_name}"



# Write the result to a JSON file
filename = f"{file_prefix}_{current_date}.json"
output_file = f"/app/{filename}"
with open(output_file, "w") as file:
    json.dump(json_util.dumps(result), file, indent=4)

print(f"Query results saved to '{output_file}'.")



# Upload the file to Google Cloud Storage
if "GCP_BUCKET_NAME" in os.environ:

    # Google Cloud Storage settings
    bucket_name = os.environ.get("GCP_BUCKET_NAME")
    bucket_folder = os.environ.get("GCP_BUCKET_FOLDER")

    blob_storage = f"{bucket_folder}/{filename}"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_storage)
    blob.upload_from_filename(output_file)

    print(f"Data extracted and saved as gs://{bucket_name}/{blob_storage}")
