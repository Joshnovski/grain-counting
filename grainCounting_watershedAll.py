import cv2
import sys
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import config_watershedAll
from tkinter import filedialog


def init_GUI_variables():
    global equalize_hist
    global scale_factor
    global scale_bar_pixels_per_mm
    global grayscale_threshold
    global bottom_crop_ratio
    global smaller_grain_area_min
    global smaller_grain_area_max
    global larger_grain_area_min
    global larger_grain_area_max
    global uncertain_grain_area_min
    global uncertain_grain_area_max
    global kernel_size
    global distanceTransform_threshold
    global grain_morphology
    global pixel_size_mm

    equalize_hist = config_watershedAll.equalize_hist.get()
    scale_factor = config_watershedAll.scale_factor.get()
    scale_bar_pixels_per_mm = config_watershedAll.scale_bar_pixels_per_mm.get()
    grayscale_threshold = config_watershedAll.grayscale_threshold.get()
    bottom_crop_ratio = config_watershedAll.bottom_crop_ratio.get()
    pixel_size_mm = (1 / scale_bar_pixels_per_mm) ** 2
    smaller_grain_area_min = (config_watershedAll.smaller_grain_area_min.get()) / pixel_size_mm
    smaller_grain_area_max = (config_watershedAll.smaller_grain_area_max.get()) / pixel_size_mm
    larger_grain_area_min = (config_watershedAll.larger_grain_area_min.get()) / pixel_size_mm
    larger_grain_area_max = (config_watershedAll.larger_grain_area_max.get()) / pixel_size_mm
    uncertain_grain_area_min = (config_watershedAll.uncertain_grain_area_min.get()) / pixel_size_mm
    uncertain_grain_area_max = (config_watershedAll.uncertain_grain_area_max.get()) / pixel_size_mm
    kernel_size = config_watershedAll.kernel_size.get()
    distanceTransform_threshold = config_watershedAll.distanceTransform_threshold.get()
    grain_morphology = config_watershedAll.grain_morphology.get()
    return


def select_file():
    global image_path
    image_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                            filetypes=(("tiff files", "*.tiff"), ("all files", "*.*")))
    # Ensure file as been chosen;
    if not image_path:
        print("No file selected!")
        return


def load_and_preprocessing():
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

    # Equalize the histogram of the grayscale image
    if equalize_hist:
        gray_image = cv2.equalizeHist(gray_image)

    # Smooth out noise with slight blur to assist with thresholding
    gray_image_blurred = cv2.GaussianBlur(gray_image, (kernel_size, kernel_size), 0)

    # Apply a threshold to the grayscale image
    _, thresholded_image = cv2.threshold(gray_image_blurred, grayscale_threshold, 255, cv2.THRESH_BINARY)
    thresholded_image = cv2.morphologyEx(thresholded_image, cv2.MORPH_OPEN, np.ones((grain_morphology, grain_morphology), dtype=int))

    thresholded_image_3chan = cv2.cvtColor(thresholded_image, cv2.COLOR_GRAY2BGR)

    # Distance transformation
    dt = cv2.distanceTransform(thresholded_image, cv2.DIST_L2, 3)
    dt = ((dt - dt.min()) / (dt.max() - dt.min()) * 255).astype(np.uint8)
    _, dt = cv2.threshold(dt, distanceTransform_threshold, 255, cv2.THRESH_BINARY)

    border = cv2.dilate(thresholded_image, None, iterations=5)
    border = border - cv2.erode(border, None)

    dt = dt.astype(np.uint8)
    _, markers = cv2.connectedComponents(dt)

    # Completing the markers now.
    markers[border == 255] = 255
    markers = markers.astype(np.int32)

    return thresholded_image_3chan, markers, image


def watershed_and_postprocessing(thresholded_image_3chan, markers):
    # The watershed algorithm modifies the markers image
    cv2.watershed(thresholded_image_3chan, markers)
    # image[markers == -1] = [0, 0, 255]

    # Create a binary image that marks the borders (where markers == -1)
    border_mask = np.where(markers == -1, 255, 0).astype(np.uint8)

    # Border Thickness
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated_border_mask = cv2.dilate(border_mask, kernel, iterations=2)

    # Create a grayscale image where the separated grains have their marker values
    # (with the labels gradient) and everything else is white
    separated_grains_image = np.where(markers > 1, markers, 255).astype(np.uint8)

    # Normalize the separated_grains_image to have a full range of grayscale values
    separated_grains_image = cv2.normalize(separated_grains_image, None, 0, 255, cv2.NORM_MINMAX)

    # Apply the mask to the result image
    result = np.where(dilated_border_mask == 255, dilated_border_mask, separated_grains_image)
    result = 255 - result

    return result


def calculate_area_and_filter_contours(result):

    # Find contours in the new blurred_image
    contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

    pixel_size_mm = (1 / scale_bar_pixels_per_mm)**2
    uncertain_grain_average_area_mm = uncertain_grain_average_area_pixels * pixel_size_mm
    larger_grain_average_area_mm = larger_grain_average_area_pixels * pixel_size_mm
    smaller_grain_average_area_mm = smaller_grain_average_area_pixels * pixel_size_mm

    # Return the number of chocolate chips, the outlined image, the thresholded image and the average area
    return larger_grain_contours, smaller_grain_contours, uncertain_grain_contours, uncertain_grain_average_area_mm, larger_grain_average_area_mm, smaller_grain_average_area_mm, pixel_size_mm


def draw_contours(image, uncertain_grain_contours, larger_grain_contours, smaller_grain_contours):
    # Draw the grain contours on the image
    result_image = image.copy()
    cv2.drawContours(result_image, uncertain_grain_contours, -1, (0, 255, 0), 10)  # Red. Thickness 10
    cv2.drawContours(result_image, larger_grain_contours, -1, (0, 0, 255), 10)  # Red. Thickness 10
    cv2.drawContours(result_image, smaller_grain_contours, -1, (255, 0, 0), 10)  # Blue. Thickness 10
    return result_image


def display_images(grayscale_image_cv, outlined_image_cv):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharex='all', sharey='all')

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
    init_GUI_variables()
    thresholded_image_3chan, markers, image = load_and_preprocessing()
    result = watershed_and_postprocessing(thresholded_image_3chan, markers)
    larger_grain_contours, smaller_grain_contours, uncertain_grain_contours, uncertain_grain_average_area_mm, larger_grain_average_area_mm, smaller_grain_average_area_mm, pixel_size_mm = calculate_area_and_filter_contours(result)
    result_image = draw_contours(image, uncertain_grain_contours, larger_grain_contours, smaller_grain_contours)

    if result is not None and result_image is not None:

        print(f"-----------------------------------------------------------------------------------")
        print(f" ")
        print(f"IMAGE PATH: {image_path}")
        print(f" ")
        print(f"VISIBLE GRAIN COUNT...")
        print(
            f"The number of smaller {smaller_grain_area_min * pixel_size_mm:.3f} mm^2 to {smaller_grain_area_max * pixel_size_mm:.3f} mm^2 Al grains visible: "
            f"{len(smaller_grain_contours)}")
        print(
            f"The number of larger {larger_grain_area_min * pixel_size_mm:.3f} mm^2 to {larger_grain_area_max * pixel_size_mm:.3f} mm^2 Al grains visible: "
            f"{len(larger_grain_contours)}")
        print(
            f"The number of uncertain {uncertain_grain_area_min * pixel_size_mm:.3f} mm^2 to {uncertain_grain_area_max * pixel_size_mm:.3f} mm^2 Al grains visible: "
            f"{len(uncertain_grain_contours)}")
        print(f"The total number of visible Al Grains: {len(smaller_grain_contours) + len(larger_grain_contours) + len(uncertain_grain_contours)}")
        print(f" ")
        print(f"VISIBLE GRAIN AREA...")
        print(
            f"The average visible surface area of the smaller {smaller_grain_area_min * pixel_size_mm:.3f} mm^2 to {smaller_grain_area_max * pixel_size_mm:.3f} mm^2 "
            f"Al grains: {smaller_grain_average_area_mm:.3f} mm^2")
        print(
            f"The average visible surface area of the larger {larger_grain_area_min * pixel_size_mm:.3f} mm^2 to {larger_grain_area_max * pixel_size_mm:.3f} mm^2 "
            f"Al grains: {larger_grain_average_area_mm:.3f} mm^2")
        print(f" ")
        print(f"GRAIN COUNTING IMAGE PROCESSING PARAMETERS...")
        print(f'Scale Factor: {scale_factor}')
        print(f'Scale Bar Pixels Per mm: {scale_bar_pixels_per_mm}')
        print(f'Bottom Crop Ratio: {bottom_crop_ratio}')
        print(f'Equalize Histogram: {equalize_hist}')
        print(f'Grayscale Threshold: {grayscale_threshold}')
        print(f'Kernel Size: {kernel_size}')
        print(f'Distance Threshold: {distanceTransform_threshold}')
        print(f'Grain Morphology Simplicity: {grain_morphology}')
        print(f'Smaller Grain Area Min: {smaller_grain_area_min * pixel_size_mm} mm^2. Equivalent to a {math.sqrt(4*(smaller_grain_area_min*pixel_size_mm)/math.pi):.3f} mm diameter circle')
        print(f'Smaller Grain Area Max: {smaller_grain_area_max * pixel_size_mm} mm^2. Equivalent to a {math.sqrt(4*(smaller_grain_area_max*pixel_size_mm)/math.pi):.3f} mm diameter circle')
        print(f'Larger Grain Area Min: {larger_grain_area_min * pixel_size_mm} mm^2. Equivalent to a {math.sqrt(4*(larger_grain_area_min*pixel_size_mm)/math.pi):.3f} mm diameter circle')
        print(f'Larger Grain Area Max: {larger_grain_area_max * pixel_size_mm} mm^2. Equivalent to a {math.sqrt(4*(larger_grain_area_max*pixel_size_mm)/math.pi):.3f} mm diameter circle')
        print(f'Uncertain Grain Area Min: {uncertain_grain_area_min * pixel_size_mm} mm^2. Equivalent to a {math.sqrt(4*(uncertain_grain_area_min*pixel_size_mm)/math.pi):.3f} mm diameter circle')
        print(f'Uncertain Grain Area Max: {uncertain_grain_area_max * pixel_size_mm} mm^2. Equivalent to a {math.sqrt(4*(uncertain_grain_area_max*pixel_size_mm)/math.pi):.3f} mm diameter circle')
        print(f" ")
        print(f"-----------------------------------------------------------------------------------")

        display_images(result, result_image)

    else:
        print("Error: Unable to process images.")
        sys.exit()


def reset_values():
    config_watershedAll.scale_factor.set(1.0)
    config_watershedAll.scale_bar_pixels_per_mm.set(255.9812)
    config_watershedAll.grayscale_threshold.set(170)
    config_watershedAll.bottom_crop_ratio.set(0.05)
    config_watershedAll.smaller_grain_area_min.set(10000)
    config_watershedAll.smaller_grain_area_max.set(50000)
    config_watershedAll.larger_grain_area_min.set(50000)
    config_watershedAll.larger_grain_area_max.set(90000)
    config_watershedAll.uncertain_grain_area_min.set(90000)
    config_watershedAll.uncertain_grain_area_max.set(400000)
    config_watershedAll.kernel_size.set(15)
    config_watershedAll.distanceTransform_threshold.set(70)
    config_watershedAll.grain_morphology.set(3)
