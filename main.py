from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io

app = FastAPI()

@app.post("/extract-metadata")
async def extract_metadata(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        width, height = img.size
        dpi = img.info.get("dpi", ("unknown", "unknown"))

        return JSONResponse(content={
            "filename": file.filename,
            "width_px": width,
            "height_px": height,
            "dpi_x": dpi[0],
            "dpi_y": dpi[1]
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
