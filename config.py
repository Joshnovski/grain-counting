import tkinter as tk


def init_variables(root):
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
    global dilation_iterations

    scale_factor = tk.DoubleVar(value=1.0)
    scale_bar_pixels_per_mm = tk.DoubleVar(value=255.9812)
    grayscale_threshold = tk.IntVar(value=190)
    bottom_crop_ratio = tk.DoubleVar(value=0.05)

    kernel_size = tk.IntVar(value=1)
    distanceTransform_threshold = tk.IntVar(value=0.7)
    dilation_iterations = tk.IntVar(value=1)

    smaller_grain_area_min = tk.IntVar(value=9000)
    smaller_grain_area_max = tk.IntVar(value=50000)
    larger_grain_area_min = tk.IntVar(value=50000)
    larger_grain_area_max = tk.IntVar(value=100000)
    uncertain_grain_area_min = tk.IntVar(value=100000)
    uncertain_grain_area_max = tk.IntVar(value=400000)
