# Step C — Navigation on Your Saved Map

Use the **ROS-Backup-PC** (`e5-ae-ros-pc2`) with ROS 2 Jazzy and the Yahboom
MicroROSCar. Complete [Step A](keyboard_teleop.md) and
[Step B](slam_mapping.md) first. This workflow follows a path on **the map
you saved in B**, using Navfn to plan and Regulated Pure Pursuit to drive at
up to **0.08 m/s**. It uses AMCL for localization, not SLAM; it does not build
or update the saved map.

The robot must have free floor space and a reachable goal. Keep access to its
power switch. Do not run keyboard teleop or SLAM at the same time.

## Before Starting C

- Save your map in B: `~/MicroROSCar/maps/my_map.yaml` and its referenced image
  (normally `my_map.pgm`). Keep both files together. No sample map is bundled.
- Follow B's shutdown steps. Stop its keyboard control, SLAM launch (including
  TF nodes), RViz and Agent. Power off the car before starting this launch.
- The `map` argument below is **required**. Use a different YAML path only if
  that is where you saved your own map. A missing argument or nonexistent
  file stops startup; there is no fallback to an old test map.

## Terminal 1 — Start everything

Start with the robot powered **off** and no old navigation or Agent processes
running. Open a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 launch microroscar_bringup navigation.launch.py \
  map:="$HOME/MicroROSCar/maps/my_map.yaml"
```

The launch starts the micro-ROS Agent (UDP port 8090), odometry TF, LiDAR TF,
map server, AMCL, Navfn planner, RPP controller, lifecycle manager, and RViz.
Wait until the Agent is listening, then **power on the car**. Keep Terminal 1
running. Lifecycle transitions are automatic.

**As soon as the saved map appears**, click **2D Pose Estimate** in RViz and
mark the car's actual position and heading. The red X axis should point in
the car's real forward direction. This initial pose is required to complete
the `map -> odom_frame -> base_footprint` transform chain; the planner may
remain in activation until it is supplied. Give the car and Nav2 a few
seconds to initialize. Set the initial pose within about three minutes of
launching; otherwise restart after any costmap startup timeout.

## Terminal 2 — Check and choose a goal

Open a second terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MicroROSCar/install/local_setup.bash
export ROS_DOMAIN_ID=20

ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
```

**After setting the initial pose**, all four should show `active [3]`. If any
is inactive, use the troubleshooting section below before trying to drive.

In RViz:

1. Check that the live laser points align reasonably with the saved map after
   setting the initial pose.
2. In Terminal 2, run the following command. It only plans a path:

   ```bash
   ros2 run microroscar_bringup follow_path --rviz-goal
   ```

3. While the command waits, click **2D Goal Pose** on clear floor in RViz. The
   goal must be away from obstacles by at least the car radius (0.22 m), with
   additional room to manoeuvre. Look for `Endpoint error: 0.000 m` and a red
   path. A blocked goal will be rejected. The script is a dry run by default.

## Terminal 2 — Drive the path

When the dry run looks right and the area is physically clear, run:

```bash
ros2 run microroscar_bringup follow_path --rviz-goal --execute
```

**Click the same 2D Goal Pose again** while the command waits. The script
replans from the latest position and then sends FollowPath. Watch the car.
Successful completion prints `Controller finished: status=4`; the car should
stop near the goal. If it behaves unexpectedly, stop the run and use the car's
power switch if needed.

The goal arrow's orientation is ignored: the script preserves the robot's
heading at the start as the desired final heading.

### Quick 40 cm test (no RViz goal click)

From a clear starting pose:

```bash
ros2 run microroscar_bringup follow_path
```

To execute the same type of short test:

```bash
ros2 run microroscar_bringup follow_path --execute
```

Coordinate goals are also supported with `--goal-x` and `--goal-y`; see
`ros2 run microroscar_bringup follow_path --help`. Use coordinates from your
own current map, not from another student's or instructor's test. Append
`--execute` only when ready to move.

## Stop and shut down

After the script finishes, verify that the wheels have stopped. Power off the
car, then press `Ctrl+C` in Terminal 1. If a FollowPath run is interrupted,
the script requests cancellation and publishes zero velocity; use the physical
power switch if the car has not stopped.

## What this setup does and does not do

- It plans one path using the current static map and live LiDAR-based costmap.
- It follows that path with RPP and stops on a collision risk.
- It does **not** continuously replan while driving. An obstacle that appears
  after planning may cause FollowPath to abort. This is an intended limitation
  of this minimal student handoff, and a good future project task.
- A successful action means Nav2's goal checker accepted the result. Its
  stateful 0.10 m XY tolerance can allow a slightly larger final stopped-position
  error after orientation adjustment.

## If something is wrong

| Symptom | Check |
| --- | --- |
| Missing `map` argument or map file | Save your map in B and pass its absolute YAML path with `map:=` |
| Map image cannot be loaded | Keep the image referenced by the YAML alongside it, as saved in B |
| `/scan` or `/odom_raw` missing | Agent, robot power, PSU IoT network |
| No `map -> base_footprint` TF | RViz **2D Pose Estimate**, AMCL, odometry TF |
| Nav2 node is inactive | Set **2D Pose Estimate** first; then read Terminal 1 lifecycle-manager errors. If startup timed out, power off the car, stop Terminal 1 and restart the launch |
| Planner fails | Pick an open goal; `GridBased.tolerance` is deliberately `0.0` |
| FollowPath aborts | Local costmap obstacle, TF timing, controller log |
| RViz goal click does nothing | Run `follow_path --rviz-goal` **before** clicking |

If needed, check these in Terminal 2:

```bash
ros2 param get /planner_server GridBased.tolerance
ros2 param get /controller_server FollowPath.transform_tolerance
timeout 5s ros2 run tf2_ros tf2_echo map base_footprint
```

The expected parameter values are `0.0` and `0.3` respectively. The exact
working configuration is packaged in
`src/microroscar_bringup/config/navigation.yaml`.

For first-time installation see [Initial Setup](setup.md). To map a new area,
shut down C before returning to [Step B](slam_mapping.md). More connection fixes are in
[Troubleshooting](troubleshooting.md).
