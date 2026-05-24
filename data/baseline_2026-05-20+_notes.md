# Notes on the garage experiment starting on 2026-05-20

* Testing the CO2 sensors in a garage for baseline values of sensor readings in the presence of minimal CO2 variations.
* There's no combustion happening in the garage or house, unless you count human metabolism. The garage has an electric heat pump water heater (HPWH) and an electric heat pump HVAC. The HPWH acts like an air conditioner for the garage -- moving heat from the garage air to the water. The CO2 sensor readings show some bumps, possibly due to these two appliances.
* 2026-05-20, 4:54pm power up all 19 sensors -- 1 string then the other with ~1/2 minute delay.
* The "0C" sensor is not providing data.
* Most of the sensors flash light about 0.5 Hz. A third of the sensors flash about 2 Hz.
* Initially the live graph showed times at "2:12pm" at clock time 5:50pm. This got fixed by 5:40:36pm. Presumably the gateway got the correct time from NTP. I don't know what date was timestamped on the first hour of data.
* I didn't connect the wind speed and wind direction sensors. What's the black dongle? There don't seem to be any air temerature readings during this test.
* There are some data dropouts e.g. at ≈5:40? Some blue and some blinking blue readings in the Testbed window. Later, some green, blinking green, and blinking orange readings in the Testbed.
* 5:47 Went in the garage for a minute or two.
* 6:01 Went into the garage, did a big exhale from the end of the table near the kitchen door for an "impulse response test", then walked out. This generated a big spike from a few sensors and little variation from the others.
* 6:38 Did an exhale impulse response test from the other end of the table. This generated a small spike from one sensor.
* 6:47 Repeat the second impulse response test but it still generated a modest spike from that end. See the 3 spikes starting at 6:01pm, 6:37pm, and 6:44pm in the image [images/baseline_zoom_in_to_see_breath_tests_and_garage_door_open-close.png](../images/baseline_zoom_in_to_see_breath_tests_and_garage_door_open-close.png).
* NOTE: Data filenames "baseline_CO2_data_<TIMESTAMP>.csv" contain the full data set up until the given TIMESTAMP. Data filenames "baseline2_CO2_data_<TIMESTAMP>.csv" have the readings before 6:55pm clipped out to compare sensor readings without the breath impulse response tests.
* 6:57 Opened and closed the main garage door. The opener reports 85°F air temperature. See the dip starting at 6:57 in the image [images/baseline_zoom_in_to_see_breath_tests_and_garage_door_open-close.png](../images/baseline_zoom_in_to_see_breath_tests_and_garage_door_open-close.png).
* ≈10:00 Put a tarp over the sensors.
* ≈10:30 Moved a car into the garage.
* See the image [images/baseline_zoom_in_to_see_bumps.png](../images/baseline_zoom_in_to_see_bumps.png) to see the bumps in the data. Hypothesis: These are due to the HPWH or the HP HVAC, although the former only impacts the garage air temperature and the latter shouldn't have much impace on garage air.
* See the image [images/baseline_zoom_in_to_see_bumps_in_favored_sensors.png](../images/baseline_zoom_in_to_see_bumps_in_favored_sensors.png) to see the bumps in just the sensors favored by eyeballing the graphs for responsiveness and cross-consistency.
* See the image [images/baseline_zoom_in_to_see_bumps_in_SP1_purple_plus_least_favored_sensors.png](../images/baseline_zoom_in_to_see_bumps_in_SP1_purple_plus_least_favored_sensors.png) to see the bumps in the favored SP1 sensor (thick purple) and sensors dis-favored by eyeballing the graphs for unresponsiveness or inconsistency with the others.
* 2026-05-22, ≈1:00pm Opened the garage door, moved one car out, closed the garage door, rotated the table for access to the washer &amp; dryer, and opened the tarp wider for more protection from transient changes. I'd move the table further from the HPWH and HP HVAC, but that would require temporarily unplugging it and starting everything up again. *Started a load of laundry.*
* See the image [images/baseline_zoom_in_to_see_response_to_laundry_machines_and_bumps_in_favored_sensors.png](../images/baseline_zoom_in_to_see_response_to_laundry_machines_and_bumps_in_favored_sensors.png) to see the favorite sensors responding to the laundry machines and the usual bumps that are probably caused by the HPWH or HP HVAC.
