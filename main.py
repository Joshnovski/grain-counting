import tkinter as tk
import config
import grainCounting

root = tk.Tk()
root.title("Grain Counting Parameters")

config.init_variables(root)  # Initialize the tkinter variables

# Add all the entries for the parameters
tk.Label(root, text="Scale Factor").grid(row=0, column=0)
tk.Entry(root, textvariable=config.scale_factor).grid(row=0, column=1)

tk.Label(root, text="Scale Bar Pixels per mm").grid(row=1, column=0)
tk.Entry(root, textvariable=config.scale_bar_pixels_per_mm).grid(row=1, column=1)

tk.Label(root, text="Grayscale Threshold").grid(row=2, column=0)
tk.Entry(root, textvariable=config.grayscale_threshold).grid(row=2, column=1)

tk.Label(root, text="Bottom Crop Ratio").grid(row=3, column=0)
tk.Entry(root, textvariable=config.bottom_crop_ratio).grid(row=3, column=1)

tk.Label(root, text="Smaller Grain Area Min").grid(row=4, column=0)
tk.Entry(root, textvariable=config.smaller_grain_area_min).grid(row=4, column=1)

tk.Label(root, text="Smaller Grain Area Max").grid(row=5, column=0)
tk.Entry(root, textvariable=config.smaller_grain_area_max).grid(row=5, column=1)

tk.Label(root, text="Larger Grain Area Min").grid(row=6, column=0)
tk.Entry(root, textvariable=config.larger_grain_area_min).grid(row=6, column=1)

tk.Label(root, text="Larger Grain Area Max").grid(row=7, column=0)
tk.Entry(root, textvariable=config.larger_grain_area_max).grid(row=7, column=1)

# Add a button to re-run the grain counting
tk.Button(root, text="Run Grain Counting", command=grainCounting.run_grain_counting).grid(row=8, column=0, columnspan=2)

# Add a button to reset the parameters to their default values
tk.Button(root, text="Reset Values", command=grainCounting.reset_values).grid(row=9, column=0, columnspan=2)

root.mainloop()
