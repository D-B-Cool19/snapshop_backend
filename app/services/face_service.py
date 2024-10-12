import sys
from io import BytesIO
from typing import List, Tuple
# from ultralytics import YOLO
import onnxruntime as ort
import numpy as np
from werkzeug.datastructures import FileStorage
from PIL import Image
from dataclasses import dataclass
from insightface.app import FaceAnalysis


@dataclass
class User:
    faceEmbedding: List[float]
    xyxy: Tuple[int, int, int, int]


model_path = 'app/static/model/best.onnx'
session = ort.InferenceSession(model_path)
face_model = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
face_model.prepare(ctx_id=0)


def calculate_embedding(face_img):
    current_faces = face_model.get(face_img)
    if current_faces:
        embedding = current_faces[0].normed_embedding
        return embedding.tolist()
    return []


def nms(boxes, scores, iou_threshold=0.5):
    if len(boxes) == 0:
        return []
    boxes = np.array(boxes)
    scores = np.array(scores)

    keep = []
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        inter = w * h
        iou = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]

    return keep


def calculate_embeddings(face_img: FileStorage) -> List[User]:
    img_source = Image.open(BytesIO(face_img.read())).convert('RGB')
    original_width, original_height = img_source.size
    img_resized = img_source.resize((640, 640))
    img_normalized = np.asarray(img_resized).astype(np.float32) / 255.0

    img_transposed = np.transpose(img_normalized, (2, 0, 1))
    img_input = np.expand_dims(img_transposed, axis=0)
    inputs = {session.get_inputs()[0].name: img_input}
    outputs = session.run(None, inputs)

    output_data = np.squeeze(outputs[0])
    num_detections = 8400
    boxes: List[Tuple[int, int, int, int]] = []
    confidences: List[float] = []
    faces: List[User] = []

    for i in range(num_detections):
        x, y, w, h, conf = output_data[:, i]
        if conf < 0.4:
            continue
        left = int((x - w / 2) * original_width / 640)
        top = int((y - h / 2) * original_height / 640)
        width = int(w * original_width / 640)
        height = int(h * original_height / 640)
        boxes.append((left, top, left + width, top + height))
        confidences.append(conf)

    nms_indices = nms(boxes, confidences, iou_threshold=0.5)

    for i in nms_indices:
        left, top, right, bottom = boxes[i]
        single_face_img = img_source.crop((left, top, right, bottom))
        single_face_img = np.array(single_face_img)
        face_embedding = calculate_embedding(single_face_img)
        new_user = User(
            faceEmbedding=face_embedding,
            xyxy=(left, top, right - left, bottom - top)
        )
        faces.append(new_user)
    print(faces)
    return faces
