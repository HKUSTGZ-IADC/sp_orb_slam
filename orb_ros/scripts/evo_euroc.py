#! /usr/bin/python3

import evo

import argparse
import glob

from pathlib import Path

from evo.tools import file_interface
from evo.core import metrics, sync, trajectory

import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument("--pkg_path", type=str)
args = parser.parse_args()

gt_path = Path(args.pkg_path) / "data/euroc/gt"
data_path = Path(args.pkg_path) / "expr/"


pose_relation = metrics.PoseRelation.translation_part

seqs = ['MH_01_easy', 'MH_02_easy', 'MH_03_medium', 'MH_04_difficult', 'MH_05_difficult',
        'V1_01_easy', 'V1_02_medium', 'V1_03_difficult', 'V2_01_easy', 'V2_02_medium', 'V2_03_difficult']

# for delta in deltas:
# res_final = []
for seq in seqs:
    traj_files = glob.glob(str(data_path / f'{seq}/*.txt'))
    # print(data_path / f'{seq}')
    gt_file = f'{gt_path}/{seq}.csv'

    failure_count = 0
    if not len(traj_files) == 0:
        mean, rmse = [], []
        for traj_file in traj_files:
            traj_gt = file_interface.read_euroc_csv_trajectory(gt_file)
            traj_est = file_interface.read_tum_trajectory_file(traj_file)
            kf_traj_est = file_interface.read_tum_trajectory_file(traj_file)

            traj_gt, traj_est = sync.associate_trajectories(traj_gt, traj_est)
            traj_est_aligned, rot, trans, scale = trajectory.align_trajectory(
                traj_est, traj_gt, correct_scale=True, return_parameters=True)

            data = (traj_gt, traj_est_aligned)
            ape_metric = metrics.APE(pose_relation=pose_relation)

            ape_metric.process_data(data)
            ape_stat = ape_metric.get_all_statistics()
            mean_curr = ape_stat['mean']
            rmse_curr = ape_stat['rmse']
            if mean_curr > 1.0 or rmse_curr > 1.0:
                failure_count += 1
                continue
            mean.append(mean_curr)
            rmse.append(rmse_curr)

        print(
            f'{seq}: mean: {np.mean(mean)}, rmse: {np.mean(rmse)}, #failure {failure_count}')
    else:
        print(f'{seq} empty')
