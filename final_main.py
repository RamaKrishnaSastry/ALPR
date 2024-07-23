from ultralytics import YOLO
import cv2
import numpy as np
from Sort.sort import *
from utilities import *
from add_to_database import *
import time
from pprint import pprint

# Initialize models and tracker
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('license_plate_detector.pt')
mot_tracker = Sort()

score_threshold = 0.2

# Capture video
img_path = "car2.mp4"
capture = cv2.VideoCapture(img_path)
frame_no = -1
ret = True

# Define vehicle classes
vehicles = [1, 2, 3, 5, 7]

while ret:
    ret, frame = capture.read()
    if not ret:
        break

    # cv2.imshow("frame", frame)
    # cv2.waitKey(1)

    vehicle_detection = coco_model(frame)[0]
    detections = []
    license_plates = []

    if vehicle_detection:
        frame_no += 2
        for detection in vehicle_detection.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections.append(detection[:-1])
        
        try:
            track_ids = mot_tracker.update(np.asarray(detections))
        except Exception as e:
            print(f"Tracker update failed: {e}")
            mot_tracker = Sort()
            track_ids = mot_tracker.update(np.asarray(detections))

        licenseplate_detection = license_plate_detector(frame)[0]
        for numberplate in licenseplate_detection.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = numberplate
            license_plates.append(numberplate[:-1])
            xcar1, ycar1, xcar2, ycar2, car_id = get_required_car(numberplate, track_ids)

            try:
                a = get_conformation(car_id)
            except Exception as e:
                a = False

            if not a:
                frame_no += 2
                cropped_license_plate = frame[int(y1):int(y2), int(x1):int(x2)]
                if 0 == 0: #0.3 * frame.shape[1] < x1 < 0.7 * frame.shape[1] and 0.3 * frame.shape[0] < y1 < 0.7 * frame.shape[0]:
                    enhanced_image = enhance_plate(cropped_license_plate)
                    threshold_greyed_plate = process_nameplate(enhanced_image)
                    threshold_greyed_plate = cv2.resize(threshold_greyed_plate, (500, 200))
                    plt.imshow(threshold_greyed_plate, cmap='gray')
                    plt.show()
                    a = json.loads(get_text(threshold_greyed_plate))
                    pprint(a)


                    if a:
                        licence_plate_text, liense_plate_detection_score = a["results"][0]["plate"], a["results"][0]["dscore"]
                        print("Detected text:", licence_plate_text, liense_plate_detection_score)
                        
                        if licence_plate_text and liense_plate_detection_score > score_threshold:
                            print("Adding to database")
                            add_to_database(licence_plate_text, liense_plate_detection_score, car_id, time.time())

    print(f"Processed frame no. {frame_no}")

capture.release()
cv2.destroyAllWindows()
