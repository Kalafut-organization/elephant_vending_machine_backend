Current Issues & Improvement Suggestions
==============
The AU21 CSE team focused on receiving inputs from the GPIO buttons and outputting to the treat dispenser,
connecting the devices so that they worked together. In the UI, we also added in image grouping and an experiment
template option. While we were able to finish our UI tasks, due to time constraints the connections between the 
software and GPIO inputs could not be optimized. 

The SP22 CSE team dedicated a majority of project time on troubleshooting hardware-software interfacing issues,
as well as implementing LED strip functionality. We were responsible for restoring previous experimental functionality
from the previous semester, which had depreciated due to code updates and changing requirements/materials from the
leading Mechanical Engineering Team. We worked with the ME team to replace and troubleshoot faulty components, and provided
technical consult for device operating conditions and improvements.


Although we were able to restore most of the functionality, we faced numerous recurring problems.
Below are some of the issues faced by both previous CSE teams and suggestions on improving them.

Image Display Optimization Issues
#############
AU21:
When an experiment is running, the webserver pi sends the images to be displayed to the three monitor pi's via SSH. 
These monitor pi's then use the feh library to display these images. Currently there is a delay of about 5-7 seconds 
between the fixation image button being selected and basic black/white images being displayed on the outer screens. 
Also, these images do not display at the same time on both monitors inconsistently - typically the left pi is faster, 
regardless of if it displays the basic white or black stimuli. Having the images display when they are ready results 
in this issue of not displaying at the same time, which could impact the research if elephants are drawn to the image 
first displayed. The team has tried putting the monitors to sleep until they are all ready to be displayed, but this 
causes the time between the fixation selection and the stimuli being shown to be even more delayed. This is an issue 
as it is important for the elephant's to receive an immediate response to their actions.

Additional solutions we've thought of that haven't worked are caching the images and reducing file sizes. The raspberry 
pi hardware makes it unfeasible to cache images in advance. As for reducing image sizes, the current black/white images 
used were already relatively small compared to other stimuli we could see being needed in the future. Additionally, while 
these two stimuli were not the same size, neither was consistently displayed quicker than the other - leading us to believe 
image size was not apart of the issue.

We believe the primarly issue for this delay is due to using SSH, especially as the Arduino with the wifi shield receives signals 
almost instantaneously. We'd recommend an HTTP server or MQTT messaging server be used as they both could be quicker than ssh. 

SP22: 
This issue was originally notice by the AU21 CSE team and was initially a primary objective of the SP22 CSE team, before
changing scope to restore base functionality. Near the end of our project period, we were able to dedicate some time to
researching this problem further and concluded that the source of the delay is very likely the SSH commands which
signal the Sensor Pis to display images and trigger the LED responses on input. Our best guess for a solution with the
time remaining was to create a seperate Flask App, in which the use of SSH commmand during experiment execution were
minimized by moving the choice and image display logic from the back-end Server Pi, to the Sensor Pis. In theory, this might
reduce the image and LED delay during trials (not between trials). We were not able to prototype this theory before the 
semester concluded. Unfortunately, we do not believe this solution would completely eliminate delay, only mitigate/move it.

Furthermore, we are unsure this problem can be solved using the current hardware setup. Communication between devices is
essential for experiment execution, but this communication takes time. Instead, we propose that a new system be designed using
only one point of connection (one computer). This might be able to eliminate image and LED delay altogether as well as greatly
simplify software and hardware setup.

UI
#############
While in AU21 we improved the UI, Dr. Kalafut expressed interest in developing more UI features. This could possibly be
a secondary objective for a future capstone team.
