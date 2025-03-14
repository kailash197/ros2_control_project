import os
from launch import LaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import get_package_prefix
from launch_ros.descriptions import ParameterValue
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction, LogInfo
from launch.event_handlers import OnProcessExit, OnExecutionComplete, OnProcessStart

def generate_launch_description():

    description_package_name = "rb1_ros2_description"
    install_dir = get_package_prefix(description_package_name)

    # This is to find the models inside the models folder in rb1_ros2_description package
    gazebo_models_path = os.path.join(description_package_name, 'models')
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] = os.environ['GAZEBO_MODEL_PATH'] + \
            ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = install_dir + \
            "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + \
            ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Define the launch arguments for the Gazebo launch file
    gazebo_launch_args = {
        'verbose': 'false',
        'pause': 'false',
    }

   # Include the Gazebo launch file with the modified launch arguments
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
        launch_arguments=gazebo_launch_args.items(),
    )

    # Define the robot model files to be used
    robot_desc_file = "rb1_ros2_base.urdf.xacro"
    robot_desc_path = os.path.join(get_package_share_directory(
        "rb1_ros2_description"), "xacro", robot_desc_file)

    robot_name_1 = "rb1_robot"

    rsp_robot1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'use_sim_time': use_sim_time,
                     'robot_description': ParameterValue(Command(['xacro ', robot_desc_path]), value_type=str)}],
        output="screen"
    )

    spawn_robot1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', robot_name_1, '-x', '0.0', '-y', '0.0', '-z', '0.0',
                   '-topic', '/robot_description']
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster",
                   "--controller-manager", "/controller_manager"],
    )

    diffdrive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["rb1_base_controller",
                   "--controller-manager", "/controller_manager"],
    )

    # lift_controller_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["lifting_effort_controller",
    #                "--controller-manager", "/controller_manager"],
    # )

    return LaunchDescription([
        gazebo,
        rsp_robot1,
        RegisterEventHandler(
                event_handler=OnProcessStart(
                    target_action=rsp_robot1,
                    on_start=[
                        TimerAction(
                            period=10.0, # gazebo loading
                            actions=[spawn_robot1],
                        )
                    ]
                )
            ),
        RegisterEventHandler(
            OnExecutionComplete(
                target_action=spawn_robot1,
                on_completion=[
                    LogInfo(
                        msg='Spawn finished, waiting 10 seconds to start controllers.'),
                    TimerAction(
                        period=10.0,
                        actions=[joint_state_broadcaster_spawner],
                    )
                ]
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diffdrive_controller_spawner],
            )
        ),
        # RegisterEventHandler(
        #     event_handler=OnProcessExit(
        #         target_action=diffdrive_controller_spawner,
        #         on_exit=[lift_controller_spawner],
        #     )
        # ),
    ])
