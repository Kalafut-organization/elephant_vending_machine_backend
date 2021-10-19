import random
import time
import os

FIXATION_STIMULI = _fixation_stimuli
FIXATION_DURATION = _fixation_duration
INTER_FIXATION_DURATION = _inter_fixation_duration
STIMULI_DURATION = _stimuli_duration
NUM_TRIALS = _num_trials
INTERTRIAL_INTERVAL = _intertrial_interval
REPLACEMENT = _replacement
MONITOR_COUNT = _monitor_count
STIMULI_GROUPS = []
USED_STIMULI = []
BLANK_SCREEN = 'all_black_screen.png'

def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]

def random_image(group_path):
    files = list_full_paths(group_path)
    image = random.choice(files)
    if REPLACEMENT:
        while USED_STIMULI.count(image) > 0:
            image = random.choice(files)
        USED_STIMULI.append(image)
    return os.sep.join(os.path.normpath(image).split(os.sep)[-2:])


def run_experiment(experiment_logger, vending_machine):
    """This is an experiment template to be used by the creation form.
    
    Parameters:
        experiment_logger: Instance of experiment logger for writing logs to csv files
        vending_machine: Instance of vending_machine for interacting with hardware devices
    """

    # Repeat trial for NUM_TRIALS iterations
    for trial_index in range(NUM_TRIALS):
        trial_num = trial_index + 1
        experiment_logger.info("Trial %s started", trial_num)
		
        vending_machine.left_group.display_on_screen(BLANK_SCREEN)
        vending_machine.middle_group.display_on_screen(FIXATION_STIMULI)
        vending_machine.right_group.display_on_screen(BLANK_SCREEN)
        experiment_logger.info("Presented fixation cross")
		
        correct_response = False
		
        while not correct_response:
            # Wait for choice on left, middle, or right screens. Timeout if no selection after FIXATION_DURATION
            selection = vending_machine.wait_for_input(vending_machine, [vending_machine.left_group, vending_machine.middle_group, vending_machine.right_group], FIXATION_DURATION * 1000)

            if selection == 'middle':
                experiment_logger.info("Trial %s picked middle when selecting fixation cross", trial_num)
                correct_response = True
            elif selection == 'left':
                experiment_logger.info("Trial %s picked left when selecting fixation cross", trial_num)
            elif selection == 'right':
                experiment_logger.info("Trial %s picked right when selecting fixation cross", trial_num)
            else:
                experiment_logger.info("Trial %s timed out when waiting to select fixation cross", trial_num)

        # Blank out screens
        vending_machine.left_group.display_on_screen(BLANK_SCREEN)
        vending_machine.middle_group.display_on_screen(BLANK_SCREEN)
        vending_machine.right_group.display_on_screen(BLANK_SCREEN)

        #Wait for interval between fixation and stimuli
        experiment_logger.info("Trial %s start of interfixation duration", trial_num)
        time.sleep(INTER_FIXATION_DURATION)
        experiment_logger.info("Trial %s end of interfixation duration", trial_num)

        if(MONITOR_COUNT == 3):
            # Randomly get order of groups on screens
            order = random.sample(range(3), 3)
            # Assign orders to groups
            left_group = STIMULI_GROUPS[order[0]]
            middle_group = STIMULI_GROUPS[order[1]]
            right_group = STIMULI_GROUPS[order[2]]
            # Get random images from each group
            left_image = random_image(left_group[0])
            middle_image = random_image(middle_group[0])
            right_image = random_image(right_group[0])
            # Display random images from each group
            vending_machine.left_group.display_on_screen(left_image)
            vending_machine.middle_group.display_on_screen(middle_image)
            vending_machine.right_group.display_on_screen(right_image)
            # Log images displayed
            experiment_logger.info("Trial %s, '%s' stimuli displayed on left", trial_num, left_image)
            experiment_logger.info("Trial %s, '%s' stimuli displayed on middle", trial_num, middle_image)
            experiment_logger.info("Trial %s, '%s' stimuli displayed on right", trial_num, right_image)

            # Wait for input for STIMULI_DURATION
            selection = vending_machine.wait_for_input(vending_machine, [vending_machine.left_group, vending_machine.middle_group, vending_machine.right_group], STIMULI_DURATION * 1000)

            if selection == 'timeout':
                experiment_logger.info("Trial %s no selection made.", trial_num)
            elif selection == 'left':
                experiment_logger.info("Trial %s picked left, Tray %d dispenses treat: %s", trial_num, left_group[1], left_group[2])
            elif selection == 'middle':
                experiment_logger.info("Trial %s picked middle, Tray %d dispenses treat: %s", trial_num, middle_group[1], middle_group[2])
            else:
                experiment_logger.info("Trial %s picked right, Tray %d dispenses treat: %s", trial_num, right_group[1], right_group[2])

        else:
            # Randomly get order of groups on screens
            order = random.sample(range(2), 2)
            # Assign orders to groups
            left_group = STIMULI_GROUPS[order[0]]
            right_group = STIMULI_GROUPS[order[1]]
            # Get random images from each group
            left_image = random_image(left_group[0])
            right_image = random_image(right_group[0])
            # Display random images from each group
            vending_machine.left_group.display_on_screen(left_image)
            vending_machine.middle_group.display_on_screen(BLANK_SCREEN)
            vending_machine.right_group.display_on_screen(right_image)
            # Log images displayed
            experiment_logger.info("Trial %s, '%s' stimuli displayed on left", trial_num, left_image)
            experiment_logger.info("Trial %s, '%s' stimuli displayed on right", trial_num, right_image)

            # Wait for input for STIMULI_DURATION
            selection = vending_machine.wait_for_input(vending_machine, [vending_machine.left_group, vending_machine.right_group], STIMULI_DURATION * 1000)

            if selection == 'timeout':
                experiment_logger.info("Trial %s no selection made.", trial_num)
            elif selection == 'left':
                experiment_logger.info("Trial %s picked left, Tray %d dispenses treat: %s", trial_num, left_group[1], left_group[2])
            else:
                experiment_logger.info("Trial %s picked right, Tray %d dispenses treat: %s", trial_num, right_group[1], right_group[2])

        experiment_logger.info("Trial %s finished", trial_num)
		
        experiment_logger.info("Start of intertrial interval")
		
        # Blank out screens
        vending_machine.left_group.display_on_screen(BLANK_SCREEN)
        vending_machine.middle_group.display_on_screen(BLANK_SCREEN)
        vending_machine.right_group.display_on_screen(BLANK_SCREEN)

		# Wait for intertrial interval
        time.sleep(INTERTRIAL_INTERVAL)
		
        experiment_logger.info("End of intertrial interval")

    experiment_logger.info("Experiment finished")