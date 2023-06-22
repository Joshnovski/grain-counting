import tkinter as tk
import math


def area_to_diameter(area):
    return math.sqrt(4*float(area)/math.pi)


def diameter_to_area(diameter):
    return math.pi * (float(diameter)/2)**2


def init_variables(root):
    global equalize_hist
    global scale_factor
    global scale_bar_pixels_per_mm
    global grayscale_threshold
    global bottom_crop_ratio

    global smaller_grain_area_min
    global smaller_grain_diameter_min
    global smaller_grain_area_max
    global smaller_grain_diameter_max

    global larger_grain_area_min
    global larger_grain_diameter_min
    global larger_grain_area_max
    global larger_grain_diameter_max

    global uncertain_grain_area_min
    global uncertain_grain_diameter_min
    global uncertain_grain_area_max
    global uncertain_grain_diameter_max

    global kernel_size
    global distanceTransform_threshold
    global grain_morphology

    scale_factor = tk.DoubleVar(value=1.0)
    scale_bar_pixels_per_mm = tk.DoubleVar(value=255.9812)
    grayscale_threshold = tk.IntVar(value=170)
    bottom_crop_ratio = tk.DoubleVar(value=0.05)

    kernel_size = tk.IntVar(value=15)
    distanceTransform_threshold = tk.IntVar(value=70)
    grain_morphology = tk.IntVar(value=3)

    smaller_grain_area_min = tk.DoubleVar(value=0.153)
    smaller_grain_area_max = tk.DoubleVar(value=0.763)
    larger_grain_area_min = tk.DoubleVar(value=0.763)
    larger_grain_area_max = tk.DoubleVar(value=1.373)
    uncertain_grain_area_min = tk.DoubleVar(value=1.373)
    uncertain_grain_area_max = tk.DoubleVar(value=6.104)

    smaller_grain_diameter_min = tk.DoubleVar(value=0.441)
    smaller_grain_diameter_max = tk.DoubleVar(value=0.986)
    larger_grain_diameter_min = tk.DoubleVar(value=0.986)
    larger_grain_diameter_max = tk.DoubleVar(value=1.322)
    uncertain_grain_diameter_min = tk.DoubleVar(value=1.322)
    uncertain_grain_diameter_max = tk.DoubleVar(value=2.788)

    equalize_hist = tk.BooleanVar(value=False)

