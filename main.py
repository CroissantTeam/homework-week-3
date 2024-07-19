
import os
import io
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import numpy as np
from typing import List

app = FastAPI()

# Create a directory to store uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

def get_to_Embedding_vector(byte_image: bytes) -> np.ndarray:
    # Dummy implementation
    return np.random.rand(128)  # Example vector size, replace with your actual implementation

def search(embedded_vector: np.ndarray) -> np.ndarray:
    # Dummy implementation
    return np.random.randint(0, 100, 5)  # Example results, replace with your actual implementation

# def get_to_Embedding_vectors(byte_image: bytes) -> List[np.ndarray]:
#     # Dummy implementation
#     return [np.random.rand(128)]  # Example list of embeded vector 

# def search(embedded_vectors: List[np.ndarray]) -> List[np.ndarray]:
#     # Dummy implementation
#     return [np.random.randint(0, 100, 5)]  # Example list of results

async def search_images(files: List[UploadFile]):
    """
    Find similar images in database
    
    Args:
        files: List[UploadFile]
    Returns:
        List[List[int]]: List of lists of indexes of similar images
    """
    results = []
    for file in files:
        byte_image = await file.read()
        image = Image.open(io.BytesIO(byte_image))
        embedded_vector: np.ndarray = get_to_Embedding_vector(byte_image)
        result: np.ndarray = search(embedded_vector)
        results.append(result.tolist())
    return results

@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile]):
    search_results = await search_images(files)
    saved_file_urls = []

    for file in files:
        file_extension = file.filename.split(".")[-1]
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_extension}")
        
        with open(file_path, "wb") as f:
            await file.seek(0)
            f.write(await file.read())
        
        saved_file_urls.append(f"/uploads/{file_id}.{file_extension}")

    response_content = "<html><body>"
    for i, file_url in enumerate(saved_file_urls):
        response_content += f'<h3>Uploaded Image:</h3>'
        response_content += f'<img src="{file_url}" alt="Uploaded Image" style="width:200px;height:auto;">'
        response_content += f'<h3>Similar Images:</h3>'
        for index in search_results[i]:
            # Here, you should replace this with actual similar image URLs from your database
            similar_image_url = f"/uploads/similar_image_{index}.jpg"
            response_content += f'<img src="{similar_image_url}" alt="Similar Image" style="width:100px;height:auto;">'
        response_content += "<hr>"
    response_content += "</body></html>"

    return HTMLResponse(content=response_content)

@app.get("/")
async def main():
    content = """
    <body>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)