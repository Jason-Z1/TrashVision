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

  const takeSnapshot = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
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
ReactDOM.render(<CameraPreview />,  document.getElementById("root"));
ReactDOM.render(<FactBar />, document.getElementById("fact-bar"));

