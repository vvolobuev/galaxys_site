from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import cv2
import base64
from typing import List
import os
from datetime import datetime
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

yolo = TritonYOLO(server_url=TRITON_URL, conf_threshold=0.5, iou_threshold=0.45)

@app.get("/health")
async def health_check():
    try:
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)