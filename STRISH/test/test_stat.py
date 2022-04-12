from STRISH.tools import stat, registration
from STRISH.readwrite import Read_RNAscope
import STRISH.preprocessing as strish_preprocessing
import STRISH.plotting as strish_plotting
from pathlib import Path

if __name__ == "__main__":
    input_path1 = Path('/Volumes/BiomedML/Projects/SkinSpatial/input_data/RNAscope_data/scene1_R1/')
    detection_report_fn = 'scene_1_R1_detection_measurement.txt'
    ref_image_fn = 'scene_1_R1_THY1_IL34_CSFR1-Stitching-01_RGB_ref.JPEG.jpg'

    signal2rna_r1 = {'Cy7': 'CSF1R', 'Cy5': 'IL34', 'Cy3': 'Thy1', 'DAPI': 'DAPI'}
    signal2rna_r2 = {'Cy7': 'CD207', 'Cy5': 'ITGAM', 'DAPI': 'DAPI'}
    my_strish_obj = Read_RNAscope(input_path1.joinpath(detection_report_fn), input_path1.joinpath(ref_image_fn))
    strish_preprocessing.convert_unit_micron2pixel(my_strish_obj,original_width_micron=3869.78,
                                                original_height_micron=8858.36)
    strish_preprocessing.scan_cell_locs_by_window(my_strish_obj, max_cell_per_window=50, init_sub_w=0.5, init_sub_h=0.25)
    strish_plotting.plot_tissue_window_contour(my_strish_obj, extend_margin=3, window_area_threshold=68845)

    print(my_strish_obj)