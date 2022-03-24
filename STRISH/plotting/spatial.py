from typing import Optional, Union, Mapping  # Special
from typing import Sequence, Iterable  # ABCs
from typing import Tuple  # Classes
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from ..core import STRISH_Obj
from ..utils import *
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


def plot_cell_spatial_scatter(strish_obj:STRISH_Obj ,
                                  label:Optional[str]=None, spot_size:Optional[float]=0.75, 
                                  linewidth:Optional[float]=1.0, color_mapper:Optional[dict]=None,
                                  legend_log=2,rasterize:Optional[bool]=True, save_fn:Optional[str]=None):
    """ plot the cell distribution in the spatial context """
    if 'X_px' not in list(strish_obj.obs.columns) and 'Y_px' not in list(strish_obj.obs.columns):
        logging.exception(f'Not consistent unit original_coord_unit is in {strish_obj.original_coord_unit} and ref_image_unit is in {strish_obj.ref_image_unit}')
        raise Exception('Please run convert_unit_micron2pixel')

    ox_coord = strish_obj.obs['X_px']
    oy_coord = strish_obj.obs['Y_px']
    if label:
        legend_patches = list()
        if color_mapper: 
            plt.scatter(ox_coord , oy_coord , s=spot_size,linewidth=linewidth, 
                        facecolors='none', 
                        edgecolors=[color_mapper[cell] for cell in strish_obj.obs[label].tolist()])
            for key, value in color_mapper.items():
                if key in strish_obj.obs[label].unique().tolist():
                    tmp_patch = mpatches.Patch(color=value, label=key)
                    legend_patches.append(tmp_patch)

        else:
            ax_color_mapper = sns.color_palette("tab20",  len(set(strish_obj.obs[label].values)))
            custom_mapper = dict()
            for index, color in enumerate(ax_color_mapper):
                custom_mapper[list(set(strish_obj.obs[label].values))[index]] = color
            plt.scatter(ox_coord , oy_coord , s=spot_size,linewidth=linewidth, 
                        facecolors='none', rasterized=rasterize,
                        edgecolors=[custom_mapper[cell] for cell in strish_obj.obs[label].tolist()]) 
            for key, value in custom_mapper.items():
                if key in strish_obj.obs[label].unique().tolist():
                    tmp_patch = mpatches.Patch(color=value, label=key)
                    legend_patches.append(tmp_patch)
        plt.rcParams['legend.title_fontsize'] = 24
        plt.legend(handles=legend_patches, title=r"$\bf{Cell\ types}$", loc=legend_log, 
                   prop={'size': 23})

    else:
        plt.scatter(ox_coord , oy_coord , s=spot_size,linewidth=linewidth, rasterized=rasterize,
                    facecolors='none',color='r')
    if save_fn:
        plt.savefig(save_fn)