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
    global grayscale_threshold_lower
    global grayscale_threshold_upper
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
    global histogram_bins
    global show_hist
    global show_images

    equalize_hist = config_watershedAll.equalize_hist.get()
    scale_factor = config_watershedAll.scale_factor.get()
    scale_bar_pixels_per_mm = config_watershedAll.scale_bar_pixels_per_mm.get()
    grayscale_threshold_lower = config_watershedAll.grayscale_threshold_lower.get()
    grayscale_threshold_upper = config_watershedAll.grayscale_threshold_upper.get()
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
    histogram_bins = config_watershedAll.histogram_bins.get()
    show_hist = config_watershedAll.show_hist.get()
    show_images = config_watershedAll.show_images.get()
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
    # _, thresholded_image = cv2.threshold(gray_image_blurred, grayscale_threshold, 255, cv2.THRESH_BINARY)
    thresholded_image = cv2.inRange(gray_image_blurred, grayscale_threshold_lower, grayscale_threshold_upper)

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
    grain_areas = []
    grain_areas_filtered = []
    grain_diameters = []
    grain_diameters_filtered = []
    uncertain_grain_total_area = 0
    larger_grain_total_area = 0
    smaller_grain_total_area = 0
    pixel_size_mm = (1 / scale_bar_pixels_per_mm) ** 2

    # Filter contours based on size and shape - first pass
    for contour in contours:
        grain_area = cv2.contourArea(contour)
        if grain_area < uncertain_grain_area_min:
            grain_real_area = grain_area * pixel_size_mm
            grain_areas.append(grain_real_area)
            grain_diameters.append(math.sqrt(4 * float(grain_real_area) / math.pi) * 1000)  # units in um

        # histogram filtration based on selected grain range
        if smaller_grain_area_min <= grain_area < uncertain_grain_area_min:
            grain_real_area = grain_area * pixel_size_mm
            grain_areas_filtered.append(grain_real_area)
            grain_diameters_filtered.append(math.sqrt(4 * float(grain_real_area) / math.pi) * 1000)
        # Append values outside the range to -0.1 to ensure array lengths of overlay and background hists are equal
        else:
            # Set placeholder values outside the range of the distogram to ensure data length remains the same
            grain_areas_filtered.append(-0.1)
            grain_diameters_filtered.append(-0.1)

        # smaller grain size range
        if smaller_grain_area_min < grain_area < smaller_grain_area_max:
            smaller_grain_contours.append(contour)
            smaller_grain_total_area += grain_area
        # higher grain size range
        if larger_grain_area_min <= grain_area < larger_grain_area_max:
            larger_grain_contours.append(contour)
            larger_grain_total_area += grain_area
        # uncertain grain size range
        if uncertain_grain_area_min <= grain_area < uncertain_grain_area_max:
            uncertain_grain_contours.append(contour)
            uncertain_grain_total_area += grain_area

    # Calculate average area in pixels
    uncertain_grain_average_area_pixels = uncertain_grain_total_area / len(
        larger_grain_contours) if larger_grain_contours else 0
    larger_grain_average_area_pixels = larger_grain_total_area / len(
        larger_grain_contours) if larger_grain_contours else 0
    smaller_grain_average_area_pixels = smaller_grain_total_area / len(
        smaller_grain_contours) if smaller_grain_contours else 0

    # Convert average area in pixels to average area in square millimeters

    uncertain_grain_average_area_mm = uncertain_grain_average_area_pixels * pixel_size_mm
    larger_grain_average_area_mm = larger_grain_average_area_pixels * pixel_size_mm
    smaller_grain_average_area_mm = smaller_grain_average_area_pixels * pixel_size_mm

    # Return the number of chocolate chips, the outlined image, the thresholded image and the average area
    return larger_grain_contours, smaller_grain_contours, uncertain_grain_contours, uncertain_grain_average_area_mm, larger_grain_average_area_mm, smaller_grain_average_area_mm, pixel_size_mm, grain_areas, grain_diameters, grain_areas_filtered, grain_diameters_filtered


def grain_size_histogram(grain_areas, grain_diameters, grain_areas_filtered, grain_diameters_filtered):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # filtered_count = []
    # for grain in grain_areas_filtered:
    #     if grain > 0:
    #         filtered_count.append(grain)
    #
    # print(f"Grain_areas: {len(grain_areas)}")
    # print(f"Grain_areas_filtered: {len(filtered_count)}")

    # Calculate bin_width
    n = histogram_bins  # Number of bins
    bin_width_mm = (max(grain_areas) - min(grain_areas)) / n  # based on mm
    bin_width_um = (max(grain_diameters) - min(grain_diameters)) / n  # based on um

    # Plot the first histogram (Removed first 7 bins containing a very large peaks of noise grains)
    ax1.hist(grain_areas, bins=n, color='black', alpha=0.5, range=(0 + bin_width_mm, max(grain_areas)), edgecolor='white', label='All Grain Areas')
    ax1.hist(grain_areas_filtered, bins=n, color='orange', alpha=1, range=(0 + bin_width_mm, max(grain_areas)), edgecolor='white', label='Grain Areas Selected (Excluding Uncertain Grains)')
    ax1.set_xlabel('Grain Area (mm\u00b2)')
    ax1.set_ylabel('Count of Grains')

    # Plot the second histogram
    ax2.hist(grain_diameters, bins=n, color='black', alpha=0.5, range=(0 + 7 * bin_width_um, max(grain_diameters)), edgecolor='white', label='All Grain Diameters')
    ax2.hist(grain_diameters_filtered, bins=n, color='orange', alpha=1, range=(0 + 7 * bin_width_um, max(grain_diameters)), edgecolor='white', label='Grain Diameters Selected (Excluding Uncertain Grains)')
    ax2.set_xlabel('Grain Diameters (\u03BCm)')
    ax2.set_ylabel('Count of Grains')

    ax1.legend(loc="upper right")
    ax2.legend(loc="upper right")

    for grains in ax1.containers:
        ax1.bar_label(grains)
    for grains in ax2.containers:
        ax2.bar_label(grains)

    plt.tight_layout()  # Adjust spacing between subplots to minimize overlap
    plt.show(block=False)


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
    larger_grain_contours, smaller_grain_contours, uncertain_grain_contours, uncertain_grain_average_area_mm, larger_grain_average_area_mm, smaller_grain_average_area_mm, pixel_size_mm, grain_areas, grain_diameters, grain_areas_filtered, grain_diameters_filtered = calculate_area_and_filter_contours(result)

    if show_hist:
        grain_size_histogram(grain_areas, grain_diameters, grain_areas_filtered, grain_diameters_filtered)

    result_image = draw_contours(image, uncertain_grain_contours, larger_grain_contours, smaller_grain_contours)

    if result is not None and result_image is not None:

        print(f"-----------------------------------------------------------------------------------")
        print(f" ")
        print(f"IMAGE PATH: {image_path}")
        print(f" ")
        print(f"VISIBLE GRAIN COUNT...")
        print(
            f"The number of smaller {smaller_grain_area_min * pixel_size_mm:.3f} mm\u00b2 to {smaller_grain_area_max * pixel_size_mm:.3f} mm\u00b2 Al grains visible: "
            f"{len(smaller_grain_contours)}")
        print(
            f"The number of larger {larger_grain_area_min * pixel_size_mm:.3f} mm\u00b2 to {larger_grain_area_max * pixel_size_mm:.3f} mm\u00b2 Al grains visible: "
            f"{len(larger_grain_contours)}")
        print(
            f"The number of uncertain {uncertain_grain_area_min * pixel_size_mm:.3f} mm\u00b2 to {uncertain_grain_area_max * pixel_size_mm:.3f} mm\u00b2 Al grains visible: "
            f"{len(uncertain_grain_contours)}")
        print(f"The total number of visible Al Grains: {len(smaller_grain_contours) + len(larger_grain_contours) + len(uncertain_grain_contours)}")
        print(f" ")
        print(f"VISIBLE GRAIN AREA...")
        print(
            f"The average visible surface area of the smaller {smaller_grain_area_min * pixel_size_mm:.3f} mm\u00b2 to {smaller_grain_area_max * pixel_size_mm:.3f} mm\u00b2 "
            f"Al grains: {smaller_grain_average_area_mm:.3f} mm\u00b2")
        print(
            f"The average visible surface area of the larger {larger_grain_area_min * pixel_size_mm:.3f} mm\u00b2 to {larger_grain_area_max * pixel_size_mm:.3f} mm\u00b2 "
            f"Al grains: {larger_grain_average_area_mm:.3f} mm\u00b2")
        print(f" ")
        print(f"GRAIN COUNTING IMAGE PROCESSING PARAMETERS...")
        print(f'Scale Factor: {scale_factor}')
        print(f'Scale Bar Pixels Per mm: {scale_bar_pixels_per_mm}')
        print(f'Bottom Crop Ratio: {bottom_crop_ratio}')
        print(f'Equalize Histogram: {equalize_hist}')
        print(f'Lower Grayscale Threshold: {grayscale_threshold_lower}')
        print(f'Upper Grayscale Threshold: {grayscale_threshold_upper}')
        print(f'Kernel Size: {kernel_size}')
        print(f'Distance Threshold: {distanceTransform_threshold}')
        print(f'Grain Morphology Simplicity: {grain_morphology}')
        print(f'Smaller Grain Area Min: {smaller_grain_area_min * pixel_size_mm} mm\u00b2')
        print(f'Smaller Grain Area Max: {smaller_grain_area_max * pixel_size_mm} mm\u00b2')
        print(f'Larger Grain Area Min: {larger_grain_area_min * pixel_size_mm} mm\u00b2')
        print(f'Larger Grain Area Max: {larger_grain_area_max * pixel_size_mm} mm\u00b2')
        print(f'Uncertain Grain Area Min: {uncertain_grain_area_min * pixel_size_mm} mm\u00b2')
        print(f'Uncertain Grain Area Max: {uncertain_grain_area_max * pixel_size_mm} mm\u00b2')
        print(f" ")
        print(f"-----------------------------------------------------------------------------------")

        if show_images:
            display_images(result, result_image)

    else:
        print("Error: Unable to process images.")
        sys.exit()


def reset_values():
    config_watershedAll.scale_factor.set(1.0)
    config_watershedAll.scale_bar_pixels_per_mm.set(255.9812)
    config_watershedAll.grayscale_threshold_lower.set(170)
    config_watershedAll.grayscale_threshold_upper.set(255)
    config_watershedAll.bottom_crop_ratio.set(0.05)

    config_watershedAll.smaller_grain_area_min.set(0.283)
    config_watershedAll.smaller_grain_diameter_min.set(0.600)

    config_watershedAll.smaller_grain_area_max.set(0.763)
    config_watershedAll.smaller_grain_diameter_max.set(0.986)

    config_watershedAll.larger_grain_area_min.set(0.763)
    config_watershedAll.larger_grain_diameter_min.set(0.986)

    config_watershedAll.larger_grain_area_max.set(1.373)
    config_watershedAll.larger_grain_diameter_max.set(1.322)

    config_watershedAll.uncertain_grain_area_min.set(1.373)
    config_watershedAll.uncertain_grain_diameter_min.set(1.322)

    config_watershedAll.uncertain_grain_area_max.set(6.104)
    config_watershedAll.uncertain_grain_diameter_max.set(2.788)

    config_watershedAll.kernel_size.set(3)
    config_watershedAll.distanceTransform_threshold.set(7)
    config_watershedAll.grain_morphology.set(3)
    config_watershedAll.histogram_bins.set(20)
