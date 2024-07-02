[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/KHzC7ivQ)


## Usage for Fitt's Law script

fitts-law.py [PARTICIPANT ID] [DEVICE CONDITION] [NUMBER OF TRIALS] [LATENCY]

PARTICIPANT ID: Identifier for the tested participant.

DEVICE CONDITION: Identifier for the tested condition, i.e. the input device used and any additional circumstances like latency.

NUMBER OF TRIALS: For each target size and target distance, how often the reciprocal tapping task is repeated.

LATENCY: The latency added to mouse events in seconds. Optional (if left out, no latency is added).

Clicking the first circle on the screen will start the experiment. The script will automatically cycle through all target conditions until completion and then automatically terminate. If a directory called "results" exists within the working directory of the script, the recorded data will be saved into this directory in comma-seperated-values format named [PARTICIPANT ID]-[DEVICE CONDITION].csv.

## Usage for Gesture input script

This script does not require command line parameters.

The script requires a short calibration phase before it can be started. In the first calibration phase, hold your hand into the camera at a comfortable distance. Pinch your thumb and your index finger until they are barely divided and then hit Enter. In the second calibration phase, hold your hand at the same distance and spread your thumb and index finger apart, then hit Enter. Shortly after the calibration is complete, the script will automatically transfer control of the cursor to your hand gestures.

You can move the cursor by moving your thumb, as long as your hand is in the camera's field of view. To click, pinch your thumb and your index finger together. By keeping thumb and index finger together and moving your hand, you can also drag the cursor around. Try to keep your other hand out of the camera's field of view to prevent erroneous input.
