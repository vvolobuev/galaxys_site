from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import cv2
import base64
from typing import List
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from triton_yolo import TritonYOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Object Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TRITON_URL = os.getenv("TRITON_URL", "host.docker.internal:8000")

STORAGE_PATH = Path("/app/storage/images")
METADATA_PATH = Path("/app/storage/metadata")
STORAGE_PATH.mkdir(parents=True, exist_ok=True)
METADATA_PATH.mkdir(parents=True, exist_ok=True)

yolo = TritonYOLO(server_url=TRITON_URL, conf_threshold=0.25, iou_threshold=0.3)

@app.get("/health")
async def health_check():
    try:
        dummy = np.zeros((224, 224, 3), dtype=np.uint8)
        boxes, scores, class_ids = yolo.run(dummy)
        triton_status = "connected"
    except Exception as e:
        logger.error(f"Triton health check error: {e}")
        triton_status = "disconnected"

    return {
        "status": "ok",
        "triton_status": triton_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/detect")
async def detect_objects(files: List[UploadFile] = File(...)):
    try:
        results = []
        
        for file in files:
            logger.info(f"Processing file: {file.filename}")
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error(f"Failed to decode image: {file.filename}")
                continue
            
            logger.info(f"Image shape: {image.shape}")
            
            try:
                boxes, scores, class_ids = yolo.run(image)
                logger.info(f"Detected {len(boxes)} objects")
            except Exception as e:
                logger.error(f"Triton inference error: {e}")
                boxes, scores, class_ids = [], [], []
            
            image_with_boxes = image.copy()
            
            for box, score, class_id in zip(boxes, scores, class_ids):
                x, y, w_box, h_box = box
                x = int(x)
                y = int(y)
                w_box = int(w_box)
                h_box = int(h_box)
                
                cv2.rectangle(image_with_boxes, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
                label = f"{int(class_id)}: {score:.2f}"
                cv2.putText(image_with_boxes, label, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            _, buffer = cv2.imencode('.jpg', image_with_boxes)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            detections = []
            for box, score, class_id in zip(boxes, scores, class_ids):
                detections.append({
                    "box": box.tolist(),
                    "confidence": float(score),
                    "class_id": int(class_id)
                })
            
            results.append({
                "filename": file.filename,
                "detections": detections,
                "image_base64": image_base64
            })
        
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/images/save")
async def save_image(data: dict):
    try:
        filename = data.get("filename", f"image_{uuid.uuid4()}.jpg")
        image_base64 = data.get("image_base64")
        detections = data.get("detections", [])
        
        logger.info(f"Saving image: {filename}")
        logger.info(f"Base64 data length: {len(image_base64) if image_base64 else 0}")
        
        if image_base64:
            try:
                image_data = base64.b64decode(image_base64)
                logger.info(f"Decoded image size: {len(image_data)} bytes")
                
                file_path = STORAGE_PATH / filename
                with open(file_path, "wb") as f:
                    f.write(image_data)
                logger.info(f"File saved: {file_path}")
            except Exception as e:
                logger.error(f"Base64 decode error: {e}")
        
        metadata = {
            "filename": filename,
            "detections": detections,
            "date": datetime.now().isoformat()
        }
        
        metadata_path = METADATA_PATH / f"{filename}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return {"status": "saved", "filename": filename}
        
    except Exception as e:
        logger.error(f"Error saving image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/api/images")
async def get_images():
    try:
        images = []
        for metadata_file in METADATA_PATH.glob("*.json"):
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                img_path = STORAGE_PATH / metadata["filename"]
                if img_path.exists():
                    with open(img_path, "rb") as img_f:
                        img_base64 = base64.b64encode(img_f.read()).decode('utf-8')
                        images.append({
                            "id": metadata_file.stem,
                            "filename": metadata["filename"],
                            "image_base64": img_base64,
                            "detections": metadata["detections"],
                            "date": metadata["date"]
                        })
        
        return {"images": images}
        
    except Exception as e:
        logger.error(f"Error loading images: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)