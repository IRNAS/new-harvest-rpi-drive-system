# Setup
1. Connect the power plug into the wall outlet and then into the device. A green light indicator on the back side will light up.
2. First connect to the device access point with the name `new-harvest-rpi-ap`. The password for the access point is `NewHarvest123`.
3. Launch the Web GUI by visiting the `192.168.100.1:1234`.
4. There are three possible operation modes and a PoStep Driver configuration tab - all described below.

![image](https://user-images.githubusercontent.com/17702921/167868500-61ed1365-f1a2-434c-8416-7fbf3382f83a.png)

**NOTE!** In case the Web GUI is not accessible via the access point, you can still access the Web GUI by creating a `new_harvest_ap` access point on your computer. The password must be `NewHarvest123`. This is the network the device will try to connect to.

# Flow Speed Calibration
The Flow Speed Calibration screen allows for calibration of the motor.
The workflow consits of **9** steps:
1. Set `Low PWM` in %.
2. Set `High PWM` in %.
3. Set `Time` in seconds.
4. Press the `Start` button and then press OK to start the calibration process.
5. Once the `Low PWM` calibration has finished measure the volume of the liquid and enter it into the corresponding box.
6. Press the `Next` button and confirm with OK.
7. Once the `High PWM` calibration has finished measure the volume of the liquid and enter it into the `High PWM` box.
8. Enter the `Filename`.
9. Save the calibration with a confirmation on the `Next` button.

![image](https://user-images.githubusercontent.com/17702921/167868610-8a44d89e-f869-4a03-80db-5b054f26f1ce.png)

# Single Flow Speed
This screen is used to manually set the Flow. This is done by first loading or uploading a calibration file. If you want to upload a calibration file from your computer press the `Browse` button and select one.

![image](https://user-images.githubusercontent.com/17702921/167868687-57bcb37f-10d3-41ca-963a-817679d6fb93.png)

Below is a sample calibration file.
```json
{
    "low_pwm": 10,
    "high_pwm": 100,
    "low_pwm_vol": 1.255,
    "high_pwm_vol": 6.46,
    "duration": 10
}
```

After the calibration file has been set you will see the calculated `Slope` in `mL/revolution`. Then you can set the `Flow` in `mL/min` and the desired `Acceleration` in `pwm/sec`. The default value is 100, which means the motor will accelerate from stand-still to full speed in a second. Set the desired `Direction` using the dropdown.

# Speed Profile
Aditionally to the calibration, this screen allows to select or upload a predefined `speed profile`.

![image](https://user-images.githubusercontent.com/17702921/167868767-2b926c23-e3a7-43fd-a78f-092cdee4fc55.png)

### Workflow
1. Load `calibration` file by either selecting it from the dropdown or uploading it.
2. Load `speed profile` file by either selecting it from the dropdown or uploading it.
3. Set the number of `Repeats`.
4. Select the direction.
5. Press the `Start` button and the uploaded `speed profile` will start to run.

### Speed Profile File
After the speed profile has been selected you will see a plot of it to the right, below the real time plot of the data.

The `speed profile` consists of several json objects, seperated with commas. The settings you can adjust are the `flow`, `duration` and `pwm_per_second`.

The `flow` field is set in `mL/min`, the `duration` field specifies for how long the set `flow` will be executed, and the `pwm_per_second` specifies the `acceleration` of the motor in `pwm/sec`.

```json
{
    "profile": [
        {"flow": 3.0, "duration": 30, "pwm_per_second": 50},
        {"flow": 3.4, "duration": 30, "pwm_per_second": 70},
        {"flow": 3.6, "duration": 30, "pwm_per_second": 100},
        {"flow": 3.1, "duration": 30, "pwm_per_second": 25},
        {"flow": 2.7, "duration": 30, "pwm_per_second": 50},
        {"flow": 4.3, "duration": 30, "pwm_per_second": 15}
    ]
}
```
The above speed profile will produce the following PWM profile with the `nejc1.json` calibration file.

![speed_profile_example](../images/speed_profile.png)

After the `calibration` and `speed profile` files have been selected you can set the `Repeat` box to more repetitions if so desired.

# PoStep Config

![image](https://user-images.githubusercontent.com/17702921/167868840-38366abb-c025-43dc-9175-c9f3278b13ec.png)

The PoStep Config screen allows you to modify the PoStep60-256 motor driver current settings.
You can set the:
* Full-scale current (A) - 0A to 6A
* Idle current (A) - 0A to 6A
* Overheat current (A) - 0A to 6A
