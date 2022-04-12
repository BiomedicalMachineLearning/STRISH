# Spatial TRanscriptomic In Situ Hybridization (STRISH): 
---

STRISH is a package for detecting cells local coexpression of biomarkers within tissue using highly multiplex image as input. STRISH include quality assessment, preprocessing, cell colocalisation detection.

### 1. Requirements:  

```
pandas>=1.3.2
numpy>=1.19.5
anndata>=0.7.6
Shapely>=1.7.1
Pillow>=8.1.1
opencv-python>=4.5.3.56
simpleitk>=2.1.1
matplotlib>=3.4.3
scikit-image>=0.18.2
scipy>=1.6.3
seaborn>=0.11.2
tifffile>=2021.8.8
setuptools>=52.0.0
[Others as specified in the requirements.txt file]
```
### 2. Installation

```pip install STRISH```

[20220408] version update: v0.2.1

### 3. Test Data

#### <a href="https://zenodo.org/record/4391415#.YlUEX9PP1qs"> BCC/SCC STRISH dataset (Visium Spatial Transcriptomic and RNA-in situ hybridization RNAscope )</a> dataset

## Usage
a. Input data and quality control. 

Read in cell segmentation and measurement. 

```
from STRISH.readwrite import Read_RNAscope
import STRISH.preprocessing as strish_preprocessing


input_path1 = '/path/to/input/directory/')
detection_report_fn = 'cell_detection_measurement.txt'
# optional
ref_image_fn = 'tissue_ref_image.JPEG.jpg'
my_strish_obj = Read_RNAscope(input_path1.joinpath(detection_report_fn), input_path1.joinpath(ref_image_fn))
```

Quality control and data visualisation

```
import STRISH.plotting as strish_plotting

# plot the histogram of gene/protein expression across all the cells
strish_plotting.plot_expression_histogram(my_strish_obj)
# plot the histogram of cell's sizes/areas
strish_plotting.plot_size_shape_histogram(my_strish_obj)


strish_preprocessing.scan_cell_locs_by_window(my_strish_obj, max_cell_per_window=50, init_sub_w=0.5, init_sub_h=0.25)
strish_plotting.plot_tissue_window_contour(my_strish_obj, extend_margin=3)

# (optional) for the strich object which marker's expressions are not converted from flourescene ID to gene/protein name
my_strish_obj.var_names = list(signal2rna_r1.values())

# (optional) filter cells that are either too small or too large from data (more likely to be ) 
strish_preprocessing.preprocess_filter_size_shape(strish_bcc_e15_s1, column= 'Nucleus: Area', lower=0.01,upper=0.95)

# subset the marker of interest or remove the markers that are not used throughout the analysis (DAPI for nuclei should be removed) 
marker_rna = ['CSF1R', 'IL34', 'THY1']
filtered_strish_bcc_e15_s1 = filtered_strish_bcc_e15_s1[:,marker_rna]
```


