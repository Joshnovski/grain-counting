import cv2
import sys
from grainCounting import count_grains
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

scale_factor = 1  # image scaling factor on a scale from 0 to 1. If lower than zero, lose resolution
scale_bar_pixels_per_mm = 255.9812  # number of pixels per mm found from scale bar with imagej
grayscale_threshold = 190  # Grayscale Threshold

# Grain area thresholds (in pixels)
area_min = 9000
area_max = 600000


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


if __name__ == "__main__":
    image_path = r"C:\Users\RA user\mgathermal.com\mgathermal.com - Research and Development\3000 " \
                 r"Characterisation\Collation Tool - Grain Counting\SI poly 1225-001-01.tiff"
    grain_count, outlined_image_cv, grayscale_image_cv, real_average_area = count_grains(image_path, scale_factor,
                                                                                         scale_bar_pixels_per_mm, grayscale_threshold, area_min, area_max)

    if grayscale_image_cv is not None and outlined_image_cv is not None:
        print(f"The number of Al grains visible: {grain_count}")
        print(f"The average surface area of visible Al grains: {real_average_area:.4f} mm^2")
        display_images(grayscale_image_cv, outlined_image_cv)

    else:
        print("Error: Unable to process images.")
        sys.exit()
