import tkinter as tk
import config
import grainCounting

root = tk.Tk()
root.title("Grain Counting Parameters")

config.init_variables(root)  # Initialize the tkinter variables

# Add all the entries for the parameters
tk.Label(root, text="Scale Factor: ").grid(row=0, column=0, sticky='E')
tk.Entry(root, textvariable=config.scale_factor).grid(row=0, column=2)

tk.Label(root, text="Scale Bar Pixels per mm:").grid(row=1, column=0, sticky='E')
tk.Entry(root, textvariable=config.scale_bar_pixels_per_mm).grid(row=1, column=2)

tk.Label(root, text="Grayscale Threshold:").grid(row=2, column=0, sticky='E')
tk.Entry(root, textvariable=config.grayscale_threshold).grid(row=2, column=2)

tk.Label(root, text="Bottom Crop Ratio:").grid(row=3, column=0, sticky='E')
tk.Entry(root, textvariable=config.bottom_crop_ratio).grid(row=3, column=2)

tk.Label(root, text="------------------------").grid(row=4, column=0, sticky='E')

tk.Label(root, text="Smaller Grain Area Min:").grid(row=5, column=0, sticky='E')
tk.Entry(root, textvariable=config.smaller_grain_area_min).grid(row=5, column=2)

tk.Label(root, text="Smaller Grain Area Max:").grid(row=6, column=0, sticky='E')
tk.Entry(root, textvariable=config.smaller_grain_area_max).grid(row=6, column=2)

tk.Label(root, text="Larger Grain Area Min:").grid(row=7, column=0, sticky='E')
tk.Entry(root, textvariable=config.larger_grain_area_min).grid(row=7, column=2)

tk.Label(root, text="Larger Grain Area Max:").grid(row=8, column=0, sticky='E')
tk.Entry(root, textvariable=config.larger_grain_area_max).grid(row=8, column=2)

tk.Label(root, text="Uncertain Grain Area Min:").grid(row=9, column=0, sticky='E')
tk.Entry(root, textvariable=config.uncertain_grain_area_min).grid(row=9, column=2)

tk.Label(root, text="Uncertain Grain Area Max:").grid(row=10, column=0, sticky='E')
tk.Entry(root, textvariable=config.uncertain_grain_area_max).grid(row=10, column=2)

root.grid_columnconfigure(0, weight=1, minsize=20)  # Add padding on left side
root.grid_columnconfigure(3, weight=1, minsize=10)  # Add padding on right side

# Add a button to re-run the grain counting
tk.Button(root, text="Run Grain Counting", command=grainCounting.run_grain_counting).grid(row=11, column=0, pady=10)

# Add a button to reset the parameters to their default values
tk.Button(root, text="Reset Values", command=grainCounting.reset_values).grid(row=11, column=2, pady=10)

# Add a button to select a file
tk.Button(root, text="Select File", command=grainCounting.select_file).grid(row=11, column=1, pady=10, padx=10)


root.mainloop()
