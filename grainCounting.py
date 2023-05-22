import tkinter as tk
import cv2
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import config


def count_grains(image_path, scale_factor, scale_bar_pixels_per_mm, grayscale_threshold, smaller_grain_area_min,
                 smaller_grain_area_max, larger_grain_area_min, larger_grain_area_max, bottom_crop_ratio):
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to load image from {image_path}")
        sys.exit()

    # Crop the bottom part of the image based on bottom_crop_ratio
    height, width, _ = image.shape
    image = image[:int(height * (1 - bottom_crop_ratio)), :]

    # Resize the image if scale_factor is not 1
    if scale_factor != 1:
        image = cv2.resize(image, (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor)))

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to the grayscale image
    _, thresholded_image = cv2.threshold(gray_image, grayscale_threshold, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on size and shape
    larger_grain_contours = []
    smaller_grain_contours = []
    larger_grain_total_area = 0
    smaller_grain_total_area = 0

    for contour in contours:
        larger_grain_area = cv2.contourArea(contour)
        smaller_grain_area = cv2.contourArea(contour)

        # higher grain size range
        if larger_grain_area_min < larger_grain_area < larger_grain_area_max:
            larger_grain_contours.append(contour)
            larger_grain_total_area += larger_grain_area
        # smaller grain size range
        if smaller_grain_area_min < smaller_grain_area < smaller_grain_area_max:
            smaller_grain_contours.append(contour)
            smaller_grain_total_area += smaller_grain_area

    # Calculate average area in pixels
    larger_grain_average_area_pixels = larger_grain_total_area / len(
        larger_grain_contours) if larger_grain_contours else 0
    smaller_grain_average_area_pixels = smaller_grain_total_area / len(
        smaller_grain_contours) if smaller_grain_contours else 0

    # Convert average area in pixels to average area in square millimeters
    pixel_size_mm = 1 / scale_bar_pixels_per_mm
    larger_grain_average_area_mm = larger_grain_average_area_pixels * pixel_size_mm ** 2
    smaller_grain_average_area_mm = smaller_grain_average_area_pixels * pixel_size_mm ** 2

    # Draw the grain contours on the image
    result_image = image.copy()
    cv2.drawContours(result_image, larger_grain_contours, -1, (0, 0, 255), 10)  # Red
    cv2.drawContours(result_image, smaller_grain_contours, -1, (255, 0, 0), 10)  # Blue

    # Return the number of chocolate chips, the outlined image, the thresholded image and the average area
    return len(larger_grain_contours), len(
        smaller_grain_contours), result_image, thresholded_image, larger_grain_average_area_mm, smaller_grain_average_area_mm


def display_images(grayscale_image_cv, outlined_image_cv):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    ax1.imshow(grayscale_image_cv, cmap='gray')
    ax1.set_title('Grayscale Image')
    ax1.axis('off')
    Cursor(ax1, useblit=True, color='red', linewidth=1)

    ax2.imshow(cv2.cvtColor(outlined_image_cv, cv2.COLOR_BGR2RGB))
    ax2.set_title('Outlined Image')
    ax2.axis('off')
    Cursor(ax2, useblit=True, color='red', linewidth=1)

    plt.tight_layout()
    plt.show()


def run_grain_counting():
    image_path = r"C:\Users\RA user\mgathermal.com\mgathermal.com - Research and Development\3000 " \
                 r"Characterisation\Collation Tool - Grain Counting\SI poly 1225-001-01.tiff"

    larger_grain_count, smaller_grain_count, outlined_image_cv, grayscale_image_cv, larger_real_average_area, \
        smaller_real_average_area = count_grains(image_path, config.scale_factor.get(),
                                                 config.scale_bar_pixels_per_mm.get(),
                                                 config.grayscale_threshold.get(),
                                                 config.smaller_grain_area_min.get(),
                                                 config.smaller_grain_area_max.get(),
                                                 config.larger_grain_area_min.get(),
                                                 config.larger_grain_area_max.get(), config.bottom_crop_ratio.get())

    if grayscale_image_cv is not None and outlined_image_cv is not None:

        print(f"-----------------------------------------------------------------------------------")
        print(f"VISIBLE GRAIN COUNT...")
        print(
            f"The number of smaller {config.smaller_grain_area_min.get()} to {config.smaller_grain_area_max.get()} pixel Al grains visible: "
            f"{smaller_grain_count}")
        print(
            f"The number of larger {config.larger_grain_area_min.get()} to {config.larger_grain_area_max.get()} pixel Al grains visible: "
            f"{larger_grain_count}")
        print(f"VISIBLE GRAIN AREA...")
        print(
            f"The average visible surface area of the smaller {config.smaller_grain_area_min.get()} to {config.smaller_grain_area_max.get()} "
            f"pixel Al grains: {smaller_real_average_area:.4f} mm^2")
        print(
            f"The average visible surface area of the larger {config.larger_grain_area_min.get()} to {config.larger_grain_area_max.get()} "
            f"pixel Al grains: {larger_real_average_area:.4f} mm^2")
        print(f"-----------------------------------------------------------------------------------")

        display_images(grayscale_image_cv, outlined_image_cv)

    else:
        print("Error: Unable to process images.")
        sys.exit()


def reset_values():
    config.scale_factor.set(1.0)
    config.scale_bar_pixels_per_mm.set(255.9812)
    config.grayscale_threshold.set(190)
    config.bottom_crop_ratio.set(0.05)
    config.smaller_grain_area_min.set(9000)
    config.smaller_grain_area_max.set(50000)
    config.larger_grain_area_min.set(50000)
    config.larger_grain_area_max.set(600000)
