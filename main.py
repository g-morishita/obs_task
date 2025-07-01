import pandas as pd
from psychopy import visual, core, gui, data, event
from psychopy.hardware import keyboard
import os
import time
from window_setting import WINDOW_SIZE, FULLSCREEN, DEBUG
from util import make_iti_duration, draw_all, before_block_page
from stimuli_setting import *

SAVE_BASE_FOLDER = "data"

# ───────────────────────── 1. PRE-EXPERIMENT DIALOG ────────────────────────────
# register escape to quit immediately
kb = keyboard.Keyboard()


while True:
    dlg = gui.Dlg(title="OL Task")
    dlg.addField("Participant ID:", "P001")
    dlg.addField("Male Face Images", True)
    dlg.show()
    if not dlg.OK:
        core.quit()
    participant = dlg.data[0]
    gender = "male" if dlg.data[1] else "female"

    # Check condition files are created.
    condition_path = f"conditions/{participant}"
    if os.path.exists(condition_path):
        break
    else:
        warning_dlg = gui.Dlg(title="Warning")
        warning_dlg.addText("It looks like condition files have not been created.")
        warning_dlg.show()

# Check condition files are correctly created.
trial_file = os.path.join(condition_path, f"trial_middle_exp_0.csv")
if not os.path.exists(trial_file):
    warning_dlg = gui.Dlg(title="Warning")
    warning_dlg.addText(
        "It looks like condition files have not been created. Click cancel to finish"
    )
    warning_dlg.show()
    if not warning_dlg.OK:
        core.quit()

    trial_info = pd.read_csv(trial_file)
    if not DEBUG and len(trial_info) != 10:
        warning_dlg = gui.Dlg(title="Warning")
        warning_dlg.addText(f"{trial_file} does not have 10 trials.")
        warning_dlg.show()
        if not warning_dlg.OK:
            core.quit()

for b in range(1, 3):
    for exp in ["high", "low"]:
        trial_file = os.path.join(condition_path, f"trial_{exp}_exp_{b}.csv")
        if not os.path.exists(trial_file):
            warning_dlg = gui.Dlg(title="Warning")
            warning_dlg.addText(
                "It looks like condition files have not been created. Click cancel to finish"
            )
            warning_dlg.show()
            if not warning_dlg.OK:
                core.quit()

        trial_info = pd.read_csv(trial_file)
        if not DEBUG and len(trial_info) != 30:
            warning_dlg = gui.Dlg(title="Warning")
            warning_dlg.addText(f"{trial_file} does not have 30 trials.")
            warning_dlg.show()
            if not warning_dlg.OK:
                core.quit()

# make sure save directory exists
save_path = os.path.join(SAVE_BASE_FOLDER, participant)
os.makedirs(save_path, exist_ok=True)
timestamp = time.strftime("%Y%m%d-%H%M%S")
main_exp_block_path = os.path.join(condition_path, f"block_for_{gender}.csv")


# ───────────────────────── 3. SET UP WINDOW & BASIC STIMULI ──────────────────────────
# create a window
win = visual.Window(size=(1000, 700), units="height", fullscr=FULLSCREEN)

# Create a fixation
fixation = visual.TextStim(win, text="+", color="white", height=0.1)

# import block information from csv file
blocks = data.TrialHandler(
    nReps=1, method="sequential", trialList=data.importConditions(main_exp_block_path)
)

# ───────────────────────── 4. EXPERIMENT  ──────────────────────────
before_block_page(win, DEBUG)

# create a clock for block‐relative timing
blockClock = core.Clock()

for b in blocks:
    # ───────────────────────── 4.a SET UP BLOCK ──────────────────────────
    # Make stimuli
    stimuli = [
        visual.ImageStim(
            win,
            image=b[f"arm_img_{stim_idx}"],  # can be .png, .jpg, etc.
            pos=(0, 0),  # center of screen
            size=STIM_SIZE,  # in “norm” units by default
        )
        for stim_idx in range(3)
    ]

    # sample ITI, ISI
    itis = make_iti_duration()
    isis = make_iti_duration()

    # Make trials
    trial_path = b["trial_path"]
    trials = data.TrialHandler(
        nReps=1, method="sequential", trialList=data.importConditions(trial_path)
    )

    # ─── reset at block start ───
    blockClock.reset()

    for trial in trials:
        # ───────────────────────── Other Decision phase ──────────────────────────
        ################# 1. fixation ################
        fixation.draw()
        win.flip()
        t_other_fix_on = blockClock.getTime()
        trials.addData("t_other_fix_on", t_other_fix_on)
        if DEBUG:
            core.wait(1.0)
        else:
            core.wait(itis[trials.thisN])

        ################# 2. shuffle the order of stimuli ################
        # parse your CSV field into a list of ints
        order = [int(x) for x in trial["obs_randomized_img_order"].split(",")]
        # e.g. "2,0,1" → [2, 0, 1]
        # This list means the 0th stimulus goes to the 3rd slot (the rightmost),
        # the 1st stimulus goes to 0th slot (the leftmost),
        # and the 2nd stimulus goes to 1st slot (the middle).

        # example order = [2, 0, 1]
        inverse_order = [None] * len(order)
        for stim_idx, slot_idx in enumerate(order):
            inverse_order[slot_idx] = stim_idx
        # now inverse_order == [1, 2, 0]
        # meaning slot 0 → stim 1, slot 1 → stim 2, slot 2 → stim 0

        # now place each stim in its designated slot
        for stim_idx, slot_idx in enumerate(order):
            stimuli[stim_idx].pos = STIM_SLOT_POSITIONS[slot_idx]

        ################ 3. face ################
        face = visual.ImageStim(
            win,
            image=b["partner_face_image"],  # can be .png, .jpg, etc.
            pos=FACE_SLOT_POSITION,  # center of screen
            size=FACE_SIZE,  # in “norm” units by default
        )

        # 3. draw & display
        draw_all(stimuli + [face])
        win.flip()
        t_other_options = blockClock.getTime()
        trials.addData("t_other_options", t_other_options)
        if DEBUG:
            core.wait(1.0)
        else:
            core.wait(OTHER_OPTION_DURATION)

        ################ 4. highlight other choice ################
        # — collect partner_choice and highlight —
        choice_idx = int(trial["partner_choice"])
        chosen = stimuli[choice_idx]

        # build a Rect that’s slightly bigger than the image
        frame = visual.Rect(
            win,
            width=chosen.size[0] + HIGHLIGHT_CHOSEN_GAP,
            height=chosen.size[1] + HIGHLIGHT_CHOSEN_GAP,
            pos=chosen.pos,
            lineColor="white",
            fillColor=None,
            lineWidth=HIGHLIGHT_LINE_WIDTH,
        )
        draw_all(stimuli + [face] + [frame])
        # hold for a bit so the participant can see it
        win.flip()
        t_other_choice = blockClock.getTime()
        trials.addData("t_other_choice", t_other_choice)
        if DEBUG:
            core.wait(1.0)
        else:
            core.wait(OTHER_CHOICE_DURATION)

        ################# 5. display outcomes ################
        is_rewarded = int(trial["partner_reward"])
        image_path = (
            "outcomes/reward.png" if is_rewarded == 1 else "outcomes/no_reward.png"
        )
        outcome = visual.ImageStim(
            win,
            image=image_path,  # can be .png, .jpg, etc.
            pos=OUTCOME_SLOT_POSITION,  # center of screen
            size=OUTCOME_SIZE,  # in “norm” units by default
        )
        draw_all(stimuli + [face] + [frame] + [outcome])
        # hold for a bit so the participant can see it
        win.flip()
        t_other_outcome = blockClock.getTime()
        trials.addData("t_other_outcome", t_other_outcome)
        if DEBUG:
            core.wait(1.0)
        else:
            core.wait(OTHER_HIGHLIGHT_DURATION)

        # ───────────────────────── Self Decision phase ──────────────────────────
        # initialize all self‐choice fields with blanks or a MISS code
        trials.addData("t_self_choice_on", "")
        trials.addData("self_choice", "")
        trials.addData("t_self_highlight_on", "")

        ################# 1. fixation ################
        fixation.draw()
        win.flip()
        t_self_fix_on = blockClock.getTime()
        trials.addData("self_fix_on", t_self_fix_on)
        if DEBUG:
            core.wait(1.0)
        else:
            core.wait(isis[trials.thisN])

        ################# 2. shuffle the order of stimuli ################
        # parse your CSV field into a list of ints
        order = [int(x) for x in trial["self_randomized_img_order"].split(",")]
        # e.g. "0,2,1" → [0, 2, 1]

        # now place each stim in its designated slot
        for stim_idx, slot_idx in enumerate(order):
            stimuli[stim_idx].pos = STIM_SLOT_POSITIONS[slot_idx]

        ################# 3. draw stimuli ################
        face = visual.ImageStim(
            win,
            image="faces/your_face.png",  # can be .png, .jpg, etc.
            pos=FACE_SLOT_POSITION,  # center of screen
            size=FACE_SIZE,  # in “norm” units by default
        )
        draw_all(stimuli + [face])
        win.flip()
        t_self_options_on = blockClock.getTime()
        trials.addData("t_self_options_on", t_self_options_on)

        ################# 3. response  ################
        keys = event.waitKeys(
            maxWait=MAX_WAIT_SELF_CHOICE, keyList=["1", "2", "3", "escape"]
        )

        if keys:
            if "escape" in keys:
                core.quit()

            ################ 4. highlight other choice ################
            # — collect partner_choice and highlight —
            choice_position_idx = int(keys[0]) - 1
            self_stim_idx = inverse_order[choice_position_idx]
            self_chosen = stimuli[self_stim_idx]

            t_self_choice_on = blockClock.getTime()
            trials.addData("t_self_choice_on", t_self_choice_on)
            trials.addData("self_choice", int(self_stim_idx))

            # build a Rect that’s slightly bigger than the image
            frame = visual.Rect(
                win,
                width=self_chosen.size[0] + HIGHLIGHT_CHOSEN_GAP,
                height=self_chosen.size[1] + HIGHLIGHT_CHOSEN_GAP,
                pos=self_chosen.pos,
                lineColor="white",
                fillColor=None,
                lineWidth=HIGHLIGHT_LINE_WIDTH,
            )

            draw_all(stimuli + [face] + [frame])
            #  hold for a bit so the participant can see it
            win.flip()
            t_self_highlight_on = blockClock.getTime()
            trials.addData("self_highlight_on", t_self_highlight_on)
            if DEBUG:
                core.wait(1.0)
            else:
                core.wait(SELF_HIGHLIGHT_DURATION)

        # Every trial, data will be saved just in case the experiment stops halfway.
        trials.saveAsWideText(
            os.path.join(save_path, f"{timestamp}_{blocks.thisN}"), delim="\t"
        )

    # wait for 5 to move on to the next block or exec to quit esc
    trials.saveAsWideText(
        os.path.join(save_path, f"{timestamp}_{blocks.thisN}.csv"), delim="\t"
    )
    before_block_page(win, DEBUG, text="completed")

# 5. Clean up
win.close()
core.quit()
