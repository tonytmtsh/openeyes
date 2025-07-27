import cv2
import os

try:
    print('starting the folders listing')
    haar_path = cv2.data.haarcascades
    print("OpenCV haarcascades directory:", haar_path)
    # List all Haarcascade XML files in this directory
    if os.path.exists(haar_path):
        print("Files in haarcascades directory:")
        for fname in os.listdir(haar_path):
            if fname.endswith(".xml"):
                print(fname)
    else:
        print("The haarcascades directory does not exist.")
except AttributeError:
    print("cv2.data.haarcascades not available in this OpenCV installation.")
    print("You may need to manually specify the path to the XML files.")