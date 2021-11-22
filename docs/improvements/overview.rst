Current Issues & Improvement Suggestions
==============
The AU21 CSE team focused on receiving inputs from the GPIO buttons and outputting to the treat dispenser,
connecting the devices so that they worked together. In the UI, we also added in image grouping and an experiment
template option. While we were able to finish our UI tasks, due to time constraints the connections between the 
software and GPIO inputs could not be optimized. Below are some of the issues we faced and suggestions on improving them.

Image Display Optimization Issues
#############
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

UI
#############
While in AU21 we improved the UI, Dr. Kalafut expressed interest in developing more UI features. This could possibly be
a secondary objective for a future capstone team.