import tensorflow as tf
import numpy as np
import cv2

__all__ = (
    "draw_boxes",
    "non_max_suppression",
    "classify_banana_type",
    "post_process_detections"
)


# Function to draw bounding boxes on the image
def draw_boxes(image, boxes, class_names, scores, threshold=0.5):
    for box, class_name, score in zip(boxes, class_names, scores):
        if score >= threshold:
            ymin, xmin, ymax, xmax = box
            color = (255, 0, 0)
            image_height, image_width, _ = image.shape
            start_point = (int(xmin * image_width), int(ymin * image_height))
            end_point = (int(xmax * image_width), int(ymax * image_height))
            image = cv2.rectangle(image, start_point, end_point, color, 2)
            text = f'{class_name}: {int(score * 100)}%'
            image = cv2.putText(image, text, start_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return image


# Function to apply Non-Maximum Suppression (NMS)
def non_max_suppression(boxes, scores, threshold=0.5):
    indices = tf.image.non_max_suppression(
        boxes, scores, max_output_size=50, iou_threshold=threshold
    ).numpy()
    return boxes[indices], scores[indices]


# Function to classify the type of banana
def classify_banana_type(banana_image, model, banana_type_labels):
    banana_image = cv2.resize(banana_image, (100, 100))  # Resize to the input size of your classifier
    banana_image = np.expand_dims(banana_image, axis=0)  # Add batch dimension
    banana_image = banana_image / 255.0  # Normalize
    predictions = model.predict(banana_image)
    predicted_class = np.argmax(predictions)
    return banana_type_labels[predicted_class]


# Apply additional post-processing to count bananas
def post_process_detections(boxes, scores, threshold=0.5):
    # Filter boxes and scores based on confidence threshold
    filtered_indices = np.where(scores >= threshold)[0]
    filtered_boxes = boxes[filtered_indices]
    filtered_scores = scores[filtered_indices]
    return filtered_boxes, filtered_scores