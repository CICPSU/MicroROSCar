#!/usr/bin/env python3

import argparse
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.time import Time

from geometry_msgs.msg import PoseStamped, Twist
from nav2_msgs.action import ComputePathToPose, FollowPath
from tf2_ros import Buffer, TransformListener
from action_msgs.msg import GoalStatus


TEST_DURATION = 240.0
GOAL_DISTANCE = 0.40
MAX_TF_AGE = 3.0


def wait_future(node, future, timeout=5.0):
    rclpy.spin_until_future_complete(
        node, future, timeout_sec=timeout
    )
    return future.done()


def main():
    parser = argparse.ArgumentParser(
        description='Plan a Nav2 path, optionally execute it on MicroROSCar.'
    )
    parser.add_argument(
        '--execute', action='store_true',
        help='Send the path to the controller; omitted means dry run only.',
    )
    parser.add_argument(
        '--rviz-goal', action='store_true',
        help='Wait for a new RViz 2D Goal Pose click on /goal_pose.',
    )
    parser.add_argument('--goal-x', type=float)
    parser.add_argument('--goal-y', type=float)
    parser.add_argument(
        '--distance', type=float, default=GOAL_DISTANCE,
        help='Forward distance when no explicit or RViz goal is given.',
    )
    args = parser.parse_args()
    if (args.goal_x is None) != (args.goal_y is None):
        parser.error('--goal-x and --goal-y must be given together')
    if args.rviz_goal and args.goal_x is not None:
        parser.error('--rviz-goal cannot be combined with coordinates')
    if args.distance <= 0:
        parser.error('--distance must be positive')
    execute = args.execute

    rclpy.init()
    node = Node('follow_path_test')

    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node)

    planner = ActionClient(
        node, ComputePathToPose, '/compute_path_to_pose'
    )

    controller = ActionClient(
        node, FollowPath, '/follow_path'
    )

    stop_pub = node.create_publisher(
        Twist, '/cmd_vel', 10
    )

    cmd_stats = {
        'monitoring': False,
        'received': 0,
        'nonzero': 0,
        'max_v': 0.0,
        'max_w': 0.0,
    }

    def cmd_callback(msg):
        if not cmd_stats['monitoring']:
            return

        cmd_stats['received'] += 1

        v = msg.linear.x
        w = msg.angular.z

        cmd_stats['max_v'] = max(cmd_stats['max_v'], abs(v))
        cmd_stats['max_w'] = max(cmd_stats['max_w'], abs(w))

        if abs(v) > 0.001 or abs(w) > 0.001:
            cmd_stats['nonzero'] += 1

            if cmd_stats['nonzero'] <= 10:
                print(f'cmd_vel: v={v:.3f}, w={w:.3f}')

    cmd_sub = node.create_subscription(
        Twist, '/cmd_vel', cmd_callback, 10
    )

    follow_handle = None
    follow_result_future = None
    goal_request_future = None

    try:
        # 1. Get robot position
        print('Waiting for robot position...')

        transform = None
        start_time = time.monotonic()

        while time.monotonic() - start_time < 20.0:
            rclpy.spin_once(node, timeout_sec=0.1)

            try:
                candidate = tf_buffer.lookup_transform(
                    'map', 'base_footprint', Time()
                )

                stamp = candidate.header.stamp
                age = time.time() - (
                    stamp.sec + stamp.nanosec * 1e-9
                )

                if age < -0.5 or age > MAX_TF_AGE:
                    continue

                transform = candidate
                print(f'TF acquired (age={age:.3f}s)')
                break

            except Exception:
                pass

        if transform is None:
            print('ERROR: Fresh robot position unavailable.')
            return

        x = transform.transform.translation.x
        y = transform.transform.translation.y
        q = transform.transform.rotation

        yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z)
        )

        # 2. Plan path
        goal = ComputePathToPose.Goal()
        goal.goal = PoseStamped()
        goal.goal.header.frame_id = 'map'
        goal.goal.header.stamp = node.get_clock().now().to_msg()

        if args.rviz_goal:
            clicked_goals = []
            click_sub = node.create_subscription(
                PoseStamped, '/goal_pose',
                lambda msg: clicked_goals.append(msg), 10
            )
            print('RViz: click 2D Goal Pose within 60 seconds...')
            start_wait = time.monotonic()
            while not clicked_goals and time.monotonic() - start_wait < 60.0:
                rclpy.spin_once(node, timeout_sec=0.1)
            if not clicked_goals:
                print('ERROR: No RViz goal received.')
                return
            clicked = clicked_goals[-1]
            if clicked.header.frame_id.lstrip('/') != 'map':
                print('ERROR: RViz goal must use the map frame.')
                return
            gx = clicked.pose.position.x
            gy = clicked.pose.position.y
            print('RViz goal received (goal arrow orientation not used).')
        elif args.goal_x is not None:
            gx = args.goal_x
            gy = args.goal_y
        else:
            gx = x + args.distance * math.cos(yaw)
            gy = y + args.distance * math.sin(yaw)

        goal.goal.pose.position.x = gx
        goal.goal.pose.position.y = gy
        print(f'Goal: x={gx:.3f}, y={gy:.3f}')
        goal.goal.pose.orientation = q

        goal.planner_id = 'GridBased'
        goal.use_start = False

        print('Planning path...')

        if not planner.wait_for_server(timeout_sec=5.0):
            print('ERROR: Planner unavailable.')
            return

        future = planner.send_goal_async(goal)

        if not wait_future(node, future):
            print('ERROR: Planning request timed out.')
            return

        plan_handle = future.result()

        if plan_handle is None or not plan_handle.accepted:
            print('ERROR: Planning rejected.')
            return

        result_future = plan_handle.get_result_async()

        if not wait_future(node, result_future):
            print('ERROR: Planning timed out.')
            return

        response = result_future.result()

        if response is None or response.status != GoalStatus.STATUS_SUCCEEDED:
            print('ERROR: Planning failed.')
            return

        path = response.result.path

        if len(path.poses) < 2:
            print('ERROR: Path too short.')
            return

        print(f'Path generated: {len(path.poses)} poses')

        endpoint = path.poses[-1].pose.position
        endpoint_error = math.hypot(endpoint.x - gx, endpoint.y - gy)
        print(f'Requested goal: x={gx:.6f}, y={gy:.6f}')
        print(f'Path endpoint: x={endpoint.x:.6f}, y={endpoint.y:.6f}')
        print(f'Endpoint error: {endpoint_error:.3f} m')
        if endpoint_error > 0.05:
            print('ERROR: Planner shifted the goal by more than 5 cm.')
            return

        # Default: do not move
        if not execute:
            print('DRY RUN COMPLETE - FollowPath not sent.')
            return

        # 3. Execute FollowPath
        if not controller.wait_for_server(timeout_sec=5.0):
            print('ERROR: Controller unavailable.')
            return

        # Recheck TF immediately before sending the goal
        try:
            current_tf = tf_buffer.lookup_transform(
                'map', 'base_footprint', Time()
            )
            stamp = current_tf.header.stamp
            age = time.time() - (
                stamp.sec + stamp.nanosec * 1e-9
            )

            if age < -0.5 or age > MAX_TF_AGE:
                print(f'ERROR: TF too old or invalid ({age:.2f}s).')
                return
        except Exception as e:
            print(f'ERROR: TF unavailable: {e}')
            return

        follow_goal = FollowPath.Goal()
        follow_goal.path = path
        follow_goal.controller_id = 'FollowPath'
        follow_goal.goal_checker_id = 'general_goal_checker'
        follow_goal.progress_checker_id = 'progress_checker'

        print('EXECUTION MODE ENABLED')
        cmd_stats['monitoring'] = True
        print('Sending FollowPath goal...')

        goal_request_future = controller.send_goal_async(
            follow_goal
        )

        # A delayed response may still represent an accepted goal.
        if not wait_future(node, goal_request_future, timeout=5.0):
            print('WARNING: Goal response delayed.')
            print('POWER OFF THE ROBOT NOW.')
            print('Waiting briefly for a goal handle to cancel...')
            wait_future(node, goal_request_future, timeout=5.0)

        if not goal_request_future.done():
            print('ERROR: Cannot determine goal acceptance.')
            print('KEEP ROBOT POWER OFF.')
            return

        follow_handle = goal_request_future.result()

        if follow_handle is None or not follow_handle.accepted:
            print('FollowPath rejected.')
            return

        print('FollowPath accepted.')

        follow_result_future = follow_handle.get_result_async()

        start = time.monotonic()

        while time.monotonic() - start < TEST_DURATION:
            rclpy.spin_once(node, timeout_sec=0.1)

            if follow_result_future.done():
                result = follow_result_future.result()
                print(f'Controller finished: status={result.status}')
                if result.status == GoalStatus.STATUS_SUCCEEDED:
                    try:
                        final_tf = tf_buffer.lookup_transform(
                            'map', 'base_footprint', Time()
                        )
                        fx = final_tf.transform.translation.x
                        fy = final_tf.transform.translation.y
                        error = math.hypot(fx - gx, fy - gy)
                        print(
                            f'Final position: x={fx:.3f}, y={fy:.3f}; '
                            f'goal error={error:.3f} m'
                        )
                    except Exception as e:
                        print(f'Final pose unavailable: {e}')
                break

        print('Execution window finished.')

    except KeyboardInterrupt:
        print('\nInterrupted. Requesting stop...')

    finally:
        # 4. Cancel accepted goal and check terminal status
        if follow_handle is not None:
            try:
                if (
                    follow_result_future is not None
                    and follow_result_future.done()
                ):
                    print(
                        'Goal already finished:',
                        follow_result_future.result().status
                    )
                else:
                    print('Canceling FollowPath...')
                    cancel_future = follow_handle.cancel_goal_async()

                    if wait_future(node, cancel_future, timeout=3.0):
                        cancel_response = cancel_future.result()

                        if cancel_response.goals_canceling:
                            print('Cancel request accepted.')
                        else:
                            print('Cancel not accepted or goal already finished.')
                    else:
                        print('WARNING: Cancel response timed out.')

                    if (
                        follow_result_future is not None
                        and wait_future(
                            node, follow_result_future, timeout=3.0
                        )
                    ):
                        status = follow_result_future.result().status
                        print(f'Final goal status: {status}')

                        if status not in (
                            GoalStatus.STATUS_CANCELED,
                            GoalStatus.STATUS_SUCCEEDED,
                            GoalStatus.STATUS_ABORTED,
                        ):
                            print('WARNING: Goal not confirmed terminated.')
                    else:
                        print('WARNING: Goal termination not confirmed.')

            except Exception as e:
                print(f'WARNING: Cancellation error: {e}')

        if cmd_stats['monitoring']:
            cmd_stats['monitoring'] = False

            print('=== Velocity Summary ===')
            print(f"Messages: {cmd_stats['received']}")
            print(f"Nonzero: {cmd_stats['nonzero']}")
            print(f"Max linear: {cmd_stats['max_v']:.3f} m/s")
            print(f"Max angular: {cmd_stats['max_w']:.3f} rad/s")

        # 5. Request zero velocity
        print('Publishing zero velocity...')

        for _ in range(10):
            stop_pub.publish(Twist())
            rclpy.spin_once(node, timeout_sec=0.1)

        print('Verify wheels have physically stopped.')
        print('If uncertain, POWER OFF THE ROBOT.')

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
