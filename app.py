from flask import Flask, request, render_template, jsonify, send_from_directory
from inference_sdk import InferenceHTTPClient
from roboflow import Roboflow
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import io

# Initialize Flask app
app = Flask(__name__)

# Initialize Roboflow Client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="rbhzu3DxasYsnk46y0Im"
)


# Initialize Roboflow Client for video
rf = Roboflow(api_key="rbhzu3DxasYsnk46y0Im")
project = rf.workspace().project("schooluniformdetectorlts2")
model = project.version("1").model

# Set minimum and maximum sizes for resizing
MIN_SIZE = (640, 640)  # Min width, height
MAX_SIZE = (1280, 1280)  # Max width, height

# Define confidence threshold for detections
CONFIDENCE_THRESHOLD = 0.5  # Adjust as necessary

def resize_image(image):
    """Resize image to fit within min and max size constraints."""
    img_width, img_height = image.size
    aspect_ratio = img_width / img_height

    # Resize based on min/max size
    if img_width < MIN_SIZE[0] or img_height < MIN_SIZE[1]:
        if img_width < img_height:
            new_width = MIN_SIZE[0]
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = MIN_SIZE[1]
            new_width = int(new_height * aspect_ratio)
    elif img_width > MAX_SIZE[0] or img_height > MAX_SIZE[1]:
        if img_width > img_height:
            new_width = MAX_SIZE[0]
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = MAX_SIZE[1]
            new_width = int(new_height * aspect_ratio)
    else:
        # No resizing needed
        return image

    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

# Image detection route
@app.route('/detect_image', methods=['POST'])
def detect_image():
    image_file = request.files['image']
    confidence_threshold = float(request.form.get('confidence', CONFIDENCE_THRESHOLD))

    # Open the image from the uploaded file in-memory
    image = Image.open(image_file)

    # Resize image if necessary
    resized_image = resize_image(image)

    # Save the resized image to a file for further processing (standardize as JPEG)
    image_path = "static/uploaded_image.jpg"
    resized_image.save(image_path, format='JPEG')

    # Infer on the resized image using the path
    result = CLIENT.infer(image_path, model_id="schooluniformdetectorlts2/1")

    # Draw bounding boxes on the resized image
    draw = ImageDraw.Draw(resized_image)

    # Define the font size
    try:
        font_path = "fonts/arial.ttf"
        font = ImageFont.truetype(font_path, size=32)
    except IOError:
        font = ImageFont.load_default()

    # Initialize detection flags
    detected_school_uniform = False
    detected_non_school_uniform = False
    detected_tie = False
    detected_shoes = False
    detected_no_shoes = False

    # Draw bounding boxes and labels from inference results if above confidence threshold
    for prediction in result['predictions']:
        if prediction['confidence'] >= confidence_threshold:
            x_center, y_center = prediction['x'], prediction['y']
            width = prediction['width']
            height = prediction['height']
            x1 = int(x_center - width / 2)
            y1 = int(y_center - height / 2)
            x2 = int(x_center + width / 2)
            y2 = int(y_center + height / 2)

            # Check for the various labels
            if prediction['class'] == 'School-Uniform':
                color = "green"
                detected_school_uniform = True
            elif prediction['class'] == 'Not-School-Uniform':
                color = "red"
                detected_non_school_uniform = True
            elif prediction['class'] == 'Tie-Detected':
                color = "blue"
                detected_tie = True
            elif prediction['class'] == 'Tie-Not-Detected':
                color = "yellow"
            elif prediction['class'] == 'Shoes-Detected':
                color = "purple"
                detected_shoes = True
            elif prediction['class'] == 'Shoes-Not-Detected':
                color = "orange"
                detected_no_shoes = True
            else:
                color = "gray"  # Default color for unexpected classes

            # Draw the bounding box
            draw.rectangle(((x1, y1), (x2, y2)), outline=color, width=2)
            # Annotate the image with label and confidence
            draw.text((x1, y1 - 10), f"{prediction['class']} ({prediction['confidence']:.2f})", fill=color, font=font)

    # Save the final image with bounding boxes
    output_path = "static/detected_image.jpg"
    resized_image.save(output_path, format='JPEG')
    
    # Return detection result based on detected flags
    if detected_school_uniform and detected_tie and detected_shoes:
        return jsonify({"status": "uniform_tie_and_shoes_detected"})
    elif detected_school_uniform and detected_tie and detected_no_shoes:
        return jsonify({"status": "uniform_tie_no_shoes_detected"})
    elif detected_school_uniform and detected_tie:
        return jsonify({"status": "uniform_tie_detected"})
    elif detected_school_uniform and detected_shoes:
        return jsonify({"status": "uniform_and_shoes_detected"})
    elif detected_school_uniform and detected_no_shoes:
        return jsonify({"status": "uniform_no_shoes_detected"})
    elif detected_school_uniform:
        return jsonify({"status": "uniform_detected"})
    elif detected_non_school_uniform and detected_tie and detected_shoes:
        return jsonify({"status": "non_uniform_tie_and_shoes_detected"})
    elif detected_non_school_uniform and detected_tie and detected_no_shoes:
        return jsonify({"status": "non_uniform_tie_no_shoes_detected"})
    elif detected_non_school_uniform and detected_tie:
        return jsonify({"status": "non_uniform_tie_detected"})
    elif detected_non_school_uniform and detected_shoes:
        return jsonify({"status": "non_uniform_and_shoes_detected"})
    elif detected_non_school_uniform and detected_no_shoes:
        return jsonify({"status": "non_uniform_no_shoes_detected"})
    elif detected_non_school_uniform:
        return jsonify({"status": "non_uniform_detected"})
    elif detected_tie and detected_shoes:
        return jsonify({"status": "tie_and_shoes_detected"})
    elif detected_tie and detected_no_shoes:
        return jsonify({"status": "tie_no_shoes_detected"})
    elif detected_tie:
        return jsonify({"status": "tie_detected"})
    elif detected_shoes:
        return jsonify({"status": "shoes_detected"})
    elif detected_no_shoes:
        return jsonify({"status": "no_shoes_detected"})
    else:
        return jsonify({"status": "no_detection"})


    

# Download route
@app.route('/download_image')
def download_image():
    return send_from_directory(directory='static', path='detected_image.jpg')

# Main route for homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/images/<path:filename>')
def serve_static(filename):
    return send_from_directory('static/images', filename)

if __name__ == '__main__':
    app.run(debug=True)
