"""
UYIR Road Safety Hackathon 2025 - Coimbatore Road Safety Dashboard.

Author: Ramaguru Radhakrishnan
Email:  r_ramaguru@cb.amrita.edu
Date:   February 2025
License: MIT License
Version: 1.0

Description:
This app provides live traffic data, air quality index (AQI), 
accident detection and reporting through Blockchain (Ethereum).

"""
from flask import Flask, render_template, Response, request, jsonify
from sklearn.linear_model import LinearRegression
import numpy as np
import easyocr
import requests
import cv2
import pandas as pd
from ultralytics import YOLO
import os 
import json

# Initialize Flask Application                            
app = Flask(__name__)

# 🔵 AQI API Token
AQI_API_KEY = "<<API>>"

# 🔴 HERE API Key
HERE_API_KEY = "<<API>>"

DATA_FILE = "data/reports.json"

# 🔹 AQI Status Categories
AQI_CATEGORIES = [
    (0, 50, "Good", "Air quality is satisfactory, and air pollution poses little or no risk."),
    (51, 100, "Moderate", "Air quality is acceptable, but some pollutants may affect sensitive individuals."),
    (101, 150, "Unhealthy for Sensitive Groups", "People with respiratory diseases should limit outdoor exertion."),
    (151, 200, "Unhealthy", "Everyone may begin to experience health effects; sensitive groups at higher risk."),
    (201, 300, "Very Unhealthy", "Health warnings; everyone should reduce outdoor activities."),
    (301, 999, "Hazardous", "Health alert: everyone should avoid all outdoor exertion."),
]

# 🔹 Initialize Camera     
camera = cv2.VideoCapture(0)  # Live Camera Feed

def load_reports():
    """Load citizen-reported traffic issues from JSON file."""                 
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []  # Return empty list if file doesn't exist

# 🔹 Routes
# 🔵 Route: Home Dashboard                                     
@app.route('/')
def index():
    """Render the home dashboard."""
    return render_template('index.html')
    
@app.route('/dash')
def dashboard():
    """Render the main dashboard page."""
    return render_template('index2.html')    

# 🔴 Route: Object Detection Page
@app.route('/camera')
def camera():
    """Render the traffic violation detection page."""
    return render_template('camera.html')
    
@app.route('/api/live-traffic')
def get_live_traffic():
    traffic_data = [
        {"coordinates": [[11.0168, 76.9558], [11.0185, 76.9600]], "level": "high"},
        {"coordinates": [[11.0123, 76.9501], [11.0140, 76.9550]], "level": "moderate"},
        {"coordinates": [[11.0200, 76.9700], [11.0250, 76.9800]], "level": "low"}
    ]
    return jsonify(traffic_data)

# Sample iRAP Road Ratings (Replace with Database or API Data)
@app.route('/api/irap-ratings')
def get_irap_ratings():
    irap_data = [
        {"coordinates": [[11.0300, 76.9850], [11.0350, 76.9950]], "rating": 5},
        {"coordinates": [[11.0100, 76.9450], [11.0150, 76.9500]], "rating": 3},
        {"coordinates": [[11.0250, 76.9650], [11.0300, 76.9700]], "rating": 1}
    ]
    return jsonify(irap_data)
    
@app.route('/live_traffic')
def live_traffic():
    """Render Live Traffic page"""
    return render_template('live_traffic.html')    

# 🟠 Route: Heatmap Page
@app.route('/heatmap')
def heatmap():
    """Render the heatmap visualization page."""
    return render_template('heatmap.html')

@app.route('/citizen_reports')
def citizen_reports():
    """Render the citizen reports page."""
    return render_template('citizen_reports.html')
    
@app.route('/reports', methods=['GET'])
def get_reports():
    """Fetch all citizen-reported traffic issues."""
    reports = load_reports()
    return jsonify(reports)
    
    
@app.route('/api/here-traffic-flow')
def get_traffic_flow():
    """Fetch live traffic flow data using HERE API."""
    
    print("Routing to /api/here-traffic-flow")
    
    try:
        url = f"https://data.traffic.hereapi.com/v7/flow?in=circle:11.0168,76.9558;r=5000&locationReferencing=olr&apiKey={HERE_API_KEY}"
    
        #url =f"https://data.traffic.hereapi.com/v7/flow?locationReferencing=shape&in=bbox:10.85,76.85,11.20,77.20&apiKey=${HERE_API_KEY}";
        
        response = requests.get(url)
        response.raise_for_status()  # 🔴 Raise an error for non-200 responses

        return jsonify(response.json())  # Return valid JSON response

    except requests.exceptions.RequestException as e:
        print(f"Error fetching traffic flow: {e}")  # Log error
        return jsonify({"error": "Failed to fetch traffic data"}), 500  # Return error

@app.route('/api/here-traffic-incidents')
def get_traffic_incidents():
    """Fetch live traffic incidents using HERE API."""
    
    print("Routing to /api/here-traffic-incidents")
    
    try:
        url = f"https://data.traffic.hereapi.com/v7/incidents?in=circle:11.0168,76.9558;r=5000&locationReferencing=olr&apiKey={HERE_API_KEY}"
    
        response = requests.get(url)
        response.raise_for_status()  

        return jsonify(response.json())

    except requests.exceptions.RequestException as e:
        print(f"Error fetching traffic incidents: {e}")  
        return jsonify({"error": "Failed to fetch incidents data"}), 500     

    
@app.route('/aqi/<city>', methods=['GET'])
def get_aqi(city):
    response = requests.get(f'https://api.waqi.info/feed/{city}/?token={AQI_API_KEY}')
    data = response.json()
    
    if data.get("status") == "ok":
        return jsonify({"city": city, "aqi": data["data"]["aqi"]})
    else:
        return jsonify({"error": "Unable to fetch AQI data."}), 400    
        
@app.route('/alpr', methods=['POST'])
def alpr():
    """Handle ALPR (License Plate Detection)."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    image_path = f'uploads/{file.filename}'
    file.save(image_path)

    plates = detect_license_plate(image_path)
    return jsonify({'license_plates': plates})  
    
def get_irap_compliance():
    """Fetch iRAP compliance details for roads in Coimbatore"""
    # Placeholder data (Replace with real API or database query)
    irap_data = {
        "star_rating": 3,  # Example: 1 to 5 stars
        "high_risk_areas": 12,  # Example: Number of high-risk zones
        "safety_improvements": ["Pedestrian crossings", "Speed limit enforcement"]
    }
    return irap_data

def get_sdg_compliance():
    """Fetch SDG compliance data (Goal 3.6 - Road Safety)"""
    # Placeholder data (Replace with real API or government reports)
    sdg_data = {
        "target": "Reduce road fatalities by 50% by 2030",
        "current_reduction": "28% reduction achieved",
        "initiatives": ["Traffic signal automation", "Speed monitoring cameras"]
    }
    return sdg_data

@app.route('/irap_compliance', methods=['GET'])
def irap_compliance():
    return jsonify(get_irap_compliance())

@app.route('/sdg_compliance', methods=['GET'])
def sdg_compliance():
    return jsonify(get_sdg_compliance())    

@app.route('/traffic_map')
def traffic_map():
    """Render traffic map page"""
    return render_template('traffic_map.html')
    
    
# Sample traffic data
X = np.array([[7], [8], [9], [10], [11]])
y = np.array([50, 60, 100, 120, 90])

# Train model
model = LinearRegression()
model.fit(X, y)

@app.route('/predict_traffic', methods=['GET'])
def predict_traffic():
    hour = request.args.get('hour', type=int)
    if hour is None:
        return jsonify({'error': 'Missing hour parameter'}), 400

    predicted_volume = model.predict([[hour]])[0]
    return jsonify({'hour': hour, 'predicted_traffic_volume': predicted_volume})    

def get_aqi_status(aqi_value):
    """Determine AQI status based on value"""
    for min_val, max_val, status, health_message in AQI_CATEGORIES:
        if min_val <= aqi_value <= max_val:
            return status, health_message
    return "Unknown", "No data available"

def detect_license_plate(image_path):
    reader = easyocr.Reader(['en'])
    image = cv2.imread(image_path)
    results = reader.readtext(image)
    plates = [text for (_, text, prob) in results if prob > 0.8]
    return plates
    
    
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')    

# 🔥 Route: Video Feed (YOLO Traffic Violation Detection)
def detect_violations():
    while True:
        success, frame = camera.read()
        if not success:
            break
        results = violation_model(frame)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               
def detect_accidents(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO Detection
        results = model(frame)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imshow("Accident Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()               

@app.route('/video_feed')
def video_feed():
    return Response(detect_violations(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 🔥 Route: API for Accident Data
@app.route('/api/accidents')
def get_accidents():
    return accident_data.to_json(orient="records")

if __name__ == '__main__':
    app.run(debug=True)
