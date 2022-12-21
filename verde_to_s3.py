import streamlit as st
import requests
import xml.etree.ElementTree as ET
import boto3
import os

bucket_url = os.environ.get("BUCKET_URL")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_ACCESS_ACCESS_KEY")

# Connect to the S3 bucket
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=bucket_url,
)

# Create a function to upload an image to the S3 bucket
def upload_image(image_url):
    # Send an HTTP request to retrieve the image
    response = requests.get(image_url)
    print(image_url, response.status_code)
    # Generate a unique file name for the image
    file_name = image_url.split("=")[-1]
    # Upload the image to the S3 bucket
    s3.put_object(Bucket="eirma-images", Key=file_name, Body=response.content)
    print(f"Uploaded {file_name} to S3 bucket")


# Use the file_uploader widget to accept an XML file as input
xml_file = st.file_uploader("Upload an XML file:")

# Check if an XML file was uploaded
if xml_file is not None:
    # Parse the XML data
    root = ET.fromstring(xml_file.read())

    # Find all image URLs in the XML data
    image_urls = root.findall("MainImage")

    for product in root.findall("Product"):
        main = product.find("MainImage")
        if main is not None:
            image_urls.append(main.text)

    print(f"Found {len(image_urls)} image urls")

    # Create a button in the streamlit app to trigger the image uploads
    if st.button("Upload Images"):
        # Iterate over the list of image URLs and upload each one to the S3 bucket
        for image_url in image_urls:
            upload_image(image_url)
        st.success("Done!")
