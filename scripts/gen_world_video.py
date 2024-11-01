"""
gen_video.py

This script generates a video file from data stored in a specified experiment directory. 
It uses an ExpReader object to read the data.

Author: Nimesh Nagururu
"""

from argparse import ArgumentParser
from pathlib import Path
from collections import OrderedDict
from natsort import natsorted
import numpy as np
import pandas as pd
from exp_reader import ExpReader 
import cv2
import os
import logging

def gen_video(exp_dir):
    """
    Generate a video file from data stored in the specified experiment directory.

    Args:
        exp_dir (Path): Path to the experiment directory. Expects Path object.

    Returns:
        None
    """
    if (exp_dir / '000').exists():
        output_vid_f = exp_dir / ('000/' + 'world.mp4')
        output_timestamps_f = exp_dir / ('000/' +'world_timestamps.npy')
    else:
        output_vid_f = exp_dir / 'world.mp4'
        output_timestamps_f = exp_dir / 'world_timestamps.npy'
    
    reader = ExpReader(exp_dir, verbose = True, ignore_keys = ['depth', 'r_img', 'segm'])
    od = reader._data

    world_timestamps = od['data']['time']
    l_imgs = od['data']['l_img']

    # Recording frame rate
    frate = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(str(output_vid_f), fourcc, frate, (l_imgs[0].shape[1], l_imgs[0].shape[0]))

    time_diffs = np.diff(world_timestamps)
    frames_per_timestamp = (time_diffs * frate).round().astype(int)  # Calculate number of frames to replicate

    upsampled_images = []
    upsampled_timestamps = []

    current_timestamp = world_timestamps[0]
    for i in range(len(time_diffs)):
        for _ in range(frames_per_timestamp[i]):
            upsampled_images.append(l_imgs[i])
        interval_timestamps = np.linspace(current_timestamp, 
                                        current_timestamp + time_diffs[i], 
                                        frames_per_timestamp[i], 
                                        endpoint=False)
        upsampled_timestamps.extend(interval_timestamps)
        current_timestamp += time_diffs[i]

    for img in upsampled_images:
        video.write(img)

    video.release()

    np.save(output_timestamps_f, np.array(upsampled_timestamps))

# For iterating through all folders in the directory and extracting video
def main():
    parser = ArgumentParser()
    parser.add_argument("--exp_csv", 
                        action="store", 
                        dest="exp_csv", 
                        help="Specify experiments directory", 
                        default='/Users/orenw/Documents/tb_skills_analysis/data/SDF_UserStudy_Data/exp_dirs_DONOTOVERWRITE.csv')
    
    args = parser.parse_args()
    csv = pd.read_csv(args.exp_csv)

    exp = list(csv['exp_dir'])
    
    for e in exp:
        e = Path(e)
        # Check if both '000/world.mp4' and 'world.mp4' don't exist
        if not e.exists():
            logging.warning(f"{e} doesn't exist. Skipping...")
            continue
        
        elif (e / '000/world.mp4').exists() or (e / 'world.mp4').exists():
            logging.warning(f"'000/world.mp4' and/or 'world.mp4' already exist in directory {e}. Skipping...")
            continue

        # If files exist, call the gen_video function
        gen_video(Path(e))

"""
# For generating video only for one specific trial
def main():
    
    gen_video(Path('/Users/orenw/Documents/tb_skills_analysis/data/SDF_UserStudy_Data/Participant_10/2023-02-10 10:23:22_anatT_baseline_P10T1'))

"""   

if __name__ == "__main__":
	main()