import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import config
from tkinter import filedialog


# Initialise input variables
def init_GUI_variables():
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
    global uncertain_grayscale_threshold

    scale_factor = config.scale_factor.get()
    scale_bar_pixels_per_mm = config.scale_bar_pixels_per_mm.get()
    grayscale_threshold = config.grayscale_threshold.get()
    bottom_crop_ratio = config.bottom_crop_ratio.get()
    smaller_grain_area_min = config.smaller_grain_area_min.get()
    smaller_grain_area_max = config.smaller_grain_area_max.get()
    larger_grain_area_min = config.larger_grain_area_min.get()
    larger_grain_area_max = config.larger_grain_area_max.get()
    uncertain_grain_area_min = config.uncertain_grain_area_min.get()
    uncertain_grain_area_max = config.uncertain_grain_area_max.get()
    kernel_size = config.kernel_size.get()
    uncertain_grayscale_threshold = config.uncertain_grayscale_threshold.get()
    return


# Takes files from button selection in GUI and stores as variable image_path
def select_file():
    global image_path
    image_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                            filetypes=(("tiff files", "*.tiff"), ("all files", "*.*")))
    # Ensure file as been chosen;
    if not image_path:
        print("No file selected!")
        return


# Crops bottom of image to prevent contouring of words
# Modifies input resize factor if required
# Converts Image to grayscale
# Thresholds the grayscale image based on an input value
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

    # Apply a threshold to the grayscale image
    _, thresholded_image = cv2.threshold(gray_image, grayscale_threshold, 255, cv2.THRESH_BINARY)

    return thresholded_image, image


# Identifies contours based on the thresholded image
# For a specified large surface area range, uncertain grain contours are identified and stored
# A blur mask is applied to only these grains to minimise noise to help with grain separation
# Contours for the recombined image are recorded
def detect_contours(thresholded_image):

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find uncertain grain contours to apply blur before contour drawing of the whole image
    uncertain_grain_contours = [contour for contour in contours if uncertain_grain_area_min < cv2.contourArea(contour) < uncertain_grain_area_max]

    # Apply blur to uncertain grain areas
    blurred_image = apply_mask_and_blur(thresholded_image, uncertain_grain_contours)

    # Find contours in the new blurred_image
    contours, _ = cv2.findContours(blurred_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, blurred_image


# Initialises arrays and area values
# For each contour the area is recorded
# The contours a filtered based on their area value
# The average area for each area range is calculated
# The average area is converted to mm^2 based on the scale bar
# The contours are assigned a color based on the area range and are drawn on a copy of the image
def classify_and_calculate_contours(contours, image):

    # Initialise contours and contour areas
    uncertain_grain_contours = []
    larger_grain_contours = []
    smaller_grain_contours = []
    uncertain_grain_total_area = 0
    larger_grain_total_area = 0
    smaller_grain_total_area = 0

    # Filter contours based on size and shape
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
    cv2.drawContours(result_image, uncertain_grain_contours, -1, (0, 255, 0), 10)  # Red. Thickness 10
    cv2.drawContours(result_image, larger_grain_contours, -1, (0, 0, 255), 10)  # Red. Thickness 10
    cv2.drawContours(result_image, smaller_grain_contours, -1, (255, 0, 0), 10)  # Blue. Thickness 10

    # Return the number of chocolate chips, the outlined image, the thresholded image and the average area
    return result_image, smaller_grain_average_area_mm, larger_grain_average_area_mm, smaller_grain_contours, larger_grain_contours, uncertain_grain_contours


# Runs all the required functions to initialise and store values in required variables
# Checks that the image processing was successful and returned an image
# Prints the number of grains that fall into a given area range and prints the average area for those contours
def run_grain_counting():
    init_GUI_variables()
    thresholded_image, image = load_and_preprocessing()
    contours, blurred_image = detect_contours(thresholded_image)
    result_image, smaller_grain_average_area_mm, larger_grain_average_area_mm, smaller_grain_contours, larger_grain_contours, uncertain_grain_contours = classify_and_calculate_contours(contours, image)

    if blurred_image is not None and result_image is not None:

        print(f"-----------------------------------------------------------------------------------")
        print(f"VISIBLE GRAIN COUNT...")
        print(
            f"The number of smaller {smaller_grain_area_min} to {smaller_grain_area_max} pixel Al grains visible: "
            f"{len(smaller_grain_contours)}")
        print(
            f"The number of larger {larger_grain_area_min} to {larger_grain_area_max} pixel Al grains visible: "
            f"{len(larger_grain_contours)}")
        print(f"The total number of certain visible Al Grains: {len(smaller_grain_contours) + len(larger_grain_contours)}")
        print(
            f"The number of uncertain {uncertain_grain_area_min} to {uncertain_grain_area_max} pixel Al grains visible: "
            f"{len(uncertain_grain_contours)}")
        print(f"VISIBLE GRAIN AREA...")
        print(
            f"The average visible surface area of the smaller {smaller_grain_area_min} to {smaller_grain_area_max} "
            f"pixel Al grains: {smaller_grain_average_area_mm:.4f} mm^2")
        print(
            f"The average visible surface area of the larger {larger_grain_area_min} to {larger_grain_area_max} "
            f"pixel Al grains: {larger_grain_average_area_mm:.4f} mm^2")
        print(f"-----------------------------------------------------------------------------------")

        display_images(blurred_image, result_image)

    else:
        print("Error: Unable to process images.")
        sys.exit()


# Takes the grayscale and contoured image and displays the two plots
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


# Sets the input fields back to original settings
def reset_values():
    config.scale_factor.set(1.0)
    config.scale_bar_pixels_per_mm.set(255.9812)
    config.grayscale_threshold.set(190)
    config.bottom_crop_ratio.set(0.05)
    config.smaller_grain_area_min.set(9000)
    config.smaller_grain_area_max.set(50000)
    config.larger_grain_area_min.set(50000)
    config.larger_grain_area_max.set(100000)
    config.uncertain_grain_area_min.set(100000)
    config.uncertain_grain_area_max.set(400000)
    config.kernel_size.set(5)
    config.uncertain_grayscale_threshold.set(200)


# Takes the tresholded image and the uncertain contour values
# Creates an empty black mask over the uncertain contour region then fills in the mask with white
# Applies the mask over the uncertain grains in the image
# Applies a gaussian blur the masked region only
# Applies the watershed algorithm to the masked image
def apply_mask_and_blur(image, contours):
    # Create an empty mask to start with
    mask = np.zeros(image.shape[:2], dtype=np.uint8)  # Ensuring mask size and shape

    # Draw filled contours on mask
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)  # Mask requires single channel

    # Apply the mask to the image
    masked_image = cv2.bitwise_and(image, image, mask=mask)

    # # Apply the blur to the masked image
    blurred_image = cv2.GaussianBlur(masked_image, (kernel_size, kernel_size), 0)
    blurred_image_3chan = cv2.cvtColor(blurred_image, cv2.COLOR_GRAY2BGR)

    # Now we apply the watershed algorithm to the masked image
    # Distance transformation
    distance_transform = cv2.distanceTransform(blurred_image, cv2.DIST_L2, 5)
    _, sure_foreground = cv2.threshold(distance_transform, uncertain_grayscale_threshold * distance_transform.max(), 255, 0)
    sure_foreground = np.uint8(sure_foreground)

    # Create a kernel for dilation
    kernel = np.ones((1, 1), np.uint8)
    sure_background = cv2.dilate(blurred_image, kernel, iterations=1)
    uncertain_region = cv2.subtract(sure_background, sure_foreground)

    _, markers = cv2.connectedComponents(sure_foreground)
    markers = markers + 1
    markers[uncertain_region == 255] = 0
    markers = markers.astype(np.int32)

    # The watershed algorithm modifies the markers image
    cv2.watershed(blurred_image_3chan, markers)

    # Create a new binary image where the separated grains are white and everything else is black
    separated_grains_image = np.where(markers > 1, 255, 0).astype(np.uint8)

    # Combine the blurred part with the original image
    inv_mask = cv2.bitwise_not(mask)
    image_bg = cv2.bitwise_and(image, image, mask=inv_mask)
    combined_image = cv2.bitwise_or(image_bg, separated_grains_image)

    return combined_image








