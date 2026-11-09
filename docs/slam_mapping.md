# SLAM Mapping

Create a map by driving the robot with a keyboard.

## 1. Connect the Robot

Follow [Keyboard Teleoperation](keyboard_teleop.md) to start the micro-ROS Agent and connect the robot.

Keep the Agent running.

## 2. Start SLAM

Open a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 launch microroscar_bringup slam_mapping.launch.py
```

Keep this terminal running.

## 3. Drive and View the Map

Open another terminal and start keyboard control:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p stamped:=false -p speed:=0.05 -p turn:=0.3
```

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

## 4. Save the Map

Open a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

mkdir -p ~/MicroROSCar/maps

ros2 run nav2_map_server map_saver_cli \
  -f ~/MicroROSCar/maps/my_map
```

Your map is saved as `my_map.yaml` and `my_map.pgm`.

## 5. Shutdown

1. Press `k` to stop the robot.
2. Stop keyboard control, SLAM, and RViz2 with `Ctrl+C`.
3. Turn off the robot.
4. Stop the micro-ROS Agent with `Ctrl+C`.

If something does not work, see [Troubleshooting](troubleshooting.md).
