import random
import time
import os

FIXATION_STIMULI = _fixation_stimuli
FIXATION_DURATION = _fixation_duration
INTER_FIX_DURATION = _inter_fix_duration
STIMULI_DURATION = _stimuli_duration
NUM_TRIALS = _num_trials
INTERTRIAL_INTERVAL = _intertrial_interval
REPLACEMENT = _replacement
STIMULI_GROUPS = []
SCREEN_SELECTION = []
USED_STIMULI = []
BLANK_SCREEN = 'all_black_screen.png'
WHITE_SCREEN = 'all_white_screen.png'

def list_full_paths(directory):
    """Returns absolute paths to all images in given group
        
    Parameters:
        directory: path to a group of images
    """
    return [os.path.join(directory, file) for file in os.listdir(directory)]

def random_image(group_path):
    """Returns path to randomly chosen image in given group
    
    Parameters:
        group_path: path to a group of images
    """
    files = list_full_paths(group_path)
    image = random.choice(files)
    # If replacement is true, do not accept stimuli that have already been used
    if REPLACEMENT:
        # While chosen image exists in USED_STIMULI, choose new one
        while USED_STIMULI.count(image) > 0:
            image = random.choice(files)
        USED_STIMULI.append(image)
    return os.sep.join(os.path.normpath(image).split(os.sep)[-2:])

def assign_groups():
    """Randomly assigns groups given screen selection"""
    left_group = None
    middle_group = None
    right_group = None
    groups = [left_group, middle_group, right_group]
    # Randomly get order of groups on screens
    if all(SCREEN_SELECTION): order = random.sample(range(3), 3)
    else: order = random.sample(range(2), 2)
    k = 0
    for i in range(len(SCREEN_SELECTION)):
        if SCREEN_SELECTION[i]: 
            groups[i] = STIMULI_GROUPS[order[k]]
            k += 1
    return groups

def assign_images(groups):
    """Assigns images to screens"""
    left_image = BLANK_SCREEN
    middle_image = BLANK_SCREEN
    right_image = BLANK_SCREEN
    images = [left_image, middle_image, right_image]
    for i in range(len(SCREEN_SELECTION)):
        if SCREEN_SELECTION[i]: 
            images[i] = random_image(groups[i][0])
    return images

def selection_response(group, vending_machine, experiment_logger):
    """Determines if a group is a 'correct' group"""
    treat_name = group[1]
    tray_num = group[2]
    if group is not None:
        if tray_num != 0:
            vending_machine.dispense_treat(tray_num)
            experiment_logger.info("Tray %d dispenses treat: %s", tray_num, treat_name)
            print("Tray %d dispenses treat: %s" % (tray_num, treat_name))
            return True
    return False


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
        print("Trial %s started" % trial_num)
		
        # Display fixation stimuli
        vending_machine.display_images([BLANK_SCREEN, FIXATION_STIMULI, BLANK_SCREEN])
        experiment_logger.info("Presented fixation cross")
        print("Presented fixation cross")
		
        correct_response = False
		
        # Repeatedly present fixaton cross until correct choice is made
        while not correct_response:
            # Wait for choice on left, middle, or right screens. Timeout if no selection after FIXATION_DURATION
            selection = vending_machine.wait_for_input([vending_machine.left_group, vending_machine.middle_group, vending_machine.right_group], FIXATION_DURATION * 1000)

            if selection == 'middle':
                experiment_logger.info("Trial %s picked middle when selecting fixation cross", trial_num)
                print("Trial %s picked middle when selecting fixation cross" % trial_num)
                correct_response = True
            elif selection == 'left':
                experiment_logger.info("Trial %s picked left when selecting fixation cross", trial_num)
                print("Trial %s picked left when selecting fixation cross" % trial_num)
            elif selection == 'right':
                experiment_logger.info("Trial %s picked right when selecting fixation cross", trial_num)
                print("Trial %s picked right when selecting fixation cross" % trial_num)
            else:
                experiment_logger.info("Trial %s timed out when waiting to select fixation cross", trial_num)
                print("Trial %s timed out when waiting to select fixation cross" % trial_num)

        # Blank out screens
        vending_machine.ssh_all_hosts('xset -display :0 dpms force off')

        #Wait for interval between fixation and stimuli
        experiment_logger.info("Trial %s start of interfixation duration", trial_num)
        print("Trial %s start of interfixation duration" % trial_num)
        time.sleep(INTER_FIX_DURATION)
        experiment_logger.info("Trial %s end of interfixation duration", trial_num)
        print("Trial %s end of interfixation duration" % trial_num)

        correct = False
        #Assign groups to screens and images to groups
        groups = assign_groups()
        images = assign_images(groups)
        # Set which screens should wait for input
        accepted_groups = []
        if SCREEN_SELECTION[0]:
            accepted_groups.append(vending_machine.left_group)
        if SCREEN_SELECTION[1]:
            accepted_groups.append(vending_machine.middle_group)
        if SCREEN_SELECTION[2]:
            accepted_groups.append(vending_machine.right_group)
        # Display random images from each group
        vending_machine.display_images([images[0], images[1], images[2]])
        # Log images displayed
        experiment_logger.info("Trial %s, '%s' stimuli displayed on left", trial_num, images[0])
        experiment_logger.info("Trial %s, '%s' stimuli displayed on middle", trial_num, images[1])
        experiment_logger.info("Trial %s, '%s' stimuli displayed on right", trial_num, images[2])
        print("Trial %s, '%s' stimuli displayed on left" % (trial_num, images[0]))
        print("Trial %s, '%s' stimuli displayed on middle" % (trial_num, images[1]))
        print("Trial %s, '%s' stimuli displayed on right" % (trial_num, images[2]))
        # Wait for input for STIMULI_DURATION
        selection = vending_machine.wait_for_input(accepted_groups, STIMULI_DURATION * 1000)

        # Log selection, and if selection has a corresponding tray, log it's treat and set correct
        if selection == 'timeout':
            experiment_logger.info("Trial %s no selection made.", trial_num)
            print("Trial %s no selection made." % trial_num)
        elif selection == 'left':
            experiment_logger.info("Trial %s picked left", trial_num)
            print("Trial %s picked left", trial_num)
            correct = selection_response(groups[0], vending_machine, experiment_logger)
        elif selection == 'middle':
            experiment_logger.info("Trial %s picked middle", trial_num)
            print("Trial %s picked middle", trial_num)
            correct = selection_response(groups[1], vending_machine, experiment_logger)
        else:
            experiment_logger.info("Trial %s picked right", trial_num)
            print("Trial %s picked right", trial_num)
            correct = selection_response(groups[2], vending_machine, experiment_logger)

        #if correct:
            # FLash LEDS
            # vending_machine.left_group.led_color_with_time(255,255,255,1000)

        experiment_logger.info("Trial %s finished", trial_num)
        print("Trial %s finished" % trial_num)
		
        experiment_logger.info("Start of intertrial interval")
        print("Start of intertrial interval")
		
        # Blank out screens
        vending_machine.ssh_all_hosts('xset -display :0 dpms force off')

        #Clear images
        vending_machine.ssh_all_hosts('pkill feh')

		# Wait for intertrial interval
        time.sleep(INTERTRIAL_INTERVAL)
		
        experiment_logger.info("End of intertrial interval")
        print("End of intertrial interval")

    experiment_logger.info("Experiment finished")
    print("Experiment finished")