import random
import time

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
    INTERTRIAL_INTERVAL = 5 # seconds
    BLANK_SCREEN = 'all_black_screen.png'
    FIXATION_STIMULI = 'fixation_stimuli.png'
    WHITE_STIMULI = 'white_stimuli.png'
    BLACK_STIMULI = 'black_stimuli.png'

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
            # Wait for choice on left, middle, or right screens. Timeout if no selection after 5 minutes (300000 milliseconds)
            selection = vending_machine.wait_for_input([vending_machine.left_group, vending_machine.middle_group, vending_machine.right_group], 30000)

            if selection == 'middle':
                experiment_logger.info("Trial %s picked middle when selecting fixation cross", trial_num)
                # Flash middle screen LEDs green for 3 seconds (3000 milliseconds)
                vending_machine.middle_group.led_color_with_time(0, 255, 0, 3000)
                correct_response = True
            elif selection == 'left':
                experiment_logger.info("Trial %s picked left when selecting fixation cross", trial_num)
            elif selection == 'right':
                experiment_logger.info("Trial %s picked right when selecting fixation cross", trial_num)
            else:
                experiment_logger.info("Trial %s timed out when waiting to select fixation cross", trial_num)

        # Randomly decide to display white stimuli on left or right display
        white_on_left = random.choice([True, False])

        if white_on_left:
            vending_machine.left_group.display_on_screen(WHITE_STIMULI)
            vending_machine.middle_group.display_on_screen(FIXATION_STIMULI)
            vending_machine.right_group.display_on_screen(BLACK_STIMULI)
            experiment_logger.info("Trial %s correct stimuli displayed on left", trial_num)
        else:
            vending_machine.left_group.display_on_screen(BLACK_STIMULI)
            vending_machine.middle_group.display_on_screen(FIXATION_STIMULI)
            vending_machine.right_group.display_on_screen(WHITE_STIMULI)
            experiment_logger.info("Trial %s correct stimuli displayed on right", trial_num)

        selection = vending_machine.wait_for_input([vending_machine.left_group, vending_machine.right_group], 300000)

        if selection == 'timeout':
            experiment_logger.info("Trial %s no selection made.", trial_num)
        elif selection == 'left':
            experiment_logger.info("Trial %s picked left", trial_num)
        else:
            experiment_logger.info("Trial %s picked right", trial_num)

        experiment_logger.info("Trial %s finished", trial_num)
		
        experiment_logger.info("Start of intertrial interval")
		
		# Wait for intertrial interval
        time.sleep(INTERTRIAL_INTERVAL)
		
        experiment_logger.info("End of intertrial interval")

    experiment_logger.info("Experiment finished")