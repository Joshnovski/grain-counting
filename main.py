import grainCounting
# Specify the location of the image
directory_name = '//mgathermalnas1/RD Onsite/BATCHES/1226-001-01/SI 200423/polygon'   # e.g. 'Y:/BATCHES/1259/1259-001-01 SI'
# directory_name = '//mgathermalnas1/RD Onsite/BATCHES/1165-011/1165-011-08 polygon SI/SI polygon 1165-011-08'
stitched_image_name = 'SI 1226-001-01.tiff'         # Include the file extension .tiff
# The program gets the metadata
meta_data = grainCounting.get_metadata(directory_name, stitched_image_name)
metadata_dict = grainCounting.process_metadata(meta_data)
# Specify the name of the phases and the intensity range of grey associated. Intensity ranges from [0, 255] (dark to
# bright).
# og greyscale phases = {'Void': [0, 20], 'C': [20, 100], 'AlN': [100, 150], 'Al': [150, 255]}

# 'Fe': [230, 255]} # PT
# phases = {'Void': [0, 15], 'C': [16, 60], 'O': [61, 130], 'AlN': [131, 160], 'Al': [161, 255]} # PT 11/04/23
phases = {'Other phases': [0, 160], 'Al': [161, 255]} # just Al
# phases = {'Other phases': [0, 15], 'C': [16, 60], 'Other phases': [61, 160], 'Al': [161, 255]} # just Al and C

edge_detection_threshold = 75
# Count the pixels and calculate the area fraction according to the range
area_fraction = grainCounting.process_image(directory_name, stitched_image_name, metadata_dict, phases,
                                            edge_detection_threshold, True)