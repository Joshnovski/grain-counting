import sys

import cv2
import sys
import numpy as np

def count_chocolate_chips(image_path, scale_factor, scale_bar_pixels_per_mm):
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
    _, thresholded_image = cv2.threshold(gray_image, 190, 255, cv2.THRESH_BINARY) # 170, 255

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on size and shape
    chocolate_chip_contours = []
    total_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if 9000 < area < 600000: # Widen range here to allow for larger particle sizes
            chocolate_chip_contours.append(contour)
            total_area += area

    # Calculate average area in pixels
    average_area_pixels = total_area / len(chocolate_chip_contours) if chocolate_chip_contours else 0

    # Convert average area in pixels to average area in square millimeters
    pixel_size_mm = 1 / scale_bar_pixels_per_mm
    average_area_mm = average_area_pixels * pixel_size_mm ** 2

    # Draw the grain contours on the image
    result_image = image.copy()
    cv2.drawContours(result_image, chocolate_chip_contours, -1, (0, 255, 0), 2)

    # Return the number of chocolate chips, the outlined image, the thresholded image and the average area
    return len(chocolate_chip_contours), result_image, thresholded_image, average_area_mm
