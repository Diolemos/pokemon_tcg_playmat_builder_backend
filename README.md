# Playmat Builder Backend  

This is the backend service for the **Playmat Builder** app, built with **FastAPI**. It processes user-uploaded images, resizes them to playmat dimensions, applies an overlay (black or white), and returns the final image for download.
The goal is to let users easily build custom pokemon tcg playmats.

### Credits for the ovelays: some IMGUR.com user, thank you ❤️ https://imgur.com/a/pokemon-playmats-U2NQQ

## 🚀 Features  
- ✅ Upload an image and resize it to **24" × 14"** (2400 × 1400 pixels)  
- ✅ Apply a transparent **white or black** overlay  
- ✅ Return the processed image for preview and download  
- ✅ **CORS enabled** for frontend communication  

## 🛠 Installation & Setup  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/playmat-builder-backend.git
cd playmat-builder-backend
```
### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt

```

### 4️⃣ Run the Server

```bash
uvicorn main:app --reload


```

## 🔗 API Endpoints

| Method  | Endpoint  | Description  |
|---------|----------|--------------|
| **GET**  | `/`       | Check if the API is running |
| **POST** | `/upload/` | Upload an image and generate a playmat |


### Body (multipart/form-data):

- file: The image file to upload
- overlay: "black" or "white"
