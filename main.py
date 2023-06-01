import tkinter as tk
import config_watershedAll
import grainCounting_watershedAll

root = tk.Tk()
root.title("Grain Counting Parameters")

config_watershedAll.init_variables(root)  # Initialize the tkinter variables

# Add all the entries for the parameters
tk.Label(root, text="Scale Factor: ").grid(row=0, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.scale_factor).grid(row=0, column=2)

tk.Label(root, text="Scale Bar Pixels per mm:").grid(row=1, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.scale_bar_pixels_per_mm).grid(row=1, column=2)

tk.Label(root, text="Bottom Crop Ratio:").grid(row=2, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.bottom_crop_ratio).grid(row=2, column=2)

tk.Label(root, text="------------------------").grid(row=3, column=0, sticky='E')

tk.Label(root, text="Pre-Process Contrast Threshold:").grid(row=4, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.grayscale_threshold).grid(row=4, column=2)

tk.Label(root, text="Blur Kernel Size (Odd Values Only):").grid(row=5, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.kernel_size).grid(row=5, column=2)

tk.Label(root, text="Distance Transform Contrast Threshold:").grid(row=6, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.distanceTransform_threshold).grid(row=6, column=2)

tk.Label(root, text="Grain Edge Morphology Simplicity:").grid(row=7, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.grain_morphology).grid(row=7, column=2)

tk.Label(root, text="------------------------").grid(row=8, column=0, sticky='E')

tk.Label(root, text="Smaller Grain Area Min (Pixels):").grid(row=9, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.smaller_grain_area_min).grid(row=9, column=2)

tk.Label(root, text="Smaller Grain Area Max (Pixels):").grid(row=10, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.smaller_grain_area_max).grid(row=10, column=2)

tk.Label(root, text="Larger Grain Area Min (Pixels):").grid(row=11, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.larger_grain_area_min).grid(row=11, column=2)

tk.Label(root, text="Larger Grain Area Max (Pixels):").grid(row=12, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.larger_grain_area_max).grid(row=12, column=2)

tk.Label(root, text="Uncertain Grain Area Min (Pixels):").grid(row=13, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.uncertain_grain_area_min).grid(row=13, column=2)

tk.Label(root, text="Uncertain Grain Area Max (Pixels):").grid(row=14, column=0, sticky='E')
tk.Entry(root, textvariable=config_watershedAll.uncertain_grain_area_max).grid(row=14, column=2)

root.grid_columnconfigure(0, weight=1, minsize=20)  # Add padding on left side
root.grid_columnconfigure(3, weight=1, minsize=10)  # Add padding on right side

# Add a button to re-run the grain counting
tk.Button(root, text="Run Grain Counting", command=grainCounting_watershedAll.run_grain_counting).grid(row=15, column=0, pady=10)

# Add a button to reset the parameters to their default values
tk.Button(root, text="Reset Values", command=grainCounting_watershedAll.reset_values).grid(row=15, column=2, pady=10)

# Add a button to select a file
tk.Button(root, text="Select File", command=grainCounting_watershedAll.select_file).grid(row=15, column=1, pady=10, padx=10)


root.mainloop()
