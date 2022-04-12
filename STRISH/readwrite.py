from STRISH.core import STRISH_Obj
from typing import Any, Union, Optional
from skimage import io as sk_io
from pathlib import Path
import pandas as pd
import re
import tifffile
import cv2

def Read_Polaris(file_path: Union[str, Path],
                 ref_image: Union[str, Path] = None,
                 cell_mask: Optional[Union[str, Path]] = None) -> STRISH_Obj:
    data_table = pd.read_csv(file_path, sep='\t')
    short_markers = dict()
    expresion_cols = list()

    for col in data_table.columns:
        if 'Cell' in col and any(ele in col for ele in ['mean', 'Mean']):
            tmp_col = re.sub(r'Cell:|:|\s', '', re.findall(r'^(.*)\s(mean|Mean)$', col)[0][0])
            short_markers[col] = re.sub(r'\(.*?\)', '', tmp_col)
            expresion_cols.append(col)
    count_matrix = data_table.rename(columns=short_markers)[short_markers.values()]

    geometry_cols = list()
    regex_marker_rule = r''.join(['(?!{0})'.format(value.split(' ')[0]) for value in short_markers.values()])
    for col in data_table.columns:
        if re.match(r'^Centroid\s+(.*)', col) or re.match(r'^Nucleus:\s+{0}(.*)'.format(regex_marker_rule), col):
            geometry_cols.append(col)
    geo_vars = data_table[geometry_cols]

    if ref_image is None:
        qupath_folder = Path(file_path).parent.resolve()
        image_fns = [x.resolve() for x in qupath_folder.glob('*') if
                     x.suffix in ['.png', '.tif', '.tiff', '.jpg'] and x.is_file()]
        assert len(image_fns) < 1, 'Image for reference not found'
        assert len(image_fns) >= 2, 'Multiple images found'
        ref_img_data = sk_io.imread(image_fns[0])
    else:
        assert Path(ref_image).is_file(), 'Cannot file image from path' + str(ref_image)
        if '.tiff' in Path(ref_image).suffixes or '.tif' in Path(ref_image).suffixes:
            #             if '.ome' is in Path(ref_image).suffixes:
            ref_img_data = tifffile.imread(Path(ref_image))

        ref_img_data = sk_io.imread(ref_image)

    if cell_mask:
        segmentation_img = cv2.imread(cell_mask)
        numb_cells = segmentation_img.max()
        if numb_cells != data_table.shape[0]:
            raise Exception('Inconsistent of cell count from report and cell masks from image')
    #         else:
    #             from skimage import measure
    #             data_table['Polygon'] = None
    #             for index, cell_row in data_table.iterrows():
    #                 cell_mask_contours = measure.find_contours(np.array(segmentation_img)==int(index)+1, 0.1)
    #                 cell_polygon = Polygon(cell_mask_contours[0])
    #                 data_table['Polygon'].iloc[index] = cell_polygon

    strish_obj = STRISH_Obj(count_matrix, geo_vars, ref_img_data)
    return strish_obj


def Read_RNAscope(file_path: Union[str, Path],
                  ref_image: Union[str, Path] = None,
                  cell_mask: Optional[Union[str, Path]] = None) -> STRISH_Obj:
    data_table = pd.read_csv(file_path, sep='\t')
    short_markers = dict()
    expresion_cols = list()

    for col in data_table.columns:
        if 'Cell' in col and any(ele in col for ele in ['mean', 'Mean']):
            tmp_col = re.sub(r'Cell:|:|\s', '', re.findall(r'^(.*)\s(mean|Mean)$', col)[0][0])
            short_markers[col] = re.sub(r'\(.*?\)', '', tmp_col)
            expresion_cols.append(col)
    count_matrix = data_table.rename(columns=short_markers)[short_markers.values()]

    geometry_cols = list()
    regex_marker_rule = r''.join(['(?!{0})'.format(value.split(' ')[0]) for value in short_markers.values()])
    for col in data_table.columns:
        if re.match(r'^Centroid\s+(.*)', col) or re.match(r'^Nucleus:\s+{0}(.*)'.format(regex_marker_rule), col):
            geometry_cols.append(col)
    geo_vars = data_table[geometry_cols]

    if ref_image is None:
        qupath_folder = Path(file_path).parent.resolve()
        image_fns = [x.resolve() for x in qupath_folder.glob('*') if
                     x.suffix in ['.png', '.tif', '.tiff', '.jpg'] and x.is_file()]
        assert len(image_fns) < 1, 'Image for reference not found'
        assert len(image_fns) >= 2, 'Multiple images found'
        ref_img_data = sk_io.imread(image_fns[0])
    else:
        assert Path(ref_image).is_file(), 'Cannot file image from path' + str(ref_image)
        if '.tiff' in Path(ref_image).suffixes or '.tif' in Path(ref_image).suffixes:
            #             if '.ome' is in Path(ref_image).suffixes:
            ref_img_data = tifffile.imread(Path(ref_image))

        ref_img_data = sk_io.imread(ref_image)

    if cell_mask:
        segmentation_img = cv2.imread(cell_mask)
        numb_cells = segmentation_img.max()
        if numb_cells != data_table.shape[0]:
            raise Exception('Inconsistent of cell count from report and cell masks from image')

    strish_obj = STRISH_Obj(count_matrix, geo_vars, ref_img_data)

    return strish_obj


