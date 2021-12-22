from ..core import STRISH_Obj
from typing import Any, Union, Optional  # Meta
from typing import Iterable, Sequence, Mapping, MutableMapping  # Generic ABCs
from typing import Tuple, List  # Generic
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from skimage import io as sk_io
from pathlib import Path


def plot_expression_histogram(
    strish_object:STRISH_Obj, 
    figsize:Union[int,tuple]=(15,15), 
    save_fn:Optional[str]=None
):
        """ Visualization of the expression of every existing marker accross all the cell """
        if isinstance(figsize, tuple) and len(figsize) == 2:
            strish_object.to_df().hist(column=strish_object.to_df().columns, bins=50, figsize=figsize)
        elif isinstance(figsize, int):
            strish_object.to_df().hist(column=strish_object.to_df().columns, bins=50, figsize=(figsize, figsize))
        else:
            raise Exception(f'figsize is invalid {type(figsize)}, only support int or tuple format')
        if save_fn:
            plt.savefig(save_fn)
            
def plot_size_shape_histogram(
    strish_object:STRISH_Obj, 
    colums:Optional[Union[str, list]]=None,
    figsize:Union[int,tuple]=(15,15),
    save_fn:Optional[str]=None):
        """ Visualization of the cell's size and shape accross all the cells """
        plot_columns = None
        if colums: 
            plot_columns = colums
        else:
            plot_columns = [col for col in strish_object.obs.columns if 'Nucleus' in col]
        if isinstance(figsize, tuple) and len(figsize) == 2:
            strish_object.obs.hist(column=plot_columns, bins=50, figsize=figsize)
        elif isinstance(figsize, int):
            strish_object.obs.hist(column=plot_columns, bins=50, figsize=(figsize, figsize))
        else:
            raise Exception(f'figsize is invalid {type(figsize)}, only support int or tuple format')
        if save_fn:
            plt.savefig(save_fn)
          