const { useRef, useEffect, useState } = React;

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
      
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImage(imageDataUrl);
    }
  };

  const downloadImage = () => {
    if (capturedImage) {
      const link = document.createElement('a');
      link.download = `snapshot_${new Date().getTime()}.jpg`;
      link.href = capturedImage;
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
        <h1 className="app-title">📷 Camera Preview</h1>
        
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

        {/* Hidden canvas for image capture */}
        <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
      </div>
    </div>
  );
}

// Actually render CameraPreview on page
ReactDOM.render(<CameraPreview />, document.getElementById("root"));
