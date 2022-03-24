import numpy as np
import cv2
import os
import seaborn as sns
from PIL import Image
import glob
import io
from scipy.optimize import minimize

def get_files_in_directory(directory, postfix=""):
    """ list all the files with postfix in the directory and return the sorted list """
    fileNames = [s for s in os.listdir(directory) if not os.path.isdir(os.path.join(directory, s))]
    if not postfix or postfix == "":
        return sorted(fileNames)
    else:
        return sorted([s for s in fileNames if s.lower().endswith(postfix)])
    
def get_files_in_dir_recursively(directory, postfix='json'):
    """ list all the files in the directory with postfix recursively """
    files = [file for file in glob.glob(os.path.join(directory, '**/*.{0}'.format(postfix)), recursive=True)]
    return files


def get_subdirectories_in_directory(directory, postfix=""):
    """ list all the subdirectories in the directory """
    dir_names = [s for s in os.listdir(directory) if os.path.isdir(os.path.join(directory, s))]
    return sorted(dir_names)


def overlay_pil_imgs(foreground, background, best_loc=(0, 0), alpha=0.5):
    """ overlay two images to visualize the registration """
    newimg1 = Image.new('RGBA', size=background.size, color=(0, 0, 0, 0))
    newimg1.paste(foreground, best_loc)
    newimg1.paste(background, (0, 0))

    newimg2 = Image.new('RGBA', size=background.size, color=(0, 0, 0, 0))
    newimg2.paste(background, (0, 0))
    newimg2.paste(foreground, best_loc)
    result = Image.blend(newimg1, newimg2, alpha=alpha)
    return result


def mkdirs(dirs):
    """ create new directory  if it does not exist"""
    if not os.path.exists(dirs):
        os.makedirs(dirs)


def convert_micron2pixel(x_micron, micron_dim, scale_dim):
    """ 
    convert the annotation box coordinate from micron unit to pixel unit
    ox_px_coord = convert_micron2pixel(ox_coords, 6276.93, im_demo.shape[1])
    oy_px_coord = convert_micron2pixel(oy_coords, 15235.53, im_demo.shape[0])
    """
    return x_micron*scale_dim/micron_dim

def inverse_transform_point(xform, p):
    """
    Returns the inverse-transform of a point.

    :param sitk.Transform xform: The transform to invert
    :param (float,float)|[float|float]|np.ndarray p: The point to find inverse for
    :return np.ndarray, bool: The point and whether the operation succeeded or not
    """

    def fun(x):
        return np.linalg.norm(xform.TransformPoint(x) - p)

    p = np.array(p)
    res = minimize(fun, p, method='Powell')
    return res.x, res.success


def add_detection_boxes(list_annots, current_ox, current_oy, 
                        current_width, current_height, 
                        sub_h_size=0.5, sub_w_size=0.5,):
    """
    Recursively add the scanning windows to the current coordinates by splitting the current into sub-smaller
    list_annots: current list of annotation windows for BFS
    current_ox, current_oy: refer to left, and top coordinate values.
    current_width, current_height: refer the size of current considering window
    sub_h_size, sub_w_size: ratios for splitting the current window into subsmaller 
    """
    numb_w_subbox = int(1/sub_w_size)
    numb_h_subbox = int(1/sub_h_size)
    sub_annot_width, sub_annot_height = int(current_width * sub_w_size), int(current_height * sub_h_size)
#         list_annots = list()
    for idx_w in range(numb_w_subbox):
        for idx_h in range(numb_h_subbox):
            stride_x = idx_w * sub_annot_width
            stride_y = idx_h * sub_annot_height
            tmp_rect = [stride_x+current_ox, 
                        stride_y+current_oy, 
                        stride_x+current_ox+sub_annot_width, 
                        stride_y+current_oy+sub_annot_height]
            list_annots.append(tmp_rect)


def map_heat_values2colors(values, color_palette='viridis'):
    """
    Map and convert the co-localization scores to colors range 
    """
    from collections import OrderedDict
    colors = list()
    sorted_values = np.sort(values, kind='mergesort')
    set_box_scores = list(OrderedDict.fromkeys(sorted_values).keys())
    heat_colors_range = sns.color_palette(color_palette, len(set_box_scores))
    for value in values:
        raw_color = heat_colors_range[set_box_scores.index(value)]
        colors.append(raw_color)
    return np.array(colors)


def list_to_int(list1D):
    """ convert list of float values to integer values """
    return [int(float(x)) for x in list1D]


def draw_rectangles(img, rects, color=(0, 255, 255), thickness=7):
    """ draw rectangles to a cv2 img 
    img: cv2 image in 2D/3D array
    rects: list of rectangle coordinates top, left, bottom, right
    color: rectangle color
    thickness: the thickness of 4 edges
    """
#     print(img.shape)
    clone_image = img.copy()
    for rect in rects:
        pt1 = tuple(list_to_int(rect[0:2]))
        pt2 = tuple(list_to_int(rect[2:]))
#         print(pt1, pt2)
        cv2.rectangle(clone_image, pt1, pt2, color, thickness, cv2.FILLED)
    return clone_image


def draw_rectangles_heat(img, rects:dict, colors:list, thickness=0):
    """
    Plot the spatial heatmap of cell colocalization score
    rects: a list of windows that store the coordinates, top left, and bottom right
    color: mapped the scores of each rect with the color value
    thickness: define the thickness of the rect
    """
    clone_image = img.copy()
    for index, rect in enumerate(rects):
        pt1 = np.array(list_to_int(rect[0:2]))
        pt2 = np.array(list_to_int(rect[2:]))
        cv2.rectangle(clone_image, tuple(pt1-thickness), tuple(pt2+thickness), colors[index], cv2.FILLED)
    return clone_image


def extract_physical_dimension(ome_tiff_path):
        """ A function to load the original OME tiff to extract micron resolution and pixel conversion"""
        """ return two dictionaries: one for unit conversion and the other for channel2name"""
        import tifffile
        import xml.etree.ElementTree
        tiff_image = tifffile.TiffFile(ome_tiff_path)
        omexml_string = tiff_image.pages[0].description
        root = xml.etree.ElementTree.parse(io.StringIO(omexml_string))
        namespaces = {'ome': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'}
        channels = root.findall('ome:Image[1]/ome:Pixels/ome:Channel', namespaces)
        channel_names = [c.attrib['Name'] for c in channels]
        resolution = root.findall('ome:Image[1]/ome:Pixels', namespaces)
        attribute = resolution[0]

        resolution_unit = dict()
        resolution_unit['original_X_micron'] = float(attribute.attrib['SizeX']) * float(
            attribute.attrib['PhysicalSizeX'])
        resolution_unit['original_Y_micron'] = float(attribute.attrib['SizeY']) * float(
            attribute.attrib['PhysicalSizeY'])
        resolution_unit['original_X_pixel'] = int(attribute.attrib['SizeX'])
        resolution_unit['original_Y_pixel'] = int(attribute.attrib['SizeY'])
        return resolution_unit, channel_names