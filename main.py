from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 10000))

app = FastAPI(
    title="Image Metadata Extraction API",
    description="Extracts metadata from PNG/JPG images including dimensions and DPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-metadata")
async def extract_metadata(file: UploadFile = File(...)):
    """Extract metadata from uploaded image (PNG/JPG)"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG, JPEG, GIF, BMP, TIFF)")
        
        # Read file contents
        contents = await file.read()
        
        # Open image
        img = Image.open(io.BytesIO(contents))
        
        # Get basic dimensions
        width, height = img.size
        
        # Extract DPI (might not be present in all images)
        dpi = img.info.get("dpi", (None, None))
        
        # Extract additional metadata if available
        metadata = {
            "filename": file.filename,
            "format": img.format,
            "mode": img.mode,
            "width_px": width,
            "height_px": height,
            "dpi_x": dpi[0] if dpi[0] else "not specified",
            "dpi_y": dpi[1] if dpi[1] else "not specified",
            "file_size_bytes": len(contents),
            "file_size_mb": round(len(contents) / (1024 * 1024), 2)
        }
        
        # Calculate physical dimensions if DPI is available
        if dpi[0] and dpi[1] and isinstance(dpi[0], (int, float)) and isinstance(dpi[1], (int, float)):
            metadata["width_inches"] = round(width / dpi[0], 2)
            metadata["height_inches"] = round(height / dpi[1], 2)
            metadata["width_mm"] = round((width / dpi[0]) * 25.4, 2)
            metadata["height_mm"] = round((height / dpi[1]) * 25.4, 2)
        
        # PNG specific metadata
        if img.format == "PNG":
            png_info = img.info
            metadata["png_metadata"] = {}
            
            # Common PNG metadata fields
            for key in ['gamma', 'transparency', 'icc_profile', 'exif', 'description', 'software']:
                if key in png_info:
                    # Don't include binary data in response
                    if key not in ['icc_profile', 'exif']:
                        metadata["png_metadata"][key] = png_info[key]
                    else:
                        metadata["png_metadata"][key] = f"Present ({len(str(png_info[key]))} bytes)"
        
        logger.info(f"Successfully extracted metadata from {file.filename}")
        
        return JSONResponse(content=metadata)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Failed to process image: {str(e)}"}
        )

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "status": "healthy",
        "api": "Image Metadata Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "/": "This page",
            "/extract-metadata": "POST - Extract metadata from image",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "metadata-api"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
