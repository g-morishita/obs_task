import numpy as np
import pandas as pd
import os

def randomize_arm_images(n_blocks, n_choices=3):
    path = "choices/"
    return np.array([os.path.join(path, f"choice{idx}.png") for idx in np.random.choice(54, size=n_choices * n_blocks, replace=True)]).reshape(n_choices, -1).tolist()


def randomize_trial_path(n_blocks):
    candidate = [f"conditions/trial_high_exp_{idx}.csv" for idx in np.arange(n_block // 2)] + [f"conditions/trial_low_exp_{idx}.csv" for idx in np.arange(n_block // 2)]
    return np.random.choice(candidate, size=n_block, replace=False)


if __name__ == "__main__":
    np.random.seed(12345)
    n_block = 2
    if n_block % 2 != 0:
        raise ValueError("n_block must be even because there are two conditions")

    randomized_img_idx = randomize_arm_images(n_block)
    trial_path = randomize_trial_path(n_block)
    # block info for male participants
    male_face_images = ["faces/male/{idx + 1}.png" for idx in range(n_block)]
    block_for_male = {"block": list(range(n_block)), "arm_img_0": randomized_img_idx[0], "arm_img_1": randomized_img_idx[1], "arm_img_2": randomized_img_idx[2], "partner_face_image": male_face_images, "trial_path": trial_path}
    block_for_male = pd.DataFrame(block_for_male)
    block_for_male.to_csv("block_for_male.csv", index=False)


    # block info for male participants
    female_face_images = ["faces/female/{idx + 1}.png" for idx in range(n_block)]
    block_for_female = {"block": list(range(n_block)), "arm_img_0": randomized_img_idx[0], "arm_img_1": randomized_img_idx[1], "arm_img_2": randomized_img_idx[2], "partner_face_image": female_face_images, "trial_path": trial_path}
    block_for_female = pd.DataFrame(block_for_female)
    block_for_female.to_csv("block_for_male.csv", index=False)


    
