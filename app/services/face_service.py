import sys
from io import BytesIO
from typing import List, Tuple
from ultralytics import YOLO
import numpy as np
from werkzeug.datastructures import FileStorage
from PIL import Image
from dataclasses import dataclass


@dataclass
class User:
    faceEmbedding: List[float]
    xyxy: Tuple[int, int, int, int]


model = YOLO('app/static/model/best.pt')


def calculate_embedding(face_img: FileStorage) -> List[User]:
    img = Image.open(BytesIO(face_img.read())).convert('RGB')
    img_source = np.array(img)
    results = model(img_source)
    faces: List[User] = []
    for result in results:
        for box in result.boxes:
            if box.cls == 0:
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                new_user = User(
                    faceEmbedding=[0.1, 0.2, 0.3, 0.4],
                    xyxy=(x1, y1, x2 - x1, y2 - y1)
                )
                faces.append(new_user)
    return faces
