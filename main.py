from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from PIL import Image, ImageOps
from fastapi.middleware.cors import CORSMiddleware
import io
import uuid
import os

# Create the output directory if it doesn't exist
OUTPUT_FOLDER = "output/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



app = FastAPI()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))  
    uvicorn.run(app, host="0.0.0.0", port=port)

# Constants for playmat size (assuming 100 DPI)
PLAYMAT_WIDTH = 2400  # 24 inches × 100 DPI
PLAYMAT_HEIGHT = 1400  # 14 inches × 100 DPI
OUTPUT_FOLDER = "output/"

def resize_and_crop(image: Image.Image) -> Image.Image:
    """ Resizes and crops an image to fit the 24" × 14" playmat size """
    # Convert to RGBA (to avoid transparency issues)
    image = image.convert("RGBA")
    
    # Get original size
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
    # Load user image
    user_image = Image.open(io.BytesIO(await file.read()))

    # Resize & crop
    processed_image = resize_and_crop(user_image)

    # Load overlay (replace with actual file paths)
    overlay_path = f"templates/{overlay}_lines.png"
    overlay_image = Image.open(overlay_path).convert("RGBA")

    # Ensure overlay matches playmat size
    overlay_image = overlay_image.resize((PLAYMAT_WIDTH, PLAYMAT_HEIGHT), Image.LANCZOS)

    # Merge images
    final_image = Image.alpha_composite(processed_image, overlay_image)

    # Save the final image
    output_path = f"{OUTPUT_FOLDER}{uuid.uuid4().hex}.png"
    final_image.save(output_path, format="PNG")

    print(f"Received overlay: {overlay}")
    return FileResponse(output_path, filename="playmat.png")
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
