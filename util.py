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


def wait_and_log_all(event_logger, duration, clock, b_t, t):
    """
    Wait for `duration` seconds, polling every 1 ms for keypresses,
    and log each press (and its timestamp from `clock`) via trials.addData.

    - duration : float seconds to wait
    - trials   : your current TrialHandler
    - prefix   : column prefix (e.g. 'obs', 'self', or 'any')
    - clock    : a core.Clock() you’ve reset at block or trial start
    """
    start = clock.getTime()
    while clock.getTime() - start < duration:
        presses = event.getKeys(
            keyList=["1", "2", "3", "4", "escape"], timeStamped=clock
        )
        for key, ts in presses:
            # 1) write a row to your separate log
            event_logger.writerow(
                [
                    b_t,  # current block index
                    t,  # current trial index
                    key,
                    f"{ts:.4f}",
                ]
            )
        core.wait(0.001)
