import cv2
import string
import easyocr
import numpy as np
import skimage.exposure as ski
import requests
import json

dict_char_to_int = {
    'O': '0',
    'U': '0',
    'I': '1',
    'L': '4',
    'B': '8',
    'G': '9',
    'Z': '2',
    'J': '3',
    'A': '4',
    'S': '5',
    'T': '7',
    'P': '4'
}

dict_int_to_char = {
    '0': 'O',
    '1': 'I',
    '8': 'B',
    '9': 'G',
    '2': 'Z',
    '3': 'J',
    '4': 'A',
    '5': 'S',
    '7': 'T'
}


def get_required_car(numberplate, track_id):
    x1, y1, x2, y2, score, class_id = numberplate
    for i in range(len(track_id)):
        x1_car, y1_car, x2_car, y2_car, car_id = track_id[i]
        # if x1+50>x1_car and y1>y1_car and x2-50<x2_car and y2-50<y2_car:
        if x1>x1_car and y1>y1_car and x2<x2_car and y2<y2_car:
            return track_id[i]
    return -1, -1, -1, -1, -1


def unsharp_masking(image, sigma=1.0, strength=1.5):
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    sharpened = cv2.addWeighted(image, 1 + strength, blurred, -strength, 0)
    return sharpened


def enhance_plate(cropped_license_plate):
    upscaled_plate = cv2.resize(cropped_license_plate, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    unsharped_image = unsharp_masking(upscaled_plate)
    enhanced_plate1 = cv2.resize(unsharped_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    enhanced_plate = cv2.medianBlur(enhanced_plate1, 5)
    return enhanced_plate



def license_complies_format(text):

    """
    This is for the indian standard license plates, not for all the plates.
    """
    if len(text) > 8 and len(text) < 11:
        if len(text) == 10:
            if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
                (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char.keys()) and \
                (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()) and \
                (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[6] in dict_char_to_int.keys()) and \
                (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[7] in dict_char_to_int.keys()) and \
                (text[8] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[8] in dict_char_to_int.keys()) and \
                (text[9] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()):
                return True
        elif len(text) == 9:
            if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
                (text[4] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()) and \
                (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[6] in dict_char_to_int.keys()) and \
                (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[7] in dict_char_to_int.keys()) and \
                (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[8] in dict_char_to_int.keys()) and \
                (text[8] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()):
                return True
        elif len(text) == 8:
            if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
                (text[3] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()) and \
                (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[6] in dict_char_to_int.keys()) and \
                (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[7] in dict_char_to_int.keys()) and \
                (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[8] in dict_char_to_int.keys()) and \
                (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()):
                return True

    else:
        return False
    

def final_check(text):
    if license_complies_format(text):
        return text
    return ''


def format_license(detected_text):
    "My code for Indian plates"
    text = detected_text.replace('g', '9')
    text = detected_text.replace(' ', '').upper()
    text = list(detected_text)
    text = [i for i in text if i.isalnum()]
    if len(text)>7:
        for i in [0, 1]:
            if text[i].isdigit() and text[i] in dict_int_to_char.keys():
                text[i] = dict_int_to_char[text[i]]
        for i in range(4):
            if text[-(i+1)].isalpha() and text[-(i+1)] in dict_char_to_int.keys():
                text[-(i+1)] = dict_char_to_int[text[-(i+1)]]
        if text[2].isalpha() and text[2] in dict_char_to_int.keys():
            text[2] = dict_char_to_int[text[2]]
        if text[-5].isdigit() and text[-5] in dict_int_to_char.keys():
            text[-5] = dict_int_to_char[text[-5]]
        if len(text[3:-5]) == 2:
            if text[3].isalpha() and text[3] in dict_char_to_int.keys():
                text[3] = dict_char_to_int[text[3]]
            if text[4].isdigit() and text[4] in dict_int_to_char.keys():
                text[4] = dict_int_to_char[text[4]]
        elif len(text[3:-5]) == 1:
            if text[3].isalpha() and text[3] in dict_char_to_int.keys():
                text[3] = dict_char_to_int[text[3]]
        return ''.join(text).upper()
    return ''
    

reader = easyocr.Reader(['en'], gpu = False)

#important function

def detect_text(cropped_license_plate):
    detections = reader.readtext(cropped_license_plate)
    if detections is not None:
        a, b = np.shape(cropped_license_plate)
        new_res = np.abs(a*b)
        if len(detections)==1:
            for detection in detections:
                if detection:
                    bbox, text, score = detection
                    if np.abs(area(bbox))>0.2*(new_res):
                        if final_check(format_license(text)):
                            return text, final_check(format_license(text)), score
                        else:
                            return '', '', 0
                return '', '', 0
        elif len(detections) > 1:
            res = ''
            c_score = []
            exceptions = ['IND', 'ONGOVERNMENTDUTY', 'ONGOVTDUTY', 'MINISTRYOFEDUCATION']
            for i in detections:
                bbox = i[0]
                if np.abs(area(bbox))>0.1*(new_res) and i[1] not in exceptions:
                    res = res+i[1]
                    c_score.append(i[2])
            return res, format_license(res.upper()), np.mean(c_score)
    else:
        return '', '', 0


def process_nameplate(image):
    greyed_plate = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # binary = cv2.equalizeHist(greyed_plate)    
    threshold = cv2.threshold(greyed_plate, 0, 255, cv2.ADAPTIVE_THRESH_MEAN_C+cv2.ADAPTIVE_THRESH_GAUSSIAN_C+ cv2.THRESH_OTSU)[1]
    # threshold = cv2.threshold(greyed_plate, np.mean(binary), 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.bitwise_not(threshold)
    contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    sorted_contours = sorted(contours, key = lambda x: min_area(x), reverse = True)
    new_contour = []
    sorted_contours = sorted_contours[:min(180, len(sorted_contours))]
    for i in sorted_contours:
        if min_area(i) > 0.002*image.shape[0]*image.shape[1]:
            new_contour.append(i)
    img1 = cv2.bitwise_and(thresh, 255-thresh)
    cv2.drawContours(img1, new_contour, -1, (255, 255, 0), 3)
    return thresh
    

def area(bbox):
    res = abs((bbox[0][0] - bbox[1][0])*(bbox[1][1] - bbox[2][1]))
    return np.abs(res)

def min_area(contour):
    a = cv2.minAreaRect(contour)
    return a[1][0]*a[1][1]



def get_text(image):
    # With OpenCV
    _, image_jpg = cv2.imencode('.jpg', image)
    files={'upload':image_jpg.tostring()}
    response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                files=files,
                headers={'Authorization': 'Token d67673a22ba9170e1ee739936f3e74b78d3735e5'})
    a = json.dumps(response.json(), indent=2)
    return a