from flask import Flask, request, jsonify, render_template
from PIL import Image
import torch
import json
from torchvision import transforms, models
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from io import BytesIO
import uuid
import requests

app = Flask(__name__)

# Load the pre-trained ResNet50 model
model = models.resnet50(pretrained=True)
model.eval()

# Class labels for ImageNet
with open("imagenet_class_index.json") as f:
    imagenet_class_index = json.load(f)

# Define Azure Blob Storage Configuration
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=vivek123123;AccountKey=yYBJISqGbpFBZo1iFAkTyYuQqP0YLOMyhRTe4RQhUiBMIEkOcfC1mGNASfGUIvpDtjDKLN5Wmth2+AStTXroiw==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "images"

# Replace these values with your own Azure Translator Text API subscription key and endpoint
subscription_key = 'bf3d53be3d1441709660146ac6988b61'
endpoint = 'https://api.cognitive.microsofttranslator.com/'
location = 'eastus'  # e.g., global

def preprocess_image(image):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)
    return input_batch

def classify_image(image):
    input_batch = preprocess_image(image)
    output = model(input_batch)
    _, predicted_idx = torch.max(output, 1)
    return imagenet_class_index[str(predicted_idx.item())][1]

def upload_to_blob_storage(image_bytes, filename):
    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    
    # Create a blob client using the filename as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)

    # Upload the image bytes
    blob_client.upload_blob(image_bytes)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})

    try:
        image_file = request.files['image']
        image_bytes = image_file.read()

        # Perform basic validation on the image bytes
        if not image_bytes:
            return jsonify({'error': 'Empty image data'})

        # Upload the image to Azure Blob Storage
        upload_to_blob_storage(image_bytes, image_file.filename)

        # Load the image from memory
        image = Image.open(BytesIO(image_bytes)).convert('RGB')

        # Perform image classification
        animal_class = classify_image(image)

        return jsonify({'animal': animal_class})

    except Exception as e:
        # Log the error for debugging purposes
        app.logger.error(f"Error during image classification: {str(e)}")
        return jsonify({'error': 'Failed to classify the image'})

@app.route('/translate', methods=['POST'])
def translate():
    text = request.json['text']
    target_language = request.json['target_language']
    api_url = f"{endpoint}/translate?api-version=3.0&to={target_language}"

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    data = [{'text': text}]
    response = requests.post(api_url, headers=headers, json=data)
    translation = response.json()[0]['translations'][0]['text']
    return jsonify({'translation': translation})

if __name__ == '__main__':
    app.run(debug=True)
