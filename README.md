# 🌿 Go Gaia
### *AI-Powered Recycling Classification for a Sustainable Future*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Azure Custom Vision](https://img.shields.io/badge/Azure-Custom%20Vision-0078d4.svg)](https://azure.microsoft.com/en-us/services/cognitive-services/custom-vision-service/)

## Go Gaia Team
- **Jason Zheng** - Full-Stack Development & Model Integration
- **Bhoomi Patni** - Model Training & Integration  
- **Sharanya Raj** - Front End Development
- **Ann Carlos** - Front End Development

---

## Project Overview

**TrashVision** is an innovative web application that uses artificial intelligence to help users make informed recycling decisions. By leveraging Azure Custom Vision AI, our app analyzes photos of waste items and provides instant classification with recycling recommendations.

### **Mission Statement**
*"The Planet is Waiting. The Time is Now."* - Empowering individuals to make sustainable choices through AI-powered guidance, inspired by Gaia, the Earth goddess who reminds us that our planet is the original resource.

---

## Key Features

### **Dual Input Methods**
- **Live Camera Capture**: Take real-time photos using device camera
- **File Upload**: Upload existing photos from device storage

### **AI-Powered Classification**
- **Azure Custom Vision Integration**: Advanced machine learning model
- **Multiple Model Versions**: v1, v2, v3 for improved accuracy
- **Confidence Scoring**: Percentage-based prediction reliability

### **Responsive Design**
- **Mobile-First Approach**: Optimized for smartphones and tablets  
- **Cross-Platform Compatibility**: Works on iOS, Android, and desktop
- **No-Scroll Layout**: Everything fits on one screen

### **Environmental Theme**
- **Earth-Inspired Design**: Gradient backgrounds and natural colors
- **Goddess Imagery**: Greek mythology elements representing Mother Earth
- **Animated Elements**: Breathing neon facts and decorative vines

### **Smart Recommendations**
- **Instant Results**: Real-time recycling guidance
- **Highest Confidence Selection**: Shows most likely classification
- **Educational Facts**: Rotating environmental tips and statistics

---

## Technology Stack

### **Frontend**
- **HTML5**: Semantic structure and camera API integration
- **CSS3**: Responsive design with viewport units and gradients
- **Vanilla JavaScript**: Live camera, file upload, and API communication

### **Backend**
- **Flask (Python)**: Web server and API endpoints
- **Azure Custom Vision**: AI model training and prediction
- **Environment Management**: Secure API key handling

### **Development Tools**
- **VS Code**: Primary development environment
- **Git**: Version control and collaboration
- **PowerShell**: Deployment and testing scripts

---

## 🚀 Getting Started

### **Prerequisites**
```bash
Python 3.8+
Flask 2.0+
Azure Custom Vision Account
Modern web browser with camera support
```

### **Installation**

1. **Clone the Repository**
```bash
git clone https://github.com/Jason-Z1/TrashVision.git
cd TrashVision
```

2. **Install Dependencies**
```bash
pip install flask requests python-dotenv
```

3. **Configure Environment Variables**
Create a `.env` file in the `backend` directory:
```env
PREDICTION_KEY=your_azure_prediction_key
TRAINING_KEY=your_azure_training_key  
PREDICTION_ENDPOINT=your_azure_endpoint
PROJECT_ID=your_project_id
PUBLISHED_NAME=trashvision-v3
```

4. **Run the Application**
```bash
cd backend/scripts
python test_predict.py
```

5. **Access the App**
Open your browser to `http://localhost:5000`

---

## Usage Guide

### **Taking a Photo**
1. Click **"Take Snapshot"** to access your camera
2. Position the item in the camera viewfinder
3. Click the capture button
4. View AI analysis results instantly

### **Uploading a Photo** 
1. Click **"Upload Photo"** next to the snapshot button
2. Select an image file from your device
3. Wait for processing and AI analysis
4. Review recycling recommendations

### **Understanding Results**
- **Item Type**: Recyclable or Non-recyclable classification
- **Confidence**: Percentage accuracy of the prediction
- **Recommendations**: Specific guidance for disposal

---

## API Endpoints

### **Main Routes**
- `GET /` - Serves the main web application
- `POST /predict` - Handles image prediction requests
- `GET /resources/<path>` - Serves static assets
- `GET /Images/<path>` - Serves image resources

### **Prediction API**
```python
# POST /predict
Content-Type: multipart/form-data
Body: image file

Response:
{
  "detected_items": [
    {
      "type": "recyclable",
      "confidence": 0.87,
      "recyclable": true
    }
  ],
  "recommendations": [
    "Recyclable item can be placed in recycling bin"
  ]
}
```

---

## Design Philosophy

### **Sustainability Focus**
- Earth-toned color palette reflecting nature
- Minimal resource usage and efficient code
- Educational content promoting environmental awareness

### **User Experience**
- Single-screen layout eliminating scrolling
- Intuitive controls with clear visual feedback
- Responsive design adapting to any device size

### **Accessibility**
- High contrast ratios for readability
- ARIA labels for screen readers
- Keyboard navigation support

---

## Project Highlights

- *** Hackathon Project***: Built during NJIT Hackathon Fall 2025
- *** Problem-Solving**: Addresses real-world recycling confusion
- *** Innovation**: Combines AI with environmental education
- *** Modern Tech**: Utilizes latest web APIs and cloud services
- *** Impact**: Promotes sustainable behavior change

---

##  Contributing

We welcome contributions to make Go Gaia even better! 

### **How to Contribute**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Azure Custom Vision** for providing powerful AI capabilities
- **NJIT Hackathon Fall 2025** for the opportunity and inspiration
- **Environmental Organizations** whose work motivates sustainable technology
- **Greek Mythology** for the Gaia inspiration representing Mother Earth

---

GirlHacks NJIT 2025
