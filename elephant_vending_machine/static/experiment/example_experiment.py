import random

def run_experiment(experiment_logger, vending_machine):
    """This is an example of an experiment file used to create custom experiments.

    In this experiment, a fixation cross is presented on the center display and the other two displays randomly
    display either a white, or a black stimuli. The correct response is to select the white stimuli. The LEDs flash
    green if the correct choice was made.
    
    Parameters:
        experiment_logger: Instance of experiment logger for writing logs to csv files
        vending_machine: Instance of vending_machine for interacting with hardware devices
    """

    NUM_TRIALS = 20
    BLANK_SCREEN = 'all_black_screen.png'
    FIXATION_STIMULI = 'fixation_stimuli.png'
    WHITE_STIMULI = 'white_stimuli.png'
    BLACK_STIMULI = 'black_stimuli.png'

    vending_machine.left_group.display_on_screen(BLANK_SCREEN, False)
    vending_machine.middle_group.display_on_screen(FIXATION_STIMULI, False)
    vending_machine.right_group.display_on_screen(BLANK_SCREEN, False)
    experiment_logger.info("Presented fixation cross")

    # Repeat trial for NUM_TRIALS iterations
    for trial_index in range(NUM_TRIALS):
        trial_num = trial_index + 1
        experiment_logger.info("Trial %s started", trial_num)

        # Randomly decide to display white stimuli on left or right display
        white_on_left = random.choice([True, False])

        if white_on_left:
            vending_machine.left_group.display_on_screen(WHITE_STIMULI, True)
            vending_machine.right_group.display_on_screen(BLACK_STIMULI, False)
            experiment_logger.info("Trial %s correct stimuli displayed on left", trial_num)
        else:
            vending_machine.left_group.display_on_screen(BLACK_STIMULI, False)
            vending_machine.right_group.display_on_screen(WHITE_STIMULI, True)
            experiment_logger.info("Trial %s correct stimuli displayed on right", trial_num)

        # Wait for choice on left or right screen. If no selection after 5 minutes (300000 milliseconds)
        selection = vending_machine.wait_for_selection(vending_machine.left_group, vending_machine.right_group, timeout=300000)

        if selection == 'left':
            experiment_logger.info("Trial %s picked left", trial_num)
        else:
            experiment_logger.info("Trial %s picked right", trial_num)

        experiment_logger.info("Trial %s finished", trial_num)

    experiment_logger.info("Experiment finished")
