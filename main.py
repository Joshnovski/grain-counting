# import cv2
# from grainCounting import count_chocolate_chips
#
# image_path = r"C:\Users\RA user\mgathermal.com\mgathermal.com - Research and Development\3000 Characterisation\Collation Tool - Grain Counting\SI poly 1225-001-01.tiff"
# scale_factor = 0.1  # Adjust this value to fit the image to your screen
# chocolate_chip_count, outlined_image, grayscale_image = count_chocolate_chips(image_path, scale_factor)
#
# print(f"The number of Al grains visible: {chocolate_chip_count}")
#
# cv2.imshow("Grayscale Image", grayscale_image)
# cv2.imshow("Outlined Grains", outlined_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

#############################################################################################


import cv2
import sys
from grainCounting import count_chocolate_chips
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor


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
    image_path = r"C:\Users\RA user\mgathermal.com\mgathermal.com - Research and Development\3000 Characterisation\Collation Tool - Grain Counting\SI poly 1225-001-01.tiff"
    scale_factor = 1
    chocolate_chip_count, outlined_image_cv, grayscale_image_cv = count_chocolate_chips(image_path, scale_factor)

    if grayscale_image_cv is not None and outlined_image_cv is not None:
        print(f"The number of Al grains visible: {chocolate_chip_count}")
        display_images(grayscale_image_cv, outlined_image_cv)
    else:
        print("Error: Unable to process images.")
        sys.exit()



