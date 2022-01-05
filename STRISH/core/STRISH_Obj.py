from anndata import AnnData
from typing import Optional, Union, Mapping
from typing import Sequence
from shapely.geometry import Polygon
import pandas as pd
import re
import numpy as np
import logging
from PIL import Image


class STRISH_Obj(AnnData):
    def __init__(
        self, 
        cnt_matrix: pd.DataFrame, 
        meta_vars: pd.DataFrame, 
        ref_image: Optional[np.ndarray],
        polygon: Optional[Union[pd.DataFrame, Mapping[str, Sequence[Polygon]]]]=None,
        is_view: bool=False
    ):
        super().__init__(cnt_matrix, asview=is_view)
        self.obs = meta_vars
        self._polygon = polygon
        self._ref_image = ref_image
        for col in meta_vars.columns: 
            if re.match(r'^Centroid\s+(.*)', col):
                if 'X' in col:
                    self.centroid_X = col
                if 'Y' in col:
                    self.centroid_Y = col
                self._original_coord_unit = re.sub('^[X|Y]+\s', '' ,re.findall(r'^Centroid\s+(.*)', col)[0])
        self._ref_image_unit = 'px'

    def _gen_repr(self, n_obs, n_vars) -> str:
        """Overide the default get object representation function from Anndata"""
        if self.isbacked:
            backed_at = f" backed at {str(self.filename)!r}"
        else:
            backed_at = ""
        descr = f"STRISH object with n_obs × n_vars = {n_obs} × {n_vars}{backed_at}"
        for attribute in [
            "obs",
            "var",
            "uns",
            "obsm",
            "varm",
            "layers", 'colocalized_scores' , 'colocalized_boxes',
            "obsp", 'all_rects', 'areas', 'contours',
            "varp",'ref_image','original_coord_unit','ref_image_unit',
        ]:
            if hasattr(self, attribute):
                if isinstance(getattr(self, attribute), pd.DataFrame):
                    keys = getattr(self, attribute).keys()
                    if len(keys) > 0:
                        descr += f"\n {attribute}: {str(list(keys))[1:-1]}"
                elif isinstance(getattr(self, attribute), np.ndarray):
                    descr += f"\n {attribute}: {getattr(self, attribute).shape}"
                elif isinstance(getattr(self, attribute), str):
                    descr += f"\n {attribute}: {getattr(self, attribute)}"
#                 else:
#                     descr += f"\n {attribute}: {type(getattr(self, attribute))}"
        return descr

    def __repr__(self):
        """Function to return representation of the object"""
        if self.is_view:
            return "View of " + self._gen_repr(self.n_obs, self.n_vars)
        else:
            return self._gen_repr(self.n_obs, self.n_vars)
        
    def __getitem__(self, index) -> 'STRISH_Obj':
        """Function to return the slice of the original object while keeping the other attribute accordingly
        Override from Anndata
        """
        oidx, vidx = self._normalize_indices(index)
        tmp = AnnData(self, oidx=oidx, vidx=vidx, asview=True)
        data = tmp.copy()
        logging.warning('Slice of data')
        cached_polygon = None
        if self._polygon:
            cached_polygon = self.polygon.iloc[vidx]
        observe_df = data.obs.replace({np.nan: None})
        # pour the important data back to the object and create a new STRISH_Obj
        strish_item = STRISH_Obj(data.to_df(), observe_df, ref_image=self.ref_image, polygon=cached_polygon, is_view=False)
        return strish_item

    def copy(self) -> "STRISH_Obj":
        """Full copy, optionally on disk."""
        """Overide Anndata's copy function to return the proper STRISH_Obj"""
        return STRISH_Obj(self.to_df(), self.obs, ref_image=self.ref_image, polygon=self.polygon, is_view=False)

    # Additional parameter to fit in the new object
    @property
    def polygon(self): 
        """A Dataframe stores the metadata of the cells including coordination, cell type, tissue id etc"""
        return self._polygon
    
    # @property
    # def contours(self):
    #     """A Dataframe stores the metadata of the cells including coordination, cell type, tissue id etc"""
    #     return self.contours
    
    # @contours.setter
    # def contours(self, value:np.ndarray):
    #     self.contours = value

    @property
    def ref_image(self):
        """stores the image that will be used as the reference of analysis and plot the result"""
        return self._ref_image
    
    @ref_image.setter
    def ref_image(self, value:Union[np.ndarray]):
        assert isinstance(value, (np.ndarray, Image)), 'Check the image type'
        self._ref_image = value
    
    @property 
    def original_coord_unit(self): 
        """ the dataframe or ndarray to store the count matrix of all cells"""
        return self._original_coord_unit
    
    @property 
    def ref_image_unit(self): 
        """ the dataframe or ndarray to store the count matrix of all cells"""
        return self._ref_image_unit
    
    @property
    def all_score_rects(self):
        return self.all_score_rects
    
    @all_score_rects.setter
    def all_score_rects(self, values):
        self.all_score_rects = values
        
    @property
    def heat_colors(self):
        return self.heat_colors
    
    @heat_colors.setter
    def heat_colors(self, value):
        self.heat_colors = value


