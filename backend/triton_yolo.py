import cv2
import numpy as np
import tritonclient.http as httpclient

class TritonYOLO:
    def __init__(self, server_url, conf_threshold, iou_threshold):
        self.client = httpclient.InferenceServerClient(url=server_url)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.img_w = None
        self.img_h = None
        
    def prepare_input(self, image):
        self.img_h, self.img_w = image.shape[:2]
        input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_img = cv2.resize(input_img, (224, 224))
        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)
        return input_tensor
    
    def run(self, image):
        input_tensor = self.prepare_input(image)
        inputs = [httpclient.InferInput("images", input_tensor.shape, "FP32")]
        inputs[0].set_data_from_numpy(input_tensor)
        outputs = [httpclient.InferRequestedOutput("output0")]
        response = self.client.infer("yolo12", inputs=inputs, outputs=outputs)
        output = response.as_numpy("output0")
        return self.process_output([output])
    
    def process_output(self, output):
        predictions = np.squeeze(output[0]).T
        scores = np.max(predictions[:, 4:], axis=1)
        predictions = predictions[scores > self.conf_threshold, :]
        scores = scores[scores > self.conf_threshold]
        if len(scores) == 0:
            return [], [], []
        class_ids = np.argmax(predictions[:, 4:], axis=1)
        boxes = self.extract_boxes(predictions)
        indices = self.nms(boxes, scores, self.iou_threshold)
        return boxes[indices], scores[indices], class_ids[indices]

    def extract_boxes(self, predictions):
        boxes = predictions[:, :4]
        boxes = self.rescale_boxes(boxes, (224, 224), (self.img_h, self.img_w))
        boxes = self.yolo_to_standard(boxes)
        boxes[:, 0] = np.clip(boxes[:, 0], 0, self.img_w)
        boxes[:, 1] = np.clip(boxes[:, 1], 0, self.img_h)
        boxes[:, 2] = np.clip(boxes[:, 2], 0, self.img_w)
        boxes[:, 3] = np.clip(boxes[:, 3], 0, self.img_h)
        return boxes

    def nms(self, boxes, scores, iou_threshold):
        sorted_indices = np.argsort(scores)[::-1]
        keep_boxes = []
        while sorted_indices.size > 0:
            box_id = sorted_indices[0]
            keep_boxes.append(box_id)
            ious = self.compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])
            keep_indices = np.where(ious < iou_threshold)[0]
            sorted_indices = sorted_indices[keep_indices + 1]
        return keep_boxes

    def compute_iou(self, box, boxes):
        xmin = np.maximum(box[0], boxes[:, 0])
        ymin = np.maximum(box[1], boxes[:, 1])
        xmax = np.minimum(box[0] + box[2], boxes[:, 0] + boxes[:, 2])
        ymax = np.minimum(box[1] + box[3], boxes[:, 1] + boxes[:, 3])
        intersection_area = np.maximum(0, xmax - xmin) * np.maximum(0, ymax - ymin)
        box_area = box[2] * box[3]
        boxes_area = boxes[:, 2] * boxes[:, 3]
        union_area = box_area + boxes_area - intersection_area
        iou = intersection_area / union_area
        return iou

    def yolo_to_standard(self, x):
        y = np.copy(x)
        y[..., 0] = x[..., 0] - x[..., 2] / 2
        y[..., 1] = x[..., 1] - x[..., 3] / 2
        return y

    def rescale_boxes(self, boxes, input_shape, image_shape):
        input_shape = np.array([input_shape[1], input_shape[0], input_shape[1], input_shape[0]])
        boxes = np.divide(boxes, input_shape, dtype=np.float32)
        boxes *= np.array([image_shape[1], image_shape[0], image_shape[1], image_shape[0]])
        return boxes