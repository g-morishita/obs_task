import os

import numpy as np
import pandas as pd
from scipy.special import softmax


class q_learning:
    def __init__(self, alpha, beta, init_q):
        if not 0 <= alpha <= 1:
            raise ValueError(f"alpha is invalid {alpha}")
        if beta < 0:
            raise ValueError(f"beta is invalid {beta}")
        self.alpha = alpha
        self.beta = beta
        self.init_q = np.array(init_q, copy=True)
        self.q = np.array(init_q, copy=True)

    def reset(self):
        self.q = self.init_q.copy()

    def learn(self, c, r):
        self.q[c] += self.alpha * (r - self.q[c])

    def make_choice(self):
        p = softmax(self.beta * self.q)
        return np.random.choice(len(self.q), p=p)


def create_choice_reward_history(model, n_trials, reward_probs):
    while True:
        choices, rewards = [], []
        model.reset()
        for _ in range(n_trials):
            c = model.make_choice()
            r = int(np.random.rand() < reward_probs[c])
            model.learn(c, r)
            choices.append(c)
            rewards.append(r)

        # If there's any option that the partner has never chosen
        # Get back to the loop.
        if len(np.unique(choices)) == 3:
            break
    return choices, rewards


def create_randomized_order(n_trials, n_options=3):
    orders = []
    for _ in range(n_trials):
        perm = np.random.permutation(n_options)
        orders.append("-".join(map(str, perm)))
    return orders


def save_block(model, prefix, n_trials, block_idx, seed, reward_probs):
    """Simulate one block and write out a CSV with the given prefix."""
    choices, rewards = create_choice_reward_history(model, n_trials, reward_probs)
    obs_order = create_randomized_order(n_trials)
    self_order = create_randomized_order(n_trials)
    df = pd.DataFrame(
        {
            "trial": np.arange(n_trials),
            "partner_choice": choices,
            "partner_reward": rewards,
            "obs_randomized_img_order": obs_order,
            "self_randomized_img_order": self_order,
        }
    )
    save_path = f"{seed}/"
    os.makedirs(save_path, exist_ok=True)
    filename = os.path.join(save_path, f"{prefix}_{block_idx}.csv")
    df.to_csv(filename, index=False)


def main(seed):
    np.random.seed(seed)

    # practice blocks
    save_block(
        middle_explorative, "trial_middle_exp", practice_n_trials, 0, seed, reward_probs
    )

    for b in range(1, n_blocks // 2 + 1):
        # main blocks
        save_block(low_explorative, "trial_low_exp", n_trials, b, seed, reward_probs)
        save_block(high_explorative, "trial_high_exp", n_trials, b, seed, reward_probs)


# Settings
n_trials = 30
practice_n_trials = 10
reward_probs = [0.25, 0.5, 0.75]
init_q = [0.5, 0.5, 0.5]
alpha = 0.3
high_exp_beta = 1.5
middle_exp_beta = 7
low_exp_beta = 20.0

low_explorative = q_learning(alpha, low_exp_beta, init_q)
high_explorative = q_learning(alpha, high_exp_beta, init_q)
middle_explorative = q_learning(alpha, middle_exp_beta, init_q)

if __name__ == "__main__":
    import sys

    n_blocks = int(sys.argv[2])
    main(int(sys.argv[1]))
