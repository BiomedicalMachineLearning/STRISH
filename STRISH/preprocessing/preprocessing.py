from typing import Optional, Union, Mapping  # Special
from typing import Sequence, Iterable  # ABCs
from typing import Tuple  # Classes
import pandas as pd
import numpy as np
from pathlib import Path
from ..core import STRISH_Obj
from ..utils import *

def preprocess_clip_expression_range(strish_obj: STRISH_Obj, lower:float=0, upper:float=0.95):
    """ Clip the marker expression to a certain range of value"""
    logging.warning(f'Clipped the expression to {lower} and {upper}')
    clipped_x = strish_obj.to_df().clip(lower=lower, upper=strish_obj.to_df().quantile(upper), axis=1)
    strish_obj.X = clipped_x
        
def preprocess_clip_size_shape_range(strish_obj: STRISH_Obj, column:str, lower:float=0, upper:float=0.95):
    """ Clip the cell size or to a certain range of value (only one column at a time)"""
    logging.warning(f'Clipped the cell {column} to {lower} and {upper}')
    plot_columns = [col for col in self.obs.columns if 'Nucleus' in col]
    clipped_x = self.obs[colum].clip(lower=lower, upper=self.obs[colum].quantile(upper), axis=1)
    self.obs = clipped_x

def preprocess_filter_size_shape(strish_obj: STRISH_Obj, column:str, lower:float=0.05, upper:float=0.95):
    """ Filter out cells that are too small or too large that might be outlier """
    logging.warning(f'Clipped the cell from {column} which is less than {lower} and larger than {upper}')
    filtered_data = self[(strish_obj.obs[column] < np.quantile(strish_obj.obs[column], upper)) 
                         & (strish_obj.obs[column] > np.quantile(strish_obj.obs[column], lower))]
    return filtered_data