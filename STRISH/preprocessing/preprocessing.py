import sys
sys.path.append("..")
from typing import Optional, Union, Mapping  # Special
from typing import Sequence, Iterable  # ABCs
from typing import Tuple  # Classes
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from ..core import STRISH_Obj
from ..utils import *


def preprocess_clip_expression_range(strish_obj: STRISH_Obj, lower: float = 0, upper: float = 0.95):
    """ Clip the marker expression to a certain range of value"""
    logging.warning(f'Clipped the expression to {lower} and {upper}')
    clipped_x = strish_obj.to_df().clip(lower=lower, upper=strish_obj.to_df().quantile(upper), axis=1)
    strish_obj.X = clipped_x


def preprocess_clip_size_shape_range(strish_obj: STRISH_Obj, column: str, lower: float = 0, upper: float = 0.95):
    """ Clip the cell size or to a certain range of value (only one column at a time)"""
    logging.warning(f'Clipped the cell {column} to {lower} and {upper}')
    plot_columns = [col for col in strish_obj.obs.columns if 'Nucleus' in col]
    clipped_x = strish_obj.obs[plot_columns].clip(lower=lower, upper=strish_obj.obs[plot_columns].quantile(upper), axis=1)
    strish_obj.obs = clipped_x


def preprocess_filter_size_shape(strish_obj: STRISH_Obj, column: str, lower: float = 0.05, upper: float = 0.95):
    """ Filter out cells that are too small or too large that might be outlier """
    logging.warning(f'Clipped the cell from {column} which is less than {lower} and larger than {upper}')
    filtered_data = strish_obj[(strish_obj.obs[column] < np.quantile(strish_obj.obs[column], upper))
                               & (strish_obj.obs[column] > np.quantile(strish_obj.obs[column], lower))]
    return filtered_data


def scan_cell_locs_by_window(strish_obj: STRISH_Obj, max_cell_per_window=100,
                                 init_sub_w: float = 0.5, init_sub_h: float = 0.5,
                                 subset_rate: Optional[float] = 0.5,
                                 input_shape: Optional[Union[list, tuple]] = None):
    list_annotation_boxes = list()
    init_ox, init_oy = 0, 0
    if input_shape:
        init_height, init_width = input_shape
    else:
        init_height, init_width, _ = strish_obj.ref_image.shape
    init_sub_h_size, init_sub_w_size = init_sub_h, init_sub_w
    logging.warning(f'Scanning for cell type colocalization by window')
    if 'X_px' not in list(strish_obj.obs.columns) and 'Y_px' not in list(strish_obj.obs.columns):
        logging.exception(
            f'Not consistent unit original_coord_unit is in {strish_obj.original_coord_unit} and ref_image_unit is in {strish_obj.ref_image_unit}')
        Exception('Please run convert_unit_micron2pixel')

    strish_obj.obs['Colocal_window'] = None
    list_annots = list()
    all_rects = list()
    areas = list()
    add_detection_boxes(list_annots, init_ox, init_oy,
                        init_width, init_height,
                        init_sub_h_size, init_sub_w_size)

    while len(list_annots) > 0:
        for annot_box in list_annots:
            list_annots.remove(annot_box)
            #                 print(len(list_annots))
            min_ox, min_oy, max_ox, max_oy = annot_box
            tmp_cell_geo = strish_obj.obs[(min_ox < strish_obj.obs['X_px']) &
                                    (strish_obj.obs['X_px'] < max_ox) &
                                    (min_oy < strish_obj.obs['Y_px']) &
                                    (strish_obj.obs['Y_px'] < max_oy)]
            cell_count = tmp_cell_geo.shape[0]
            # BFS here

            if cell_count < 3:
                continue
            elif (3 <= cell_count < max_cell_per_window):
                strish_obj.obs['Colocal_window'] = np.where(strish_obj.obs.index.isin(tmp_cell_geo.index.values),
                                                      ','.join([str(i) for i in annot_box]),
                                                      strish_obj.obs['Colocal_window'])
                all_rects.append(annot_box)
                areas.append((annot_box[2] - annot_box[0]) * (annot_box[3] - annot_box[1]))
            else:
                sub_annot_width = max_ox - min_ox
                sub_annot_height = max_oy - min_oy
                add_detection_boxes(list_annots, min_ox, min_oy,
                                    sub_annot_width, sub_annot_height,
                                    sub_w_size=subset_rate, sub_h_size=subset_rate)
    strish_obj.areas = np.array(list(set(areas)))
    strish_obj.all_rects = np.array(all_rects)
    logging.warning(f'Added Colocal_window to obs')


def convert_unit_micron2pixel(strish_obj: STRISH_Obj, original_width_micron, original_height_micron,
                              X_col: Optional[str] = None, Y_col: Optional[str] = None):
    """ Running the conversion of the unit from micron unit to pixel image """
    """ In case you do not have the conversion unit please use the original OME.tiff extract_physical_dimension"""
    if strish_obj.original_coord_unit != strish_obj.ref_image_unit:
        logging.warning(f'Converting {strish_obj.original_coord_unit} to {strish_obj.ref_image_unit}')

    if X_col:
        strish_obj.obs['X_px'] = convert_micron2pixel(strish_obj.obs[X_col], original_width_micron,
                                                strish_obj.ref_image.shape[1])
    else:
        strish_obj.obs['X_px'] = convert_micron2pixel(strish_obj.obs[strish_obj.centroid_X], original_width_micron,
                                                strish_obj.ref_image.shape[1])

    if Y_col:
        strish_obj.obs['Y_px'] = convert_micron2pixel(strish_obj.obs[Y_col], original_height_micron,
                                                strish_obj.ref_image.shape[0])
    else:
        strish_obj.obs['Y_px'] = convert_micron2pixel(strish_obj.obs[strish_obj.centroid_Y], original_height_micron,
                                                strish_obj.ref_image.shape[0])
    logging.warning(f'X_px and Y_px are added to meta_vars')