import streamlit as st
import requests
import xml.etree.ElementTree as ET
import base64
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


def get_image_from_s3(file_name):
    s3.get_object(Bucket="eirma-images", Key=file_name)


# Function to parse the XML and extract the relevant data
def parse_xml(xml_string):

    root = ET.fromstring(xml_string)

    products = []
    categories_count = {}

    for product in root.findall("Product"):
        data = {}
        categories_count[product.find("CategoryName").text] = (
            categories_count.get(product.find("CategoryName").text, 0) + 1
        )

        name = product.find("BarcodeDesc").text
        uppercase_name = name[0].upper() + name[1:].lower()

        data["name"] = uppercase_name
        data["type"] = "simple"
        data["sku"] = product.find("ProductSku").text
        data["regular_price"] = product.find("Price").text
        data["description"] = product.find("HtmlDescr").text
        data["short_description"] = product.find("HtmlDescr").text
        data["categories"] = [{"name": "Blouses"}]

        data["dimensions"] = {
            "length": product.find("Length").text,
            "width": product.find("Width").text,
            "height": product.find("Height").text,
        }

        data["stock_quantity"] = 10

        if product.find("MainImage") is not None:
            bucket_url = "https://eu2.contabostorage.com/dbc41575d769405eb54f6b1b6f2e65f9:eirma-images/eirma-images"
            file_name = product.find("MainImage").text.split("=")[-1]
            data["images"] = [{"src": f"{bucket_url}/{file_name}", "position": 0}]

        # if product.find('Images') is not None:
        #     for i, image in enumerate(product.find('Images').findall('ImageUrl')):
        #         data['images'].append({'src': image.text, 'position': i + 1})

        products.append(data)

    print("Categories:")
    print(categories_count)
    return products


# Function to send a POST request to the WooCommerce API
def create_product(api_key, api_secret, data):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic "
        + base64.b64encode(f"{api_key}:{api_secret}".encode()).decode(),
    }

    url = "https://eirmacollection.gr/wp-json/wc/v3/products"

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        st.success(f'{data["name"]} created successfully')
    else:
        print(response.text)
        st.error(f'Error creating {data["name"]}. Error: {response.text}')


# Streamlit app
st.title("XML to WooCommerce API")

# API credentials
api_key = st.text_input("API Key")
api_secret = st.text_input("API Secret")

# XML file
xml_file = st.file_uploader("Upload XML file")
if xml_file is not None:
    xml_string = xml_file.read().decode()

    products = parse_xml(xml_string)
    st.json(products[:5])

    if st.button("Send to WooCommerce API"):
        for data in products:
            create_product(api_key, api_secret, data)
