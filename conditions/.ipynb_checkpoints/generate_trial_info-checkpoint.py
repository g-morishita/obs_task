import numpy as np
import pandas as pd
from scipy.special import softmax


class q_learning:
    def __init__(self, alpha, beta, init_q):
        if (alpha < 0) or (alpha > 1):
            raise ValueError(f"alpha is invalid {alpha}")
        self.alpha = alpha

        if beta < 0:
            raise ValueError(f"beta is invalid {beta}")
        self.beta = beta
 
        self.init_q = np.array(init_q).copy()
        self.q = np.array(init_q)

    def reset(self):
        self.q = self.init_q.copy()

    def learn(self, c, r):
        self.q[c] = self.q[c] + self.alpha * (r - self.q[c])

    def make_choice(self):
        p = softmax(self.beta * self.q)
        c = np.random.choice(len(self.q), p=p)
        return c


def create_choice_reward_history(model, n_trials):
    choices = []
    rewards = []
    model.reset()
    for t in range(n_trials):
        c = model.make_choice()
        r = int(np.random.uniform() < reward_probs[c]) # Implicitly assume index-reward relationship (0 <-> .25, 1 <-> .5, 2 <-> .75)
        model.learn(c, r)
        
        # Save history
        choices.append(c)
        rewards.append(r)

    return choices, rewards


def create_randomized_order(n_trials):
    return [','.join(np.random.choice(np.arange(3), size=3, replace=False).astype(str).tolist()) for _ in range(n_trials)]


def main():
    # create partner history 
    for b in range(n_blocks):
        # partner is low-explorative
        choices, rewards = create_choice_reward_history(low_explorative, n_trials)
        obs_random_order = create_randomized_order(n_trials)
        self_random_order = create_randomized_order(n_trials)
        trial_for_low_exp = {"trial": np.arange(n_trials), "partner_choice": choices, "partner_rewards": rewards, "obs_randomized_img_order": obs_random_order, "self_randomized_img_order": self_random_order}
        trial_for_low_exp = pd.DataFrame(trial_for_low_exp)
        trial_for_low_exp.to_csv(f"trial_low_exp_{b}.csv", index=False)

        # partner is high-explorative
        choices, rewards = create_choice_reward_history(high_explorative, n_trials)
        obs_random_order = create_randomized_order(n_trials)
        self_random_order = create_randomized_order(n_trials)
        trial_for_low_exp = {"trial": np.arange(n_trials), "partner_choice": choices, "partner_rewards": rewards, "obs_randomized_img_order": obs_random_order, "self_randomized_img_order": self_random_order}
        trial_for_low_exp = pd.DataFrame(trial_for_low_exp)
        trial_for_low_exp.to_csv(f"trial_high_exp_{b}.csv", index=False)

# Setting
seed = 12345
n_blocks = 2
n_trials = 30
reward_probs = [.25, .5, .75]
init_q = [.5, .5, .5]
alpha = .3
high_exp = 1.5
low_exp = 20.0
low_explorative = q_learning(alpha, low_exp, init_q)
high_explorative = q_learning(alpha, high_exp, init_q)

if __name__ == "__main__":
    np.random.seed(seed)
    main()