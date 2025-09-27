const { useState, useRef, useEffect } = React;

const TrashVisionApp = () => {
    const [isStreaming, setIsStreaming] = useState(false);
    const [capturedImage, setCapturedImage] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [error, setError] = useState(null);
    const [showPreview, setShowPreview] = useState(true);
    const [savedImages, setSavedImages] = useState([]);
    
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const previewCanvasRef = useRef(null);
    const streamRef = useRef(null);
    const animationFrameRef = useRef(null);
    
    // Load saved images on component mount
    useEffect(() => {
        try {
            const stored = JSON.parse(localStorage.getItem('trashvision_images') || '[]');
            setSavedImages(stored);
        } catch (error) {
            console.error('Error loading saved images:', error);
        }
    }, []);
    
    // Update preview canvas with live video feed
    const updatePreview = () => {
        if (videoRef.current && previewCanvasRef.current && isStreaming) {
            const video = videoRef.current;
            const canvas = previewCanvasRef.current;
            const context = canvas.getContext('2d');
            
            if (video.videoWidth && video.videoHeight) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                // Clear canvas
                context.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw video frame
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                // Add overlay effects only if showPreview is true
                if (showPreview) {
                    // Add overlay effects for better visualization
                    context.strokeStyle = '#667eea';
                    context.lineWidth = 3;
                    context.setLineDash([10, 5]);
                    
                    // Draw a focus frame
                    const frameMargin = 40;
                    context.strokeRect(
                        frameMargin, 
                        frameMargin, 
                        canvas.width - frameMargin * 2, 
                        canvas.height - frameMargin * 2
                    );
                    
                    // Add crosshair in center
                    const centerX = canvas.width / 2;
                    const centerY = canvas.height / 2;
                    const crosshairSize = 20;
                    
                    context.setLineDash([]);
                    context.lineWidth = 2;
                    context.strokeStyle = '#ff6b6b';
                    
                    // Horizontal line
                    context.beginPath();
                    context.moveTo(centerX - crosshairSize, centerY);
                    context.lineTo(centerX + crosshairSize, centerY);
                    context.stroke();
                    
                    // Vertical line
                    context.beginPath();
                    context.moveTo(centerX, centerY - crosshairSize);
                    context.lineTo(centerX, centerY + crosshairSize);
                    context.stroke();
                    
                    // Add text overlay
                    context.font = '16px -apple-system, BlinkMacSystemFont, sans-serif';
                    context.fillStyle = 'rgba(255, 255, 255, 0.9)';
                    context.fillRect(10, 10, 200, 30);
                    context.fillStyle = '#333';
                    context.fillText('📸 Frame your trash item', 15, 30);
                }
            }
        }
        
        if (isStreaming) {
            animationFrameRef.current = requestAnimationFrame(updatePreview);
        }
    };

    // Start camera stream
    const startCamera = async () => {
        try {
            setError(null);
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use back camera on mobile if available
                }
            });
            
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                streamRef.current = stream;
                setIsStreaming(true);
                
                // Start preview updates when video is loaded
                videoRef.current.addEventListener('loadedmetadata', () => {
                    updatePreview();
                });
            }
        } catch (err) {
            console.error('Error accessing camera:', err);
            setError('Unable to access camera. Please ensure you have granted camera permissions.');
        }
    };
    
    // Stop camera stream
    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
        }
        setIsStreaming(false);
        setCapturedImage(null);
        setAnalysisResult(null);
    };
    
    // Save image to temporary site data (localStorage)
    const saveImageToStorage = (imageDataUrl, timestamp) => {
        try {
            const currentSaved = JSON.parse(localStorage.getItem('trashvision_images') || '[]');
            const newImage = {
                id: timestamp,
                dataUrl: imageDataUrl,
                timestamp: timestamp,
                date: new Date(timestamp).toLocaleString()
            };
            
            const updatedImages = [...currentSaved, newImage];
            
            // Keep only the last 10 images to avoid storage issues
            if (updatedImages.length > 10) {
                updatedImages.splice(0, updatedImages.length - 10);
            }
            
            localStorage.setItem('trashvision_images', JSON.stringify(updatedImages));
            setSavedImages(updatedImages);
            console.log('Image saved to local storage:', newImage.date);
            return newImage.id;
        } catch (error) {
            console.error('Error saving image to storage:', error);
            return null;
        }
    };
    
    // Download image function
    const downloadImage = (imageDataUrl, filename) => {
        const link = document.createElement('a');
        link.download = filename || `trashvision_${new Date().getTime()}.jpg`;
        link.href = imageDataUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Capture snapshot
    const captureSnapshot = () => {
        if (!videoRef.current || !canvasRef.current) return;
        
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Get image data
        const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
        setCapturedImage(imageDataUrl);
        
        // Save image to temporary storage
        const timestamp = new Date().getTime();
        const imageId = saveImageToStorage(imageDataUrl, timestamp);
        
        if (imageId) {
            // Show success message briefly
            setError(`✅ Image saved successfully!`);
            setTimeout(() => setError(null), 2000);
        }
        
        // Simulate API call (replace with actual backend call later)
        analyzeImage(imageDataUrl);
    };
    
    // Simulate backend API call for image analysis
    const analyzeImage = async (imageData) => {
        setIsAnalyzing(true);
        setAnalysisResult(null);
        
        try {
            // TODO: Replace this with actual API call to your backend
            // const response = await fetch('/api/analyze', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify({ image: imageData })
            // });
            // const result = await response.json();
            
            // Simulate API delay and response
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Mock analysis result
            const mockResult = {
                detected_items: [
                    { type: 'plastic_bottle', confidence: 0.95, recyclable: true },
                    { type: 'food_waste', confidence: 0.87, recyclable: false }
                ],
                recommendations: [
                    'Plastic bottle can be recycled in plastic recycling bin',
                    'Food waste should go in compost or general waste'
                ]
            };
            
            setAnalysisResult(mockResult);
        } catch (err) {
            console.error('Analysis error:', err);
            setError('Failed to analyze image. Please try again.');
        } finally {
            setIsAnalyzing(false);
        }
    };
    
    // Retake photo
    const retakePhoto = () => {
        setCapturedImage(null);
        setAnalysisResult(null);
    };
    
    return (
        <div className="app">
            <header className="header">
                <h1>🗑️ TrashVision</h1>
                <p>AI-Powered Waste Classification & Recycling Assistant</p>
            </header>
            
            <main className="main-content">
                <div className="app-container">
                    {/* Always visible preview area */}
                    <div className="preview-section">
                        <div className="camera-preview-container">
                            {!isStreaming ? (
                                <div className="preview-placeholder">
                                    <div className="placeholder-content">
                                        <div className="placeholder-icon">📷</div>
                                        <h3>Preview</h3>
                                        <p>Turn camera on to see live preview</p>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    {/* Hidden video element for camera stream */}
                                    <video 
                                        ref={videoRef}
                                        autoPlay 
                                        playsInline 
                                        className="video-stream-hidden"
                                        style={{ display: 'none' }}
                                    />
                                    
                                    {/* Visible canvas with live preview and overlays */}
                                    <canvas 
                                        ref={previewCanvasRef}
                                        className="preview-canvas"
                                    />
                                    
                                    <div className="preview-overlay">
                                        <div className="preview-controls">
                                            <button 
                                                className={`btn btn-icon ${showPreview ? 'active' : ''}`}
                                                onClick={() => setShowPreview(!showPreview)}
                                                title="Toggle preview effects"
                                            >
                                                {showPreview ? '🎯' : '📹'}
                                            </button>
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                        
                        {/* Camera controls */}
                        <div className="camera-controls">
                            {!isStreaming ? (
                                <button 
                                    className="btn btn-primary btn-large"
                                    onClick={startCamera}
                                >
                                    📷 Start Camera
                                </button>
                            ) : (
                                <>
                                    <button 
                                        className="btn btn-secondary"
                                        onClick={stopCamera}
                                    >
                                        ❌ Stop Camera
                                    </button>
                                    {!capturedImage && (
                                        <button 
                                            className="btn btn-primary btn-capture"
                                            onClick={captureSnapshot}
                                        >
                                            � Capture
                                        </button>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                    
                    {/* Content area */}
                    <div className="content-section">
                        {!capturedImage ? (
                            <div className="welcome-content">
                                <h2>Ready to analyze your waste?</h2>
                                <p>Take a photo of your trash item and get instant recycling guidance!</p>
                                
                                {savedImages.length > 0 && (
                                    <div className="saved-images-section">
                                        <h3>📁 Recent Photos ({savedImages.length})</h3>
                                        <div className="saved-images-grid">
                                            {savedImages.slice(-6).reverse().map((image) => (
                                                <div key={image.id} className="saved-image-item">
                                                    <img 
                                                        src={image.dataUrl} 
                                                        alt={`Saved ${image.date}`}
                                                        className="saved-image-thumbnail"
                                                        onClick={() => downloadImage(image.dataUrl, `trashvision_${image.id}.jpg`)}
                                                        title={`Click to download - Taken: ${image.date}`}
                                                    />
                                                    <div className="saved-image-info">
                                                        <small>{new Date(image.timestamp).toLocaleDateString()}</small>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        <button 
                                            className="btn btn-secondary"
                                            onClick={() => {
                                                localStorage.removeItem('trashvision_images');
                                                setSavedImages([]);
                                            }}
                                        >
                                            🗑️ Clear All Images
                                        </button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="captured-image-section">
                                <div className="image-container">
                                    <img 
                                        src={capturedImage} 
                                        alt="Captured trash item"
                                        className="captured-image"
                                    />
                                </div>
                                
                                {isAnalyzing ? (
                                    <div className="analyzing">
                                        <div className="spinner"></div>
                                        <p>🤖 Analyzing image...</p>
                                    </div>
                                ) : analysisResult ? (
                                    <div className="analysis-results">
                                        <h3>🔍 Analysis Results</h3>
                                        <div className="detected-items">
                                            <h4>Detected Items:</h4>
                                            {analysisResult.detected_items.map((item, index) => (
                                                <div key={index} className="detected-item">
                                                    <span className="item-type">{item.type.replace('_', ' ')}</span>
                                                    <span className="confidence">
                                                        {(item.confidence * 100).toFixed(1)}% confidence
                                                    </span>
                                                    <span className={`recyclable ${item.recyclable ? 'yes' : 'no'}`}>
                                                        {item.recyclable ? '♻️ Recyclable' : '🗑️ Not Recyclable'}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                        
                                        <div className="recommendations">
                                            <h4>♻️ Recommendations:</h4>
                                            <ul>
                                                {analysisResult.recommendations.map((rec, index) => (
                                                    <li key={index}>{rec}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                ) : null}
                                
                                <div className="action-buttons">
                                    <button 
                                        className="btn btn-secondary"
                                        onClick={retakePhoto}
                                    >
                                        🔄 Retake Photo
                                    </button>
                                    <button 
                                        className="btn btn-secondary"
                                        onClick={() => downloadImage(capturedImage, `trashvision_${new Date().getTime()}.jpg`)}
                                    >
                                        💾 Download Image
                                    </button>
                                    <button 
                                        className="btn btn-primary"
                                        onClick={stopCamera}
                                    >
                                        ✅ Done
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
                
                {error && (
                    <div className={`message ${error.includes('✅') ? 'success-message' : 'error-message'}`}>
                        <p>{error.includes('⚠️') ? error : error}</p>
                    </div>
                )}
            </main>
            
            {/* Hidden canvas for image capture */}
            <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
        </div>
    );
};

// Render the app
ReactDOM.render(<TrashVisionApp />, document.getElementById('root'));