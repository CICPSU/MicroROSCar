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

Continue to [Keyboard Teleoperation](keyboard_teleop.md).

If anything seems wrong, refer to [Troubleshooting](troubleshooting.md).
