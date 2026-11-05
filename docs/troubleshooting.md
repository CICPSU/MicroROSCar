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
