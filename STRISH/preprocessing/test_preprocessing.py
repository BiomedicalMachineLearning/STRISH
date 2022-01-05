import unittest
from ..readwrite import Read_RNAscope
from pathlib import Path
from utils import convert_micron2pixel
from preprocessing import *

input_path1 = Path('/Volumes/BiomedML/Projects/SkinSpatial/input_data/RNAscope_data/scene1_R1/')
detection_report_fn = 'scene_1_R1_detection_measurement.txt'
ref_image_fn = 'scene_1_R1_THY1_IL34_CSFR1-Stitching-01_RGB_ref.JPEG.jpg'

signal2rna_r1 = {'Cy7':'CSF1R','Cy5':'IL34','Cy3':'Thy1', 'DAPI':'DAPI'}
signal2rna_r2 = {'Cy7':'CD207','Cy5':'ITGAM', 'DAPI':'DAPI'}

if __name__ == '__main__':
    strish_demo = Read_RNAscope(input_path1.joinpath(detection_report_fn), input_path1.joinpath(ref_image_fn))
    convert_unit_micron2pixel(strish_demo, original_width_micron=3869.78, original_height_micron=8858.36)