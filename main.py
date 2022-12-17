import streamlit as st
import requests
import xml.etree.ElementTree as ET
import base64

# Function to parse the XML and extract the relevant data
def parse_xml(xml_string):
    
    root = ET.fromstring(xml_string)

    products = []
    categories_count = {}
    
    for product in root.findall('Product'):
        data = {}
        categories_count[product.find('CategoryName').text] = categories_count.get(product.find('CategoryName').text, 0) + 1
    
        data['name'] = product.find('BarcodeDesc').text
        data['type'] = 'simple'
        data["sku"] = product.find('ProductSku').text
        data['regular_price'] = product.find('Price').text
        data['description'] = product.find('HtmlDescr').text
        data['short_description'] = product.find('HtmlDescr').text
        data['categories'] = [{'name': product.find('CategoryName').text}]
        
        data["dimensions"] = {
            "length": product.find('Length').text,
            "width": product.find('Width').text,
            "height": product.find('Height').text
        }
        
        data["stock_quantity"] = 10
        
        if product.find('MainImage') is not None:
            data['images'] = [{'src': product.find('MainImage').text, 'position': 0}]
        if product.find('Images') is not None:
            for i, image in enumerate(product.find('Images').findall('ImageUrl')):
                data['images'].append({'src': image.text, 'position': i + 1})
        
        products.append(data)
    
    print("Categories:")
    print(categories_count)
    return products

# Function to send a POST request to the WooCommerce API
def create_product(api_key, api_secret, data):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(f'{api_key}:{api_secret}'.encode()).decode()
    }

    url = 'https://eirmacollection.gr/wp-json/wc/v3/products'

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        st.success(f'{data["name"]} created successfully')
    else:
        print(response.text)
        st.error(f'Error creating {data["name"]}. Error: {response.text}')

# Streamlit app
st.title('XML to WooCommerce API')

# API credentials
api_key = st.text_input('API Key')
api_secret = st.text_input('API Secret')

# XML file
xml_file = st.file_uploader('Upload XML file')
if xml_file is not None:
    xml_string = xml_file.read().decode()
    
    products = parse_xml(xml_string)
    st.json(products[:5])
    
    if st.button('Send to WooCommerce API'):
        for data in products[:1]:
            create_product(api_key, api_secret, data)
