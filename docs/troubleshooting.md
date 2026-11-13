# Troubleshooting

If you encounter problems, try the following solutions.

## 1. micro-ROS Agent Not Found

If the Agent cannot be started, check:

```bash
ls ~/MicroROSCar/install/local_setup.bash
```

If the file does not exist, follow [Initial Setup](setup.md).

## 2. Robot Does Not Connect

Make sure:

- The robot is powered on.
- The micro-ROS Agent is running.
- The ROS-Backup-PC is connected to `psu-iot`.

Check the PC's IP address:

```bash
ip -br -4 addr
```

The robot must be configured to connect to the PC's current IP address.

If the IP address has changed, ask the instructor to update the robot configuration.

## 3. ROS Topics Are Missing

Check the ROS environment:

```bash
echo $ROS_DOMAIN_ID
```

The expected value is `20`.

Then check:

```bash
ros2 node list
ros2 topic list
```

If `/YB_Car_Node` does not appear, restart the Agent and robot.

## 4. Keyboard Control Does Not Work

Make sure:

- The robot is connected.
- The keyboard terminal is active.
- `/cmd_vel` appears in the topic list.

Check:

```bash
ros2 topic info /cmd_vel
```

If the robot moves unexpectedly, press `k` to stop it. Use the physical power switch if necessary.

## 5. Step C — Navigation on Your Saved Map

Follow [Step C](navigation.md) using the map saved in [Step B](slam_mapping.md).
No instructor or sample map is included. Pass its absolute YAML path using
`map:="$HOME/MicroROSCar/maps/my_map.yaml"` and keep its referenced map image
beside it. A missing map argument or nonexistent YAML stops startup.

Complete B's shutdown steps before starting C. Do not run SLAM, its TF nodes
or keyboard teleop concurrently with autonomous navigation. C starts its own
Agent and TF nodes; do not leave B's copies running.

In a terminal with the ROS environment sourced, check:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
```

All four should be `active [3]` after the initial pose is set. If AMCL has no
`map -> odom_frame` TF, set the car's initial pose in RViz. Do not retry a
blocked goal: use another open point. The navigation parameters deliberately
set `GridBased.tolerance=0.0` so the planner does not silently move a goal.
