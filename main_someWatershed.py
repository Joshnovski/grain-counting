import tkinter as tk
import config
import grainCounting

root = tk.Tk()
root.title("Grain Counting Parameters")

config.init_variables(root)

frame = tk.Frame(root, bd=2, relief='groove', padx=5, pady=5)
frame2 = tk.Frame(root, bd=2, relief='groove', padx=5, pady=5)
frame3 = tk.Frame(root, bd=2, relief='groove', padx=5, pady=5)

frame.grid(row=0, column=0, sticky='nsew', padx=(10, 1), pady=10)
frame2.grid(row=1, column=0, sticky='nsew', padx=(10, 1), pady=10)
frame3.grid(row=2, column=0, sticky='nsew', padx=(10, 1), pady=10)

# Add all the entries for the parameters
tk.Label(frame, text="Scale Factor: ").grid(row=0, column=0, sticky='W', padx=5, pady=2)
tk.Entry(frame, textvariable=config.scale_factor, width=16).grid(row=0, column=1)

tk.Label(frame, text="Scale Bar Pixels per mm:").grid(row=1, column=0, sticky='W', padx=5, pady=2)
tk.Entry(frame, textvariable=config.scale_bar_pixels_per_mm, width=16).grid(row=1, column=1)

tk.Label(frame, text="Bottom Crop Ratio:").grid(row=2, column=0, sticky='W', padx=5, pady=2)
tk.Entry(frame, textvariable=config.bottom_crop_ratio, width=16).grid(row=2, column=1)

# tk.Label(root, text="------------------------").grid(row=4, column=0, sticky='W')

tk.Label(frame2, text="Grayscale Threshold:").grid(row=3, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config.grayscale_threshold).grid(row=3, column=2, padx=(0, 10))

tk.Label(frame2, text="Uncertain Grain Kernel Size (Odd):").grid(row=5, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config.kernel_size).grid(row=5, column=2, padx=(0, 10))

tk.Label(frame2, text="Overall Grain Kernel Size (Odd):").grid(row=6, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config.kernel_size_overall).grid(row=6, column=2, padx=(0, 10))

tk.Label(frame2, text="Distance Threshold:").grid(row=7, column=0, sticky='W', padx=10, pady=4)
tk.Entry(frame2, textvariable=config.distance_threshold).grid(row=7, column=2, padx=(0, 10))

# tk.Label(root, text="------------------------").grid(row=8, column=0, sticky='E')

tk.Label(frame3, text="Smaller Grain Area Min:").grid(row=9, column=0, sticky='W', padx=10, pady=4)
blue_square = tk.Label(frame3, bg='blue', width=2, height=1)
blue_square.grid(row=9, column=1)
tk.Entry(frame3, textvariable=config.smaller_grain_area_min).grid(row=9, column=2, padx=(20, 10))

tk.Label(frame3, text="Smaller Grain Area Max:").grid(row=10, column=0, sticky='W', padx=10, pady=4)
blue_square = tk.Label(frame3, bg='blue', width=2, height=1)
blue_square.grid(row=10, column=1)
tk.Entry(frame3, textvariable=config.smaller_grain_area_max).grid(row=10, column=2, padx=(20, 10))

tk.Label(frame3, text="Larger Grain Area Min:").grid(row=11, column=0, sticky='W', padx=10, pady=4)
red_square = tk.Label(frame3, bg='red', width=2, height=1)
red_square.grid(row=11, column=1)
tk.Entry(frame3, textvariable=config.larger_grain_area_min).grid(row=11, column=2, padx=(20, 10))

tk.Label(frame3, text="Larger Grain Area Max:").grid(row=12, column=0, sticky='W', padx=10, pady=4)
red_square = tk.Label(frame3, bg='red', width=2, height=1)
red_square.grid(row=12, column=1)
tk.Entry(frame3, textvariable=config.larger_grain_area_max).grid(row=12, column=2, padx=(20, 10))

tk.Label(frame3, text="Uncertain Grain Area Min:").grid(row=13, column=0, sticky='W', padx=10, pady=4)
green_square = tk.Label(frame3, bg='green', width=2, height=1)
green_square.grid(row=13, column=1)
tk.Entry(frame3, textvariable=config.uncertain_grain_area_min).grid(row=13, column=2, padx=(20, 10))

tk.Label(frame3, text="Uncertain Grain Area Max:").grid(row=14, column=0, sticky='W', padx=10, pady=4)
green_square = tk.Label(frame3, bg='green', width=2, height=1)
green_square.grid(row=14, column=1)
tk.Entry(frame3, textvariable=config.uncertain_grain_area_max).grid(row=14, column=2, padx=(20, 10))

root.grid_columnconfigure(0, weight=1, minsize=20)  # Add padding on left side
root.grid_columnconfigure(3, weight=1, minsize=10)  # Add padding on right side

# Add a button to re-run the grain counting
tk.Button(frame, text="Run", command=grainCounting.run_grain_counting, width=12).grid(row=0, column=2, pady=2, padx=(10, 2), sticky='E')

# Add a button to reset the parameters to their default values
tk.Button(frame, text="Reset Values", command=grainCounting.reset_values, width=12).grid(row=2, column=2, pady=2, padx=(10, 2), sticky='E')

# Add a button to select a file
tk.Button(frame, text="Select File", command=grainCounting.select_file, width=12).grid(row=1, column=2, pady=2, padx=(10, 2), sticky='E')


root.mainloop()
