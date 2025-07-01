import numpy as np
from psychopy import visual, event, core


def make_iti_duration(a=2.0, b=8.0, n_trials=30):
    itis = np.linspace(a, b, n_trials)  # M evenly-spaced values
    np.random.shuffle(itis)  # shuffle
    return itis


def draw_all(visuals):
    for v in visuals:
        v.draw()


def before_block_page(win, text):
    pause_text = visual.TextStim(
        win,
        text=text,
        color="white",
        height=0.05,
    )
    pause_text.draw()
    win.flip()

    # wait for 9 or escape
    keys = event.waitKeys(keyList=["9", "escape"])

    if "escape" in keys:
        core.quit()

    if "9" in keys:
        pause_text = visual.TextStim(
            win,
            text="Ready",
            color="white",
            height=0.05,
        )
        pause_text.draw()
        win.flip()

        # wait for 5 or escape
        keys = event.waitKeys(keyList=["5", "escape"])
        if "escape" in keys:
            core.quit()


def collect_response(
    duration, trials, clock, choice_keys=("1", "2", "3", "4", "escape")
):
    """
    For up to `duration` seconds:
      • poll *all* keys every frame
      • log each press (key & timestamp) into `trials` under
          prefix + '_all_keys'  (comma-separated)
          prefix + '_all_times' (comma-separated)
      • as soon as a choice_key is hit, record it + RT (only once)
    Returns (choice_key or None, choice_rt or None).
    """
    # clear buffer, prep containers
    event.clearEvents()
    all_keys, all_times = [], []
    choice = None
    rt = None
    start = clock.getTime()

    while clock.getTime() - start < duration:
        presses = event.getKeys(timeStamped=clock)
        for key, ts in presses:
            all_keys.append(key)
            all_times.append(ts)
            # first time we see a choice key, store it
            if choice is None and key in choice_keys:
                choice = key
                rt = ts
                # if you want to stop as soon as they choose, uncomment:
                break
        core.wait(0.001)

    # 1) log *all* keys & times as comma-lists
    trials.addData(f"all_keys", "-".join(all_keys) if all_keys else "")
    trials.addData(
        f"all_times",
        "-".join(f"{t:.4f}" for t in all_times) if all_times else "",
    )

    return choice, rt
