const { useRef, useEffect, useState } = React;

function FactBar() {
  const [currentFactIndex, setCurrentFactIndex] = React.useState(0);
  const facts = [
    "Recycling a single aluminum can saves enough energy to power a TV for three hours.",
    "Gaia (Mother Earth) is the oldest Greek deity—reminding us that the planet is the original resource.",
    "Making new paper from recycled pulp uses about 60% less energy than making it from trees.",
    "Demeter's cycles of season show us that materials must be continually renewed, not wasted.",
    "Nearly 75% of all waste is recyclable, yet less than 35% is currently recycled in the U.S.",
    "Artemis protects the wild: Recycling just one ton of plastic saves over 7,000 kWh of energy.",
    "Glass is 100% recyclable and can be reused endlessly without any loss in quality. ♻️",
    "Recycling paper saves trees, but it also reduces air pollution by 73% compared to making new paper.",
    "It takes a plastic bottle approximately 450 years to decompose in a landfill. ⏳",
  ];

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFactIndex(prev => (prev + 1) % facts.length);
    }, 10000); // every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fact-bar">
      <p key={currentFactIndex} className="fact-text fade">
        {facts[currentFactIndex]}
      </p>
    </div>
  );
}


function CameraPreview() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);

  useEffect(() => {
    async function startCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment' 
          } 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          setStream(mediaStream);
        }
      } catch (err) {
        alert("Camera access denied or unavailable.");
      }
    }
    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);
  
  const sendCapturedImage = async (imageDataUrl) => {
    try {
      // Convert base64 to binary Blob
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
      
      console.log('Sending image to prediction API...');
      
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
        console.log('\n=== DETECTED ITEMS (Frontend) ===');
        data.detected_items.forEach((item, index) => {
          console.log(`${index + 1}. Type: ${item.type}`);
          console.log(`   Confidence: ${(item.confidence * 100).toFixed(1)}%`);
          console.log(`   Recyclable: ${item.recyclable ? '♻️ Yes' : '🗑️ No'}`);
        });
      }
      
      if (data.recommendations && data.recommendations.length > 0) {
        console.log('\n=== RECOMMENDATIONS (Frontend) ===');
        data.recommendations.forEach((rec, index) => {
          console.log(`${index + 1}. ${rec}`);
        });
      }
      
      // Display results to user
      displayPredictionResults(data);
      
    } catch (error) {
      console.error('Prediction error:', error);
      alert(`Prediction failed: ${error.message}. Make sure the Flask server is running on port 5000.`);
    }
  };

  const takeSnapshot = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImage(imageDataUrl);
      //Captures then sends image
      sendCapturedImage(imageDataUrl);
    }
  };


  const downloadImage = () => {
    if (capturedImage) {
      const link = document.createElement('a');
      link.download = `snapshot_${new Date().getTime()}.jpg`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const retakePhoto = () => {
    setCapturedImage(null);
  };

  const displayPredictionResults = (data) => {
    if (data.error) {
      alert(`Error: ${data.error}`);
      return;
    }
    
    const items = data.detected_items || [];
    const recommendations = data.recommendations || [];
    
    // Log detected items when displaying results
    console.log('Displaying results for detected items:', items);
    console.log('Displaying recommendations:', recommendations);
    
    let message = 'Prediction Results:\n\n';
    
    if (items.length > 0) {
      items.forEach(item => {
        const confidence = Math.round(item.confidence * 100);
        const recycleIcon = item.recyclable ? '♻️' : '🗑️';
        message += `${recycleIcon} ${item.type} (${confidence}% confidence)\n`;
      });
      
      message += '\nRecommendations:\n';
      recommendations.forEach(rec => {
        message += `• ${rec}\n`;
      });
    } else {
      message += 'No items detected with high confidence.';
    }
    
    alert(message);
  };

  return (
    <div className="app">
      <div className="main-container">
        
        <h1 className="app-title">Gaia's Guardians</h1>
        <p className="app-subtitle">Be a Guardian inspired by Gaia, one recycled item at a time.</p>


        <div className="preview-section">
          {!capturedImage ? ( 
            <div className="camera-preview-container">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                className="video-stream"
              />
            </div>
          ) : (
            <div className="captured-image-container">
              <img 
                src={capturedImage} 
                alt="Captured snapshot" 
                className="captured-image"
              />
            </div>
          )}
        </div>
        <div className="image-right-wrapper">
          <img src="Images/GreekGoddess.png" className="slideUp" alt="Greek Goddess" />
        </div>
        <div className="controls-section">
          {!capturedImage ? (
            <button 
              onClick={takeSnapshot} 
              className="btn btn-capture"
              >
              Take Snapshot
            </button>
          ) : (
            <div className="action-buttons">
              <button 
                onClick={retakePhoto} 
                className="btn btn-secondary"
              >
                Retake
              </button>
              <button 
                onClick={downloadImage} 
                className="btn btn-primary"
              >
                Download
              </button>
            </div>
          )}
        </div>

        
        
      </div>
    </div>
  );
}


// Actually render CameraPreview on page
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<CameraPreview />);

ReactDOM.render(<FactBar />, document.getElementById("fact-bar"));

