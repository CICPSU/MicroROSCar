# MicroROSCar

ROS 2 Jazzy package for operating the Yahboom MicroROS Car on the
**ROS-Backup-PC**.

## Start Here — A, then B, then C

Complete [Initial Setup](docs/setup.md) once. Then work through these three
separate activities in order; each guide includes its terminal commands.

| Step | Activity | What you do |
| --- | --- | --- |
| **A** | [Keyboard Teleoperation](docs/keyboard_teleop.md) | Connect the car and drive it manually. No map is needed. |
| **B** | [Keyboard Driving + Map Creation](docs/slam_mapping.md) | Drive manually while SLAM builds a map; save your own map. |
| **C** | [Navigation on Your Saved Map](docs/navigation.md) | Load the map from B, set the initial pose, then plan and follow a path. |

All three modes remain available. **Do not run them at the same time.** Follow
the shutdown section of one step before starting the next. Step C uses AMCL
localization and Nav2 on a saved map; it does not run SLAM or create a new map.

## The Map Passes from B to C

Step B saves `~/MicroROSCar/maps/my_map.yaml` and its referenced map image
(normally `my_map.pgm`). Keep both files together. Maps are local lab data,
ignored by Git; **no instructor or sample map is distributed**.

Step C requires that map explicitly. After sourcing the ROS environment as
shown in its guide, the launch command is:

```bash
ros2 launch microroscar_bringup navigation.launch.py \
  map:="$HOME/MicroROSCar/maps/my_map.yaml"
```

If you used another name in B, pass that YAML instead. There is no fallback
map. A missing map argument or a nonexistent map file stops startup.

## Additional Resources

- [Troubleshooting](docs/troubleshooting.md)
