# Initial Setup

Follow these steps when using MicroROSCar for the first time.

All commands should be executed on the **ROS-Backup-PC**.

## 1. Clone the Repository

Open a terminal and run:

```bash
cd ~
git clone https://github.com/CICPSU/MicroROSCar.git
cd MicroROSCar
```

If you have already cloned the repository, skip this step.

## 2. Build the ROS 2 Package

```bash
cd ~/MicroROSCar

source /opt/ros/jazzy/setup.bash

colcon build --symlink-install

source install/local_setup.bash
```

## 3. Verify the Setup

Run:

```bash
ros2 pkg prefix microroscar_bringup
```

If a directory path appears, the setup is complete.

## 4. Next Step

You are ready to connect and operate the robot!

Start with [Step A: Keyboard Teleoperation](keyboard_teleop.md), then complete
[Step B: Map Creation](slam_mapping.md), and finally
[Step C: Navigation on Your Saved Map](navigation.md). Step C uses the map
you save in B; no sample map is included.

For Step C, the ROS-Backup-PC must have the Nav2 map server, AMCL, planner,
controller, lifecycle manager and RViz packages installed. They were present
on the workstation used for the November 2026 validation.

If anything seems wrong, refer to [Troubleshooting](troubleshooting.md).
