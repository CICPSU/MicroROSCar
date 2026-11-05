# Keyboard Teleoperation

Follow these steps to connect and drive the MicroROSCar using the ROS-Backup-PC.

## 1. Start the micro-ROS Agent

Open **Terminal 1** and run:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 run micro_ros_agent micro_ros_agent udp4 --port 8090 -v4
```

**Turn on the robot** after starting the Agent.

Keep this terminal running.

## 2. Check the Connection

Open **Terminal 2** and run:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 node list
ros2 topic list
```

You should see the robot node:

- `/YB_Car_Node`

And topics including:

- `/scan` (LiDAR)
- `/odom_raw` (Odometry)
- `/cmd_vel` (Velocity Commands)

## 3. Drive the Robot

In **Terminal 2**, run:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p stamped:=false -p speed:=0.05 -p turn:=0.3
```

Check that the displayed speed is `0.05` and turn rate is `0.3` before driving.

Use the following keys:

| Key | Action |
|---|---|
| `i` | Forward |
| `,` | Backward |
| `j` | Turn Left |
| `l` | Turn Right |
| `k` | Stop |

**Safety:** Start with the wheels off the ground. Press `k` to stop the robot and verify that it has stopped. Keep the power switch accessible.

## 4. Shutdown

1. Press `k` to stop the robot.
2. Press `Ctrl+C` in Terminal 2.
3. Turn off the robot.
4. Press `Ctrl+C` in Terminal 1.

---

If you encounter problems, see [Troubleshooting](troubleshooting.md).
