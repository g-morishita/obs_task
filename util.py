import numpy as np
from psychopy import visual, event, core


def make_iti_duration(a=2.0, b=8.0, n_trials=30):
    itis = np.linspace(a, b, n_trials)  # M evenly-spaced values
    np.random.shuffle(itis)  # shuffle
    return itis


def draw_all(visuals):
    for v in visuals:
        v.draw()


def before_block_page(win, debug, text="Ready"):
    pause_text = visual.TextStim(
        win,
        text=text,
        color="white",
        height=0.05,
    )
    pause_text.draw()
    win.flip()

    # wait for 5 or escape
    keys = event.waitKeys(keyList=["5", "escape"])
    if ("escape" in keys) and debug:
        core.quit()
