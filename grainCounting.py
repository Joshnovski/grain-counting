import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from PIL.TiffTags import TAGS
import PIL.ImageOps
from matplotlib.colors import ListedColormap


def get_metadata(directory_name, image_name):
    """ Get the metadata string """
    full_path = '%s/%s' % (directory_name, image_name)
    meta_dict = {}
    with Image.open(full_path) as img:
        meta_dict = img.tag
    return meta_dict


def process_metadata(meta_data):
    """ Process the meta data string into a dictionary"""
    relevant_metadata = meta_data[34683][0]
    metadata_dict = dict()
    split_relevant_metadata = relevant_metadata.split('\n')
    for line in split_relevant_metadata:
        split_line = line.replace('<', ',')
        split_line = split_line.replace('>', ',')
        split_line = split_line.split(',')
        if len(split_line) == 5:
            try:
                data_element = float(split_line[2])
            except ValueError:
                data_element = split_line[2]
            metadata_dict[split_line[1]] = data_element
    return metadata_dict


def process_image(directory_name, image_name, metadata_dict, phases, edge_detection_threshold, plot_bool):
    """ Open image, crop according to the metadata dict and count pixels according to the phases dict """
    # Open the image
    full_path = '%s/%s' % (directory_name, image_name)
    im = Image.open(full_path)
    # Convert the image to greyscale
    im = PIL.ImageOps.grayscale(im)
    # Crop off the banner
    width, height = im.size
    im = im.crop((0, 0, width, height - metadata_dict['databarHeight']))
    # Convert the image to a numpy array
    image_as_numpy = np.array(im)
    binned_image = np.zeros(np.shape(image_as_numpy))
    height, width = np.shape(image_as_numpy)
    phases_list = list(phases.keys())
    # Assign the phases to a binned array
    for jj in range(len(phases_list)):
        phase = phases_list[jj]
        indices = np.where(np.logical_and(image_as_numpy >= phases[phase][0], image_as_numpy < phases[phase][1]))
        binned_image[indices] = jj + 1
    # Detect the edges of the stitched image by looking at each row and column for first and last non-zero.
    for ii in range(height):
        current_row = image_as_numpy[ii, :]
        non_zero_ind = np.where(current_row > edge_detection_threshold)
        if np.size(non_zero_ind) > 0:
            row_start = np.min(non_zero_ind)
            row_end = np.max(non_zero_ind)
            # Assign pixels outside of this range as -1
            binned_image[ii, :row_start] = -1
            binned_image[ii, row_end:] = -1
        else:
            binned_image[ii, :] = -1
    # Detect the edges of the stitched image by looking at each row and column for first and last non-zero.
    for ii in range(width):
        current_col = image_as_numpy[:, ii]
        non_zero_ind = np.where(current_col > edge_detection_threshold)
        if np.size(non_zero_ind) > 0:
            col_start = np.min(non_zero_ind)
            col_end = np.max(non_zero_ind)
            # Assign pixels outside of this range as -1
            binned_image[:col_start, ii] = -1
            binned_image[col_end:, ii] = -1
        else:
            binned_image[:, ii] = -1
    # Count the pixels assigned to each phase
    pixel_count_dict = dict()
    pixel_count_dict['Unassigned'] = np.sum(np.where(np.logical_or(binned_image == -1, binned_image == 0)))
    pixel_count = 0
    pixel_count_inc_unassigned = pixel_count_dict['Unassigned']
    for jj in range(len(phases_list)):
        pixel_count_dict[phases_list[jj]] = np.sum(np.where(binned_image == jj + 1))
        pixel_count += pixel_count_dict[phases_list[jj]]
        pixel_count_inc_unassigned += pixel_count_dict[phases_list[jj]]
    # Calculate as an area fraction
    area_fraction = dict()
    area_fraction_inc_unassigned = dict()
    for phase in pixel_count_dict:
        area_fraction[phase] = pixel_count_dict[phase] / pixel_count
        area_fraction_inc_unassigned[phase] = pixel_count_dict[phase] / pixel_count_inc_unassigned
    # Remove the unassigned pixels from the area fraction output
    del area_fraction['Unassigned']
    # Calculate areas
    # total_area = pixel_count * metadata_dict['pixelWidth unit="um"'] * metadata_dict['pixelHeight unit="um"'] * 1E-8
    # Display original bounds and area fraction
    print(phases)
    print(area_fraction)

    # Plot the binned image next to the original
    if plot_bool:
        ax1 = plt.subplot(1, 2, 1)
        # ax1.imshow(binned_image, cmap='Accent') # original colour scheme
        ax1.imshow(im, cmap=ListedColormap(["gainsboro", "gainsboro", "navy"])) # new colour scheme
        title_string = ''
        for jj in range(len(phases_list)):
            title_string += ' %i is %s: %i%%,' % (jj + 1, phases_list[jj], round(100 * area_fraction[phases_list[jj]]))
        plt.title(title_string)
        ax2 = plt.subplot(1, 2, 2)
        ax2.imshow(im, cmap='gray')

        plt.show()
    return area_fraction