# Checkpoint 15: ROS2 Control

## About Project

This package, rb1_ros2_description, contains a ROS2 robot model description for Robotnik's RB-1 mobile base.
It has urdf and xacro files that describe robot models. This package implements following  two task for fulfillment of this checkpoint:
- Task 1: Configure the Differential Drive Controller with ROS2 Control
- Task 2: Implement a ROS2 Controller to have a functional Lifting Unit

For task1, ROS2 Control is used for implementation of differential drive in the RB1 robot using a ROS2 Gazebo Control plugin.
The parameters for this plugin are provided in rb1_controller.yaml file inside config directory of the package.

For task2, Gazebo's gazebo_ros_force_system plugin is used implement effort controllers to make the robot lift move up and down in simulation. 
The parameters for this plugin are provided in same file rb1_controller.yaml file inside config directory of the package.
Two services, /apply_joint_effort and clear_joint_efforts are used to  actuate the lifting unit joint.

## Clone the repository
```
cd ~/ros2_ws/src/
git clone https://github.com/kailash197/ros2_control_project.git
```

Move contents to src folder
```
mv ./ros2_control_project/.git/ ./
mv ./ros2_control_project/cp15_auxiliary_files/ ./
rm -rf ros2_control_project/
```

## Task1: Move robot using differential drive controller
### 1. Build and Run Simulation

```
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch rb1_ros2_description rb1_ros2_xacro.launch.py
```
This will launch gazebo simulation, spawn the rb1 robot and start following controllers:
- joint_state_broadcaster
- rb1_base_controller (differential drive controller)


Check using following command:
```
ros2 control list_controllers
```
![image](https://github.com/user-attachments/assets/6151850e-80ec-4c31-860f-b5e3a05ac7ea)


Also, make sure the /controller_manager and /gazebo_ros_control nodes exists.
```
ros2 node list
```
![image](https://github.com/user-attachments/assets/1d3df174-25c1-4259-abbc-7655bda537fc)


Check the hardware interfaces. Interfaces for active controllers are claimed. 
```
ros2 control list_hardware_interfaces
```
![image](https://github.com/user-attachments/assets/5f2ba610-ed7b-41da-9b8c-adf8a39d9a89)


Also, check for the command velocity topics.
```
ros2 topic list
```
![image](https://github.com/user-attachments/assets/4a0d6dbd-272e-431c-a26f-589e3a035d5d)



### 2. Moving robot around
/rb1_base_controller/cmd_vel_unstamped topic can be used to control robot's movement, either by teleop_twist_keyboard or simply publishing velocity commands as follows:

- Move forward direction
```
ros2 topic pub --rate 10 /rb1_base_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 0.25, y: 0, z: 0.0}, angular: {x: 0.0,y: 0.0, z: 0.0}}"  --once
```
- Move backward direction
```
ros2 topic pub --rate 10 /rb1_base_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: -0.25, y: 0, z: 0.0}, angular: {x: 0.0,y: 0.0, z: 0.0}}"  --once
```
- Rotate anticlockwise
```
ros2 topic pub --rate 10 /rb1_base_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0, z: 0.0}, angular: {x: 0.0,y: 0.0, z: 0.2}}"  --once
```
- Rotate clockwise  
```
ros2 topic pub --rate 10 /rb1_base_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0, z: 0.0}, angular: {x: 0.0,y: 0.0, z: -0.2}}"  --once
```
- Stop robot
 ```
  ros2 topic pub --rate 10 /rb1_base_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0, z: 0.0}, angular: {x: 0.0,y: 0.0, z: 0.0}}"  --once
  ```
Please feel free to change linear velocites to move in varying speed and directions.

### 3. Stop simulation
Use "Ctrl+C" to kill all the processes started by the launch file.

## Task2: Lift and release the robot elevator using Effort Controller
This section describes how to start effort controller, check various topics, services, etc to make sure it runs as expected.

### 1. Start simulation 
```
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch rb1_ros2_description rb1_ros2_xacro.launch.py
```
Using same launch file as previous section, launch gazebo simulation, spawn the rb1 robot and start all two controllers:
- joint_state_broadcaster
- rb1_base_controller (differential drive controller)


### 2. Start effort controller
```
ros2 control load_controller --set-state start lifting_effort_controller
```
![image](https://github.com/user-attachments/assets/d0f5de99-b481-4100-a84a-70fefdf1e5a3)


Check available controllers:
```
ros2 control list_controllers
```
![image](https://github.com/user-attachments/assets/240f67e7-409f-40bd-aa84-188bd7fc950e)


Also, make sure the /controller_manager and /gazebo_ros_control nodes exists.
```
ros2 node list
```
![image](https://github.com/user-attachments/assets/a54b5388-e2ea-49d6-8692-c90219b7e644)


Check the hardware interfaces. Interfaces for active controllers are claimed. 
```
ros2 control list_hardware_interfaces
```
![image](https://github.com/user-attachments/assets/2d1ff5b7-edcf-4a88-87d6-2e83735bd471)

Also, check for the command velocity topics. Topic for lifting_effort_controller are exposed too.
```
ros2 topic list
```
![image](https://github.com/user-attachments/assets/b30c787f-a87b-4f55-8a6f-02033a75373b)

As this implementation use service to actuate lifting unit up and down, check if these services are available as follows:
```
ros2 service list | grep joint_effort
```
![image](https://github.com/user-attachments/assets/8a5b364b-98bf-41a1-992c-221e15d0a061)



### 3. Commands to move the robot elevator
- Move up
```
ros2 service call /apply_joint_effort gazebo_msgs/srv/ApplyJointEffort '{joint_name: "robot_elevator_platform_joint", effort: 10.0, start_time: {sec: 0, nanosec: 0}, duration: {sec: 2000, nanosec: 0} }'
```

- Move down
```
ros2 service call /clear_joint_efforts gazebo_msgs/srv/JointRequest '{joint_name: "robot_elevator_platform_joint"}'
```

### 4. Stop the effort controller
Stop and unload the controller to shutdown completely.
```
ros2 control set_controller_state lifting_effort_controller stop
```
![image](https://github.com/user-attachments/assets/9f6180e1-3154-48d8-9131-f7fc291c300a)

```
ros2 control unload_controller lifting_effort_controller
```
![image](https://github.com/user-attachments/assets/1b26566a-52eb-4a8c-bd88-8904209be3c6)

And, use "Ctrl+C" to kill all the processes started by the launch file.







## Disclaimer:  
This package only modifies/adapts files from these repositories/packages:  
- [RobotnikAutomation/rb1_base_sim](https://github.com/RobotnikAutomation/rb1_base_sim) licensed under the BSD 2-Clause "Simplified" License
- [RobotnikAutomation/rb1_base_common/rb1_base_description](https://github.com/RobotnikAutomation/rb1_base_common/tree/melodic-devel/rb1_base_description), licensed under the BSD License
- [RobotnikAutomation/robotnik_sensors],(https://github.com/RobotnikAutomation/robotnik_sensors) licensed under the BSD License
