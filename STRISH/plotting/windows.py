from typing import Optional, Union, Mapping  # Special
from typing import Sequence, Iterable  # ABCs
from typing import Tuple  # Classes
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from skimage import io as sk_io
from pathlib import Path
from ..core import STRISH_Obj
from ..utils import *
import matplotlib.ticker as plticker
import cv2
import logging
from skimage import measure

def plot_scanned_windows(
    strish_object:STRISH_Obj, 
    box_thickness=5, 
    dpi=400, 
    inteval=256, 
    save_fn:Optional[str]=None
):
    if hasattr(strish_object, 'all_rects'):
        all_rects_over_image = draw_rectangles(strish_object.ref_image, strish_object.all_rects, thickness=box_thickness)
    else:
        all_rects = list()
        areas = list()
        for box in strish_object.obs['Colocal_window'].unique():
            if isinstance(box, str): #(isinstance(box, float) and not np.isnan(box)):
                int_box = [int(i) for i in box.split(',')]
                all_rects.append(int_box)
                areas.append((int_box[2]-int_box[0])*(int_box[3]-int_box[1]))
#             strish_object.areas = np.array(list(set(areas)))
#             strish_object.all_rects = np.array(all_rects)
        all_rects_over_image = draw_rectangles(strish_object.ref_image, all_rects, thickness=box_thickness)

    fig=plt.figure(figsize=(float(strish_object.ref_image.shape[0])/dpi,
                    float(strish_object.ref_image.shape[1])/dpi),dpi=dpi)
    ax=fig.add_subplot(111)
    fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
    # Set the gridding interval: here we use the major tick interval
    myInterval=inteval
    loc = plticker.MultipleLocator(base=myInterval)
#         print(loc)
    if strish_object.ref_image.shape[1] > strish_object.ref_image.shape[0]:
        ax.yaxis.set_major_locator(loc)
        ax.xaxis.set_major_locator(loc)
    else:
        ax.xaxis.set_major_locator(loc)
        ax.yaxis.set_major_locator(loc)
    # Add the grid
    ax.grid(which='major', axis='both', linestyle='-')
    ax.imshow(all_rects_over_image, vmax=255, vmin=0)
    if save_fn:
        fig.savefig(save_fn)
            
def plot_tissue_window_contour(
    strish_object:STRISH_Obj, 
    extend_margin:int=1, 
    window_area_threshold:Optional[Union[int,float]]=None):
    if 'Colocal_window' not in getattr(strish_object, 'obs').keys() :
        logging.exception(f' Colocal_window is missing')
        raise Exception('Please run scan_cell_locs_by_window')


    contour_rects = list()
    dummy_score = list()

    for box in strish_object.obs['Colocal_window'].unique():
        if isinstance(box, str):
            int_box = [int(i) for i in box.split(',')]
            area = (int_box[2]-int_box[0])*(int_box[3]-int_box[1])
            if window_area_threshold:
                if area < window_area_threshold:
                    contour_rects.append(int_box)
                    dummy_score.append(1)
            else:
                contour_rects.append(int_box)
                dummy_score.append(1)

    dummy_score = np.array(dummy_score)
    dummy_color = np.array(map_heat_values2colors(dummy_score))
    dummy_color = dummy_color * 255

    mask_by_dapi = draw_rectangles_heat(np.zeros_like(strish_object.ref_image), 
                                       contour_rects, dummy_color, extend_margin)
    gray_all = cv2.cvtColor(mask_by_dapi, cv2.COLOR_RGB2GRAY)
    contours = measure.find_contours(gray_all, 0.8)

    strish_object.contours = np.array(contours)
    logging.warning(f'Added attributes contours')
    fig, axs = plt.subplots(1, 2,dpi=200)
    # ax.imshow(np.zeros_like(mask_by_dapi), cmap=plt.cm.gray)
    axs[0].imshow(mask_by_dapi, vmax=255, vmin=0)
    axs[1].imshow(strish_object.ref_image, cmap=plt.cm.gray)
#         xs_coord = list()
#         ys_coord = list()
    showing_len = 1
    if len(contours) > 2:
        showing_len = 2
    else:
        showing_len = len(contours)
    logging.warning(f'For visualisation, only showing maximum two contours from list of contours')
    for n, contour in enumerate(contours[0:showing_len]):
        axs[1].plot(contour[:, 1], contour[:, 0], 'r',linewidth=1.0)
#             xs_coord.extend(contour[:, 1])
#             ys_coord.extend(contour[:, 0])
    axs[1].axis('image')
    axs[1].set_xticks([])
    axs[1].set_yticks([])
    plt.show()
    
    
def plot_colocalized_heatmap(
    strish_object:STRISH_Obj, 
    dpi=1000, 
    orientation='vertical', 
    show_contour=False, 
    n_contours=2,
    save_fn:Optional[str]=None):
    if not hasattr(strish_object, 'all_score_rects') and not hasattr(strish_object, 'heat_colors'):
        logging.exception(f' colocalized_boxes is missing')
        raise Exception('Please run scan_cell_colocalised_dectection')
    tempt_img = np.zeros_like(strish_object.ref_image)
    colocalised_heatmap = draw_rectangles_heat(tempt_img, strish_object.all_score_rects, strish_object.heat_colors)
    fig, ax = plt.subplots(dpi=dpi)
    scores_range = np.array(strish_object.box_scores)
    map_color = ax.imshow(colocalised_heatmap, vmax=scores_range.max(), vmin=scores_range.min())
    fig.colorbar(map_color, orientation=orientation)
    if show_contour:
        if n_contours != 0:
            for contour in strish_object.contours[0:n_contours]:
                ax.plot(contour[:, 1], contour[:, 0], 'r',linewidth=1.0)
        else:
            for contour in strish_object.contours[0:2]:
                ax.plot(contour[:, 1], contour[:, 0], 'r',linewidth=1.0)
    ax.axis('off')

    if save_fn:
        fig.savefig(save_fn)