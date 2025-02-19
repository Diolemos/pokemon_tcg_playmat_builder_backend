from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps
import io
import os
import logging

# Configure logging (using uvicorn's logger)
logger = logging.getLogger("uvicorn.error")

# Constants for playmat size (assuming 100 DPI)
PLAYMAT_WIDTH = 2400  # 24 inches × 100 DPI
PLAYMAT_HEIGHT = 1400  # 14 inches × 100 DPI

app = FastAPI()

# CORS setup: allow all origins (you can restrict this to your Netlify URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your Netlify URL if desired
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Playmat Builder API is running!"}

def resize_and_crop(image: Image.Image) -> Image.Image:
    """Resizes and crops an image to fit the 24" × 14" playmat size."""
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
        logger.info(f"Received file: {file.filename}, overlay: {overlay}")
        
        # Read and open the uploaded image
        contents = await file.read()
        user_image = Image.open(io.BytesIO(contents))
        
        # Resize and crop the user image to playmat size
        processed_image = resize_and_crop(user_image)
        
        # Build the absolute path for the overlay file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
        overlay_path = os.path.join(TEMPLATES_DIR, f"{overlay}_lines.png")
        logger.info(f"Looking for overlay file at: {overlay_path}")

        if not os.path.exists(overlay_path):
            raise HTTPException(status_code=404, detail=f"Overlay template not found at {overlay_path}")

        # Load and resize the overlay image
        overlay_image = Image.open(overlay_path).convert("RGBA")
        overlay_image = overlay_image.resize((PLAYMAT_WIDTH, PLAYMAT_HEIGHT), Image.LANCZOS)
        
        # Merge the images using alpha compositing
        final_image = Image.alpha_composite(processed_image, overlay_image)

        # Save the final image to a BytesIO buffer
        img_io = io.BytesIO()
        final_image.save(img_io, format="PNG")
        img_io.seek(0)
        
        logger.info("Image processed successfully, returning response.")
        return StreamingResponse(
            img_io,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=playmat.png"}
        )

    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
