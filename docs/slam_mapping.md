# Step B — Keyboard Driving + Map Creation

Create your own map by driving the robot with a keyboard. This saved map will
be used in [Step C](navigation.md); no instructor map is provided.

Complete [Step A](keyboard_teleop.md) first. For a clear starting point, finish
its shutdown steps before beginning this session. Start with the robot off
and no old Agent, teleop, SLAM or navigation processes running.

## Terminal 1 — Connect the Robot

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 run micro_ros_agent micro_ros_agent udp4 --port 8090 -v4
```

Power on the robot after starting the Agent. Keep this terminal running.
Only one Agent and one keyboard-control process should be running.

## Terminal 2 — Start SLAM

Open a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 launch microroscar_bringup slam_mapping.launch.py
```

Keep this terminal running.

## Terminal 3 — Drive with the Keyboard

Open another terminal and start keyboard control:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p stamped:=false -p speed:=0.05 -p turn:=0.3
```

Use the keys from Step A. Start slowly and keep the power switch accessible.

## Terminal 4 — View the Map

Open another terminal and run:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

rviz2
```

In RViz2:

- Fixed Frame: `map`
- Add → Map → Topic: `/map`
- Add → LaserScan → Topic: `/scan` (Best Effort)

Drive slowly and watch the map expand. Press `k` to stop.

## Terminal 5 — Save Your Map for Step C

Stop the car with `k` in Terminal 3, but leave the Agent and SLAM running.
Open a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

mkdir -p ~/MicroROSCar/maps

ros2 run nav2_map_server map_saver_cli \
  -f ~/MicroROSCar/maps/my_map
```

Your map is saved as `my_map.yaml` and a map image (normally `my_map.pgm`).
Check that saving succeeds. Keep the YAML and the image it references together
under `~/MicroROSCar/maps/`. These are local data files, not Git-tracked
package files. You do not need to rebuild the package after saving a map.

If you need to preserve an earlier map, use a different basename after `-f`.
Use that same YAML filename when starting C.

## Shutdown Before Step C

1. Press `k` to stop the robot.
2. Stop keyboard control in Terminal 3 with `Ctrl+C`.
3. Turn off the robot.
4. Stop the SLAM launch in Terminal 2 and RViz2 in Terminal 4 with `Ctrl+C`.
   Stopping the SLAM launch also stops its odometry and LiDAR TF nodes.
5. Stop the micro-ROS Agent in Terminal 1 with `Ctrl+C`.

Continue to [Step C — Navigation on Your Saved Map](navigation.md).
Do not leave the B processes running: C starts its own Agent and TF nodes,
and uses AMCL instead of SLAM to localize on the map you just saved.

If something does not work, see [Troubleshooting](troubleshooting.md).
