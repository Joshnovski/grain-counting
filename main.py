import cv2
from grainCounting import count_chocolate_chips

image_path = r"C:\Users\RA user\mgathermal.com\mgathermal.com - Research and Development\3000 " \
             r"Characterisation\Collation Tool - Grain Counting\1225-001-01_SEM.png"
chocolate_chip_count, outlined_image, grayscale_image = count_chocolate_chips(image_path)

print(f"The number of Al grains visible: {chocolate_chip_count}")

cv2.imshow("Grayscale Image", grayscale_image)
cv2.imshow("Outlined Chocolate Chips", outlined_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
