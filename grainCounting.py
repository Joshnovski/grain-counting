import sys

import cv2
import sys
import numpy as np

def count_chocolate_chips(image_path, scale_factor):
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to load image from {image_path}")
        sys.exit()

    # Resize the image if scale_factor is not 1
    if scale_factor != 1:
        image = cv2.resize(image, (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor)))

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to the grayscale image
    _, thresholded_image = cv2.threshold(gray_image, 190, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on size and shape
    chocolate_chip_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 6000 < area < 60000: # Widen range here to allow for larger particle sizes
            chocolate_chip_contours.append(contour)

    # Draw the chocolate chip contours on the image
    result_image = image.copy()
    cv2.drawContours(result_image, chocolate_chip_contours, -1, (0, 255, 0), 2)

    # Return the number of chocolate chips, the outlined image, and the thresholded image
    return len(chocolate_chip_contours), result_image, thresholded_image
