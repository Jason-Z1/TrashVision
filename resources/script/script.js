// Vanilla JavaScript for TrashVision Camera App
let videoStream = null;
let capturedImageData = null;

// Facts array for rotation
const facts = [
    "Recycling a single aluminum can saves enough energy to power a TV for three hours.",
    "Gaia (Mother Earth) is the oldest Greek deity—reminding us that the planet is the original resource.",
    "Making new paper from recycled pulp uses about 60% less energy than making it from trees.",
    "Demeter's cycles of season show us that materials must be continually renewed, not wasted.",
    "Nearly 75% of all waste is recyclable, yet less than 35% is currently recycled in the U.S.",
    "Artemis protects the wild: Recycling just one ton of plastic saves over 7,000 kWh of energy.",
    "Glass is 100% recyclable and can be reused endlessly without any loss in quality. ♻️",
    "Recycling paper saves trees, but it also reduces air pollution by 73% compared to making new paper.",
    "It takes a plastic bottle approximately 450 years to decompose in a landfill. ⏳"
];

let currentFactIndex = 0;

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', function() {
    startCamera();
    startFactRotation();
    setupEventListeners();
});

// Start camera stream
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'environment'
            }
        });
        
        const video = document.getElementById('videoStream');
        video.srcObject = stream;
        videoStream = stream;
        
        console.log('Camera started successfully');
    } catch (error) {
        console.error('Camera error:', error);
        alert('Camera access denied or unavailable.');
    }
}

// Start fact rotation
function startFactRotation() {
    setInterval(() => {
        currentFactIndex = (currentFactIndex + 1) % facts.length;
        document.getElementById('factText').textContent = facts[currentFactIndex];
    }, 10000); // Change every 10 seconds
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('takeSnapshotBtn').addEventListener('click', takeSnapshot);
    document.getElementById('retakeBtn').addEventListener('click', retakePhoto);
    document.getElementById('downloadBtn').addEventListener('click', downloadImage);
}

// Take snapshot function
function takeSnapshot() {
    console.log('Taking snapshot...');
    
    const video = document.getElementById('videoStream');
    const canvas = document.getElementById('captureCanvas');
    const context = canvas.getContext('2d');
    
    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to image data
    capturedImageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Show captured image
    document.getElementById('capturedImage').src = capturedImageData;
    document.getElementById('cameraContainer').style.display = 'none';
    document.getElementById('capturedContainer').style.display = 'block';
    document.getElementById('takeSnapshotBtn').style.display = 'none';
    document.getElementById('actionButtons').style.display = 'block';
    
    // Send to prediction API
    sendToPredictionAPI(capturedImageData);
    
    console.log('📸 Snapshot taken successfully');
}

// Retake photo function
function retakePhoto() {
    document.getElementById('cameraContainer').style.display = 'block';
    document.getElementById('capturedContainer').style.display = 'none';
    document.getElementById('takeSnapshotBtn').style.display = 'block';
    document.getElementById('actionButtons').style.display = 'none';
    capturedImageData = null;
    
    console.log('Retaking photo');
}

// Send image to prediction API
async function sendToPredictionAPI(imageDataUrl) {
    try {
        console.log('Sending image to prediction API...');
        
        // Convert base64 to blob
        const byteString = atob(imageDataUrl.split(',')[1]);
        const mimeString = imageDataUrl.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        
        const blob = new Blob([ab], { type: mimeString });
        const formData = new FormData();
        formData.append('image', blob, 'snapshot.jpg');
        
        // Send to Flask API
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Prediction results:', data);
        
        // Log detected items in detail
        if (data.detected_items && data.detected_items.length > 0) {
            console.log('\n=== DETECTED ITEMS ===');
            data.detected_items.forEach((item, index) => {
                console.log(`${index + 1}. Type: ${item.type}`);
                console.log(`   Confidence: ${(item.confidence * 100).toFixed(1)}%`);
                console.log(`   Recyclable: ${item.recyclable ? '♻️ Yes' : '🗑️ No'}`);
            });
        }
        
        if (data.recommendations && data.recommendations.length > 0) {
            console.log('\n=== RECOMMENDATIONS ===');
            data.recommendations.forEach((rec, index) => {
                console.log(`${index + 1}. ${rec}`);
            });
        }
        
        // Display results
        displayPredictionResults(data);
        
    } catch (error) {
        console.error('Prediction error:', error);
        alert(`Prediction failed: ${error.message}. Make sure the Flask server is running on port 5000.`);
    }
}

// Display prediction results
function displayPredictionResults(data) {
    if (data.error) {
        alert(`Error: ${data.error}`);
        return;
    }
    
    const items = data.detected_items || [];
    const recommendations = data.recommendations || [];
    
    console.log('Detected Items:', items);
    console.log('Recommendations:', recommendations);
    
    let message = 'Prediction Results:\n\n';
    
    if (items.length > 0) {
        items.forEach((item, index) => {
            const confidence = Math.round(item.confidence * 100);
            const icon = item.recyclable ? '♻️' : '🗑️';
            message += `${icon} ${item.type} (${confidence}% confidence)\n`;
        });
        
        if (recommendations.length > 0) {
            message += '\nRecommendations:\n';
            recommendations.forEach(rec => {
                message += `• ${rec}\n`;
            });
        }
    } else {
        message += 'No items detected with high confidence.';
    }
    
    

    alert(message);
}

// Cleanup function when page unloads
window.addEventListener('beforeunload', function() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
    }
});

