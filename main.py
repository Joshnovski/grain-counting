import tkinter as tk
import config_watershedAll
import grainCounting_watershedAll

root = tk.Tk()
root.title("Grain Counting Parameters")

config_watershedAll.init_variables(root)  # Initialize the tkinter variables

frame = tk.Frame(root, bd=2, relief='groove', padx=5, pady=5)
frame2 = tk.Frame(root, bd=2, relief='groove', padx=5, pady=5)
frame3 = tk.Frame(root, bd=2, relief='groove', padx=5, pady=5)

frame.grid(row=0, column=0, sticky='nsew', padx=(10, 1), pady=10)
frame2.grid(row=1, column=0, sticky='nsew', padx=(10, 1), pady=10)
frame3.grid(row=2, column=0, sticky='nsew', padx=(10, 1), pady=10)

# Add all the entries for the parameters

tk.Label(frame, text="Scale Factor: ").grid(row=0, column=0, sticky='W', padx=5, pady=2)
tk.Entry(frame, textvariable=config_watershedAll.scale_factor, width=16).grid(row=0, column=1)

tk.Label(frame, text="Scale Bar Pixels per mm:").grid(row=1, column=0, sticky='W', padx=5, pady=2)
tk.Entry(frame, textvariable=config_watershedAll.scale_bar_pixels_per_mm, width=16).grid(row=1, column=1)

tk.Label(frame, text="Bottom Crop Ratio:").grid(row=2, column=0, sticky='W', padx=5, pady=2)
tk.Entry(frame, textvariable=config_watershedAll.bottom_crop_ratio, width=16).grid(row=2, column=1)

tk.Label(frame2, text="*Warning: May Highlight Tile Borders*").grid(row=3, column=0, sticky='W', padx=10, pady=5)
tk.Checkbutton(frame2, text="Equalize Histogram", variable=config_watershedAll.equalize_hist).grid(row=3, column=2)

tk.Label(frame2, text="Pre-Process Contrast Threshold:").grid(row=5, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config_watershedAll.grayscale_threshold).grid(row=5, column=2)

tk.Label(frame2, text="Blur Kernel Size (Odd Values Only):").grid(row=6, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config_watershedAll.kernel_size).grid(row=6, column=2)

tk.Label(frame2, text="Distance Transform Contrast Threshold:").grid(row=7, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config_watershedAll.distanceTransform_threshold).grid(row=7, column=2)

tk.Label(frame2, text="Grain Edge Morphology Simplicity:").grid(row=8, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config_watershedAll.grain_morphology).grid(row=8, column=2)

tk.Label(frame3, text="Smaller Grain Area Min (Pixels):").grid(row=10, column=0, sticky='W', padx=10, pady=4)
blue_square = tk.Label(frame3, bg='blue', width=2, height=1)
blue_square.grid(row=10, column=1)
tk.Entry(frame3, textvariable=config_watershedAll.smaller_grain_area_min).grid(row=10, column=2, padx=(10, 10))

tk.Label(frame3, text="Smaller Grain Area Max (Pixels):").grid(row=11, column=0, sticky='W', padx=10, pady=4)
blue_square = tk.Label(frame3, bg='blue', width=2, height=1)
blue_square.grid(row=11, column=1)
tk.Entry(frame3, textvariable=config_watershedAll.smaller_grain_area_max).grid(row=11, column=2, padx=(10, 10))

tk.Label(frame3, text="Larger Grain Area Min (Pixels):").grid(row=12, column=0, sticky='W', padx=10, pady=4)
red_square = tk.Label(frame3, bg='red', width=2, height=1)
red_square.grid(row=12, column=1)
tk.Entry(frame3, textvariable=config_watershedAll.larger_grain_area_min).grid(row=12, column=2, padx=(10, 10))

tk.Label(frame3, text="Larger Grain Area Max (Pixels):").grid(row=13, column=0, sticky='W', padx=10, pady=4)
red_square = tk.Label(frame3, bg='red', width=2, height=1)
red_square.grid(row=13, column=1)
tk.Entry(frame3, textvariable=config_watershedAll.larger_grain_area_max).grid(row=13, column=2, padx=(10, 10))

tk.Label(frame3, text="Uncertain Grain Area Min (Pixels):").grid(row=14, column=0, sticky='W', padx=10, pady=4)
green_square = tk.Label(frame3, bg='green', width=2, height=1)
green_square.grid(row=14, column=1)
tk.Entry(frame3, textvariable=config_watershedAll.uncertain_grain_area_min).grid(row=14, column=2, padx=(10, 10))

tk.Label(frame3, text="Uncertain Grain Area Max (Pixels):").grid(row=15, column=0, sticky='W', padx=10, pady=4)
green_square = tk.Label(frame3, bg='green', width=2, height=1)
green_square.grid(row=15, column=1)
tk.Entry(frame3, textvariable=config_watershedAll.uncertain_grain_area_max).grid(row=15, column=2, padx=(10, 10))

root.grid_columnconfigure(0, weight=1, minsize=20)  # Add padding on left side
root.grid_columnconfigure(3, weight=1, minsize=10)  # Add padding on right side

# Add a button to re-run the grain counting
tk.Button(frame, text="Run", command=grainCounting_watershedAll.run_grain_counting, width=12).grid(row=0, column=2, pady=2, padx=(24, 2), sticky='E')

# Add a button to reset the parameters to their default values
tk.Button(frame, text="Reset Values", command=grainCounting_watershedAll.reset_values, width=12).grid(row=2, column=2, pady=2, padx=(24, 2), sticky='E')

# Add a button to select a file
tk.Button(frame, text="Select File", command=grainCounting_watershedAll.select_file, width=12).grid(row=1, column=2, pady=2, padx=(24, 2), sticky='E')


root.mainloop()
