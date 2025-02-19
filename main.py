from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps
from fastapi.middleware.cors import CORSMiddleware
import io

import os



# Constants for playmat size (assuming 100 DPI)
PLAYMAT_WIDTH = 2400  # 24 inches × 100 DPI
PLAYMAT_HEIGHT = 1400  # 14 inches × 100 DPI

app = FastAPI()

port = int(os.environ.get('PORT', 10000))

# Bind the application to the specified port
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

def resize_and_crop(image: Image.Image) -> Image.Image:
    """ Resizes and crops an image to fit the 24" × 14" playmat size """
    image = image.convert("RGBA")
    
    original_width, original_height = image.size
    target_aspect = PLAYMAT_WIDTH / PLAYMAT_HEIGHT
    image_aspect = original_width / original_height

    if image_aspect > target_aspect:
        # Wider than necessary, crop width
        new_width = int(target_aspect * original_height)
        offset = (original_width - new_width) // 2
        image = image.crop((offset, 0, offset + new_width, original_height))
    else:
        # Taller than necessary, crop height
        new_height = int(original_width / target_aspect)
        offset = (original_height - new_height) // 2
        image = image.crop((0, offset, original_width, offset + new_height))

    # Resize to exact playmat size
    return image.resize((PLAYMAT_WIDTH, PLAYMAT_HEIGHT), Image.LANCZOS)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), overlay: str = Form("white")):
    """
    Uploads an image, resizes/crops it to playmat size, and applies an overlay.
    :param file: User image upload
    :param overlay: "black" or "white" overlay template
    :return: Processed image file
    """
    try:
        # Load user image
        user_image = Image.open(io.BytesIO(await file.read()))

        # Resize & crop
        processed_image = resize_and_crop(user_image)

        
        overlay_path = f"templates/{overlay}_lines.png"
        
        # Check if the overlay file exists
        if not os.path.exists(overlay_path):
            raise HTTPException(status_code=404, detail="Overlay template not found")
        #load overlay
        overlay_image = Image.open(overlay_path).convert("RGBA")

        # Ensure overlay matches playmat size
        overlay_image = overlay_image.resize((PLAYMAT_WIDTH, PLAYMAT_HEIGHT), Image.LANCZOS)

        # Merge images
        final_image = Image.alpha_composite(processed_image, overlay_image)

        img_io = io.BytesIO()
        final_image.save(img_io, format="PNG")
        img_io.seek(0)

        # Return as a streaming response
        return StreamingResponse(img_io, media_type="image/png", headers={"Content-Disposition": "inline; filename=playmat.png"})

        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, or replace "*" with ["http://localhost:5175"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def home():
    return {"message": "Playmat Builder API is running!"}
