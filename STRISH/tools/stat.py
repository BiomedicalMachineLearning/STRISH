from ..utils import *
import re
from ..core import STRISH_Obj
import logging
import pandas as pd


def pairs(list_combine):
    """
    Create random ligand-receptor pairs from the list of markers exists
    """
    perm_pairs = list()
    for i in range(len(list_combine)):
        for j in range(i + 1, len(list_combine)):
            perm_pairs.append(re.sub('\+', '', list_combine[i]) + '_' + re.sub('\+', '', list_combine[j]))

    return perm_pairs

def colocalised_count(df, group_col = 'Colocal_window',list_col='cell_type'):
    keys, values = df[[group_col,list_col]].sort_values(group_col).values.T
    ukeys, index = np.unique(keys, True)
    arrays = np.split(values, index[1:])
    col_value = dict()
    for col in np.unique(df[list_col]):
        col_value[col] =list()
        for item in arrays:
            count = (item==col).sum()
            col_value[col].append(count)
#     df2 = pd.DataFrame({group_col:ukeys, list_col:[list(a) for a in arrays]})
    df2 = pd.DataFrame(col_value,index=ukeys)
    return df2


def assign_cells2windows(strish_obj1: STRISH_Obj, strish_obj2: STRISH_Obj):
    if 'Colocal_window' not in list(strish_obj1.obs.columns):
        logging.exception(
            f'Colocal_window does not exist in strish_obj1. Can not assess the positive windows')
        Exception('Please run scan_cell_locs_by_window')
    if 'Colocal_window' not in list(strish_obj2.obs.columns):
        logging.exception(
            f'Colocal_window does not exist in strish_obj2. Can not assess the positive windows')
        Exception('Please run scan_cell_locs_by_window')
    tmp_df = strish_obj1.obs[~strish_obj1.obs['Colocal_window'].isnull()]

    all_windows_obj1 = colocalised_count(tmp_df)
    for col_window_loc in all_windows_obj1.index.values:
        x0, y0, x1, y1 = [int(i) for i in col_window_loc.split(',')]
        tmp = strish_obj2.obs[(x0 < strish_obj2.obs['X_px']) &
                                     (strish_obj2.obs['X_px'] < x1) &
                                     (y0 < strish_obj2.obs['Y_px']) &
                                     (strish_obj2.obs['Y_px'] < y1)]
        strish_obj2.obs.loc[tmp.index.values, 'Colocal_window'] = col_window_loc
    tmp_df2 = strish_obj2.obs[~strish_obj2.obs['Colocal_window'].isnull()]

    all_windows_obj2 = colocalised_count(tmp_df2)
    all_windows_t1 = all_windows_obj1.drop(columns='Unidentified')
    all_windows_t2 = all_windows_obj2.drop(columns='Unidentified')
    merge_window_cell_count = pd.concat([all_windows_t1, all_windows_t2], axis=1)
    merge_window_cell_count.fillna(0, inplace=True)
    return merge_window_cell_count

def count_window_ligand_receptor_score(merge_count_window:pd.DataFrame):
    lr_cols = pairs(merge_count_window.columns)
    # print(len(lr_cols))
    # lr_cols
    scores = pd.DataFrame(index=merge_count_window.index.values, columns=lr_cols)
    for col in scores:
        sender, receiver = col.split('_')
        sender += '+'
        receiver += '+'
        scores[col] = (merge_count_window[sender] + merge_count_window[receiver]) / merge_count_window.sum(axis=1)
        scores[col][merge_count_window[sender] == 0] = 0
        scores[col][merge_count_window[receiver] == 0] = 0
    #     scores[col][merge_count_values[receiver] == 0] = 0
    #     print(sender, receiver)
    scores.reset_index(inplace=True)

# target_lr = 'CSF1R_IL34'
# background_table = scores.drop(columns=target_lr)
# all_obs_windows = scores[[target_lr]].values
# scores['p95_'+target_lr] = 0.0
# for index, row in background_table.iterrows():
#     background_windows_row = row[1:].values
#     single_total = list(all_obs_windows) + list(background_windows_row)
#     p_value = sum(single_total >= scores.loc[index,target_lr])/len(single_total)
#     if p_value == 0:
#         print(row)
#     scores.loc[index,'p95_'+target_lr] =  p_value
#     scores.loc[index,'log10p_'+target_lr] =  -np.log10(p_value)


def lr_significant_test(count_lr_df: pd.DataFrame, target_lr_pair: str):
    # target_lr = 'CSF1R_IL34'
    background_table = count_lr_df.drop(columns=target_lr_pair)
    # extract the lr_score of all the windows that have positive mean of co-localization of target_lr_pair
    all_obs_windows = count_lr_df[[target_lr_pair]].values
    count_lr_df['p95_'+target_lr_pair] = 0.0
    for index, row in background_table.iterrows():
        # cumulative of randomized pair of ligand-receptor within the same window in count_lr_df
        background_windows_row = row[1:].values
        single_total = list(all_obs_windows) + list(background_windows_row)
        p_value = sum(single_total >= count_lr_df.loc[index,target_lr_pair])/len(single_total)
        count_lr_df.loc[index,'p95_'+target_lr_pair] = p_value
        count_lr_df.loc[index,'log10p_'+target_lr_pair] = -np.log10(p_value)
    return count_lr_df

