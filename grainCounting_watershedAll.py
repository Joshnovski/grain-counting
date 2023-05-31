import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import config_watershedAll
from tkinter import filedialog


def count_grains(image_path, scale_factor, scale_bar_pixels_per_mm, grayscale_threshold, smaller_grain_area_min,
                 smaller_grain_area_max, larger_grain_area_min, larger_grain_area_max, uncertain_grain_area_min,
                 uncertain_grain_area_max, bottom_crop_ratio, kernel_size, distanceTransform_threshold,
                 dilation_iterations):
    # Load the image
    image = cv2.imread(image_path)

    # error capture
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

    # Smooth out noise with slight blur to assist with thresholding
    gray_image_blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Apply a threshold to the grayscale image
    _, thresholded_image = cv2.threshold(gray_image_blurred, 0, 255, cv2.THRESH_OTSU)
    thresholded_image = cv2.morphologyEx(thresholded_image, cv2.MORPH_OPEN, np.ones((3, 3), dtype=int)) # Increasing seems to remove surrounding elements from being contoured. Was 3

    thresholded_image_3chan = cv2.cvtColor(thresholded_image, cv2.COLOR_GRAY2BGR)

    # Distance transformation
    dt = cv2.distanceTransform(thresholded_image, cv2.DIST_L2, 3)
    dt = ((dt - dt.min()) / (dt.max() - dt.min()) * 255).astype(np.uint8)
    _, dt = cv2.threshold(dt, 80, 255, cv2.THRESH_BINARY)

    border = cv2.dilate(thresholded_image, None, iterations=5)
    border = border - cv2.erode(border, None)

    dt = dt.astype(np.uint8)
    _, markers = cv2.connectedComponents(dt)

    # Completing the markers now.
    markers[border == 255] = 255
    markers = markers.astype(np.int32)

    # The watershed algorithm modifies the markers image
    cv2.watershed(thresholded_image_3chan,
                  markers)
    image[markers == -1] = [0, 0, 255]

    # Invert the result and convert to 8-bit image
    result = cv2.convertScaleAbs(255 - markers)

    # Create a binary image that marks the borders (where markers == -1) as black (0) and everything else as white (255)
    border_mask = np.where(markers == -1, 0, 255).astype(np.uint8)

    # Apply the mask to the result image
    result = cv2.bitwise_and(result, border_mask)

    # Create a new binary image where the separated grains are white and everything else is black
    separated_grains_image = np.where(markers > 1, 255, 0).astype(
        np.uint8)

    # Find contours in the new blurred_image
    contours, _ = cv2.findContours(separated_grains_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialise contours and contour areas
    uncertain_grain_contours = []
    larger_grain_contours = []
    smaller_grain_contours = []
    uncertain_grain_total_area = 0
    larger_grain_total_area = 0
    smaller_grain_total_area = 0

    # Filter contours based on size and shape - first pass
    for contour in contours:
        uncertain_grain_area = cv2.contourArea(contour)
        larger_grain_area = cv2.contourArea(contour)
        smaller_grain_area = cv2.contourArea(contour)

        # uncertain grain size range
        if uncertain_grain_area_min < uncertain_grain_area < uncertain_grain_area_max:
            uncertain_grain_contours.append(contour)
            uncertain_grain_total_area += uncertain_grain_area
        # higher grain size range
        if larger_grain_area_min < larger_grain_area < larger_grain_area_max:
            larger_grain_contours.append(contour)
            larger_grain_total_area += larger_grain_area
        # smaller grain size range
        if smaller_grain_area_min < smaller_grain_area < smaller_grain_area_max:
            smaller_grain_contours.append(contour)
            smaller_grain_total_area += smaller_grain_area

    # Calculate average area in pixels
    uncertain_grain_average_area_pixels = uncertain_grain_total_area / len(
        larger_grain_contours) if larger_grain_contours else 0
    larger_grain_average_area_pixels = larger_grain_total_area / len(
        larger_grain_contours) if larger_grain_contours else 0
    smaller_grain_average_area_pixels = smaller_grain_total_area / len(
        smaller_grain_contours) if smaller_grain_contours else 0

    # Convert average area in pixels to average area in square millimeters
    pixel_size_mm = 1 / scale_bar_pixels_per_mm
    uncertain_grain_average_area_mm = uncertain_grain_average_area_pixels * pixel_size_mm ** 2
    larger_grain_average_area_mm = larger_grain_average_area_pixels * pixel_size_mm ** 2
    smaller_grain_average_area_mm = smaller_grain_average_area_pixels * pixel_size_mm ** 2

    # Draw the grain contours on the image
    result_image = image.copy()
    cv2.drawContours(result_image, uncertain_grain_contours, -1, (0, 255, 0), 10)  # Red. Thickness 10
    cv2.drawContours(result_image, larger_grain_contours, -1, (0, 0, 255), 10)  # Red. Thickness 10
    cv2.drawContours(result_image, smaller_grain_contours, -1, (255, 0, 0), 10)  # Blue. Thickness 10

    # Return the number of chocolate chips, the outlined image, the thresholded image and the average area
    return len(larger_grain_contours), len(
        smaller_grain_contours), len(
        uncertain_grain_contours), result_image, result, uncertain_grain_average_area_mm, larger_grain_average_area_mm, smaller_grain_average_area_mm


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
    larger_grain_count, smaller_grain_count, uncertain_grain_count, outlined_image_cv, grayscale_image_cv, uncertain_real_average_area, larger_real_average_area, \
        smaller_real_average_area = count_grains(image_path, config_watershedAll.scale_factor.get(),
                                                 config_watershedAll.scale_bar_pixels_per_mm.get(),
                                                 config_watershedAll.grayscale_threshold.get(),
                                                 config_watershedAll.smaller_grain_area_min.get(),
                                                 config_watershedAll.smaller_grain_area_max.get(),
                                                 config_watershedAll.larger_grain_area_min.get(),
                                                 config_watershedAll.larger_grain_area_max.get(),
                                                 config_watershedAll.uncertain_grain_area_min.get(),
                                                 config_watershedAll.uncertain_grain_area_max.get(),
                                                 config_watershedAll.bottom_crop_ratio.get(),
                                                 config_watershedAll.kernel_size.get(),
                                                 config_watershedAll.distanceTransform_threshold.get(),
                                                 config_watershedAll.dilation_iterations.get())

    if grayscale_image_cv is not None and outlined_image_cv is not None:

        print(f"-----------------------------------------------------------------------------------")
        print(f"VISIBLE GRAIN COUNT...")
        print(
            f"The number of smaller {config_watershedAll.smaller_grain_area_min.get()} to {config_watershedAll.smaller_grain_area_max.get()} pixel Al grains visible: "
            f"{smaller_grain_count}")
        print(
            f"The number of larger {config_watershedAll.larger_grain_area_min.get()} to {config_watershedAll.larger_grain_area_max.get()} pixel Al grains visible: "
            f"{larger_grain_count}")
        print(f"The total number of certain visible Al Grains: {smaller_grain_count + larger_grain_count}")
        print(
            f"The number of uncertain {config_watershedAll.uncertain_grain_area_min.get()} to {config_watershedAll.uncertain_grain_area_max.get()} pixel Al grains visible: "
            f"{uncertain_grain_count}")
        print(f"VISIBLE GRAIN AREA...")
        print(
            f"The average visible surface area of the smaller {config_watershedAll.smaller_grain_area_min.get()} to {config_watershedAll.smaller_grain_area_max.get()} "
            f"pixel Al grains: {smaller_real_average_area:.4f} mm^2")
        print(
            f"The average visible surface area of the larger {config_watershedAll.larger_grain_area_min.get()} to {config_watershedAll.larger_grain_area_max.get()} "
            f"pixel Al grains: {larger_real_average_area:.4f} mm^2")
        print(
            f"The average visible surface area of the uncertain {config_watershedAll.uncertain_grain_area_min.get()} to {config_watershedAll.uncertain_grain_area_max.get()} "
            f"pixel Al grains: {uncertain_real_average_area:.4f} mm^2")
        print(f"-----------------------------------------------------------------------------------")

        display_images(grayscale_image_cv, outlined_image_cv)

    else:
        print("Error: Unable to process images.")
        sys.exit()


def select_file():
    global image_path
    image_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                            filetypes=(("tiff files", "*.tiff"), ("all files", "*.*")))
    # Ensure file as been chosen;
    if not image_path:
        print("No file selected!")
        return


def reset_values():
    config_watershedAll.scale_factor.set(1.0)
    config_watershedAll.scale_bar_pixels_per_mm.set(255.9812)
    config_watershedAll.grayscale_threshold.set(190)
    config_watershedAll.bottom_crop_ratio.set(0.05)
    config_watershedAll.smaller_grain_area_min.set(9000)
    config_watershedAll.smaller_grain_area_max.set(50000)
    config_watershedAll.larger_grain_area_min.set(50000)
    config_watershedAll.larger_grain_area_max.set(100000)
    config_watershedAll.uncertain_grain_area_min.set(100000)
    config_watershedAll.uncertain_grain_area_max.set(400000)
    config_watershedAll.kernel_size.set(3)
    config_watershedAll.distanceTransform_threshold.set(0.15)
    config_watershedAll.dilation_iterations.set(1)
