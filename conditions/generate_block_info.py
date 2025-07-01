import os
import sys
import numpy as np
import pandas as pd


def randomize_arm_images(n_blocks, n_choices=3, path="choices"):
    """
    Randomly selects n_choices * n_blocks unique images from the given path
    and returns a nested list of shape (n_choices, n_blocks).
    """
    total_needed = n_choices * n_blocks
    choices = np.random.choice(range(1, 52), size=total_needed, replace=False)
    files = [os.path.join(path, f"choice{i}.png") for i in choices]
    # reshape: each inner list corresponds to one choice across blocks
    return np.array(files).reshape(n_choices, n_blocks).tolist()


def randomize_trial_paths(n_blocks, seed, test=False):
    """
    Builds a candidate list of trial CSV filenames based on condition
    (high/low experience) and picks n_blocks without replacement.
    """
    half = n_blocks // 2
    prefix = "test_trial" if test else "trial"
    # high-exp then low-exp
    candidates = [
        f"conditions/{seed}/{prefix}_high_exp_{i + 1}.csv" for i in range(half)
    ] + [f"conditions/{seed}/{prefix}_low_exp_{i + 1}.csv" for i in range(half)]
    return [f"conditions/{seed}/{prefix}_middle_exp_0.csv"] + np.random.choice(
        candidates, size=n_blocks - 1, replace=False
    ).tolist()


def build_block_df(n_blocks, arm_images, face_gender, trial_paths):
    """
    Constructs a DataFrame for a given gender or test block.
    """
    partner_face_images = [f"faces/{face_gender}/{i+1}.png" for i in range(1, n_blocks)]
    np.random.shuffle(partner_face_images)
    data = {
        "block": list(range(n_blocks)),
        # arm_images is list of lists: [choice0_list, choice1_list, ...]
        **{f"arm_img_{i}": arm_images[i] for i in range(len(arm_images))},
        "partner_face_image": [f"faces/{face_gender}/1.png"] + partner_face_images,
        "trial_path": trial_paths,
    }
    return pd.DataFrame(data)


def save_blocks(n_blocks, seed):
    np.random.seed(seed)

    n_blocks = n_blocks + 1  # Add a practice block

    # 1) Randomize arm images and trial paths
    arm_images = randomize_arm_images(n_blocks)
    trial_paths = randomize_trial_paths(n_blocks, seed)

    # 2) Generate and save male/female blocks
    for gender in ("male", "female"):
        df = build_block_df(n_blocks, arm_images, gender, trial_paths)
        save_path = f"{seed}/"
        os.makedirs(save_path, exist_ok=True)
        filename = f"{seed}/block_for_{gender}.csv"
        df.to_csv(filename, index=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python block_generator.py <seed> [n_blocks]")
        sys.exit(1)

    seed = int(sys.argv[1])
    n_blocks = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    if n_blocks % 2 != 0:
        raise ValueError("n_blocks must be even because there are two conditions")

    save_blocks(n_blocks, seed)
