# h12project_ws
# ROS2和Gazebo

首先必须：

```bash
conda deactivate
```

但

### 方案：临时绕过 Conda 的 `libstdc++`

不退出 conda，但临时使用系统版本的 `libstdc++.so.6`：

```bash
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6


export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH



cd ~/h12project_ws
rm -rf build install log
colcon build
source install/setup.sh

```

然后

```bash
ros2 launch ros_gz_sim gz_sim.launch.py


ros2 launch ros_gz_bringup unitree_urdf.launch.py


```

## 五、工程结构理解（可开始修改）

你将看到四个主要包：

- `ros_gz_example_description`：SDF 模型和资源文件（如 meshes、材质）
- `ros_gz_example_application`：ROS 2 节点代码，如控制或路径规划算法
- `ros_gz_example_gazebo`：Gazebo 插件、系统和自定义 world 文件
- `ros_gz_example_bringup`：launch 文件、rviz 配置和 ros_gz_bridge 桥接配置

当你修改模型、增加控制器或换成你自己的机器人时，这些模块是你重点关注的内容。

------

## 六、模型加载说明（GZ_SIM_RESOURCE_PATH）

Gazebo 通过 `GZ_SIM_RESOURCE_PATH` 查找模型（SDF/URDF）资源。

本模板已通过 `ros_gz_example_description/hooks/ros_gz_example_description.dsv.in` 设置环境钩子，在你 `source install/setup.sh` 时自动将模型路径加入该环境变量，因此你不需要手动设置路径。

------

## 七、ROS-Gazebo 整合方式选择

- 使用 `ros_gz_bridge` 动态桥接话题（推荐、模块化、解耦）
- 将 ROS 节点嵌入 Gazebo 插件（适合需要 ECM 控制的低延迟任务）

默认示例采用的是桥接方式，位于 `ros_gz_example_bringup/config/ros_gz_example_bridge.yaml` 中。





你已经完成了从 Isaac Gym 到 MuJoCo 的 sim2sim 转移，现在打算迁移到 `ros-gz-project-template`（也就是 ROS 2 + Gazebo）中，这个过程主要是 **机器人模型转换 + 控制接口集成**。我会分步骤帮你梳理清楚：

------

## 🔁 总体目标：将 Unitree H1-2 + squatting 控制，迁移到 Gazebo + ROS 2

### 你已经有的成果：

- 在 Isaac Gym 中训练出的 H1-2 控制策略（可能是 RL 模型、轨迹控制器等）
- 一个在 MuJoCo 中测试成功的版本（说明控制器已经适配多物理引擎）

### 接下来要做的，是三部分工作：

------

## 1️⃣ 迁移机器人模型到 SDF（Gazebo 使用格式）

### 📌 目标：在 Gazebo 中重建 Unitree H1-2 的模型

如果你有 MuJoCo 的 XML 模型文件（`.mjcf`），你需要将它转换为 **SDF 或 URDF**，推荐优先 SDF。

**方法：**

- 若你已有 URDF 模型（如从 Unitree 提供的 ROS 包中），可直接使用，并加上 Gazebo 插件标签
- 或者手动将 MJCF → SDF（这个过程有些繁琐，可以我来协助你）
- 使用 https://github.com/unitreerobotics/unitree_ros 可能能找到 H1 相关的 ROS 描述模型

**集成到模板方法：**

放到：

```bash
ros_gz_description/models/unitree_h1/
├── model.config
├── model.sdf （或 URDF + xacro）
```

更新 launch 文件或 world 文件中调用它。

------

## 2️⃣ 集成控制策略为 ROS 2 节点

### 📌 目标：在 ROS 中重现 squatting 控制逻辑

你训练出来的 RL 策略有几种常见形式：

- Python 脚本（用 PyTorch/TensorFlow 加载模型）
- C++ 控制器（如果是写死的状态机或轨迹生成）

你需要把这个控制策略打包成一个 ROS 2 节点，发布关节命令到：

```bash
/joint_trajectory_controller/joint_trajectory
或
/<joint_name>/cmd_pos 等话题（depends on how you set up gazebo plugins）
```

**建议：**

- 建议用 `ros_gz_bridge` 桥接 Gazebo 与 ROS 中的 joint_state、joint_cmd 话题
- 控制策略运行在 `ros_gz_example_application` 包里，作为 ROS 2 节点发布控制信号

------

## 3️⃣ 桥接 Gazebo 与 ROS 2：感知与控制通路

通过 `ros_gz_bridge`，你可以在 Gazebo 与 ROS 2 之间连接这些话题：

- `/joint_states`（来自 Gazebo） → 控制器观测输入
- `/joint_commands` 或 `/trajectory_cmd`（来自 ROS 2） → 控制器输出指令
- 可以桥接传感器话题，比如 `/imu`, `/camera`, `/force_sensor` 等

这些桥接规则写在：

```bash
ros_gz_bringup/config/ros_gz_bridge.yaml
```

例如：

```bash
- topic_name: "joint_states"
  ros_type_name: "sensor_msgs/msg/JointState"
  gz_type_name: "ignition.msgs.Model"
```

🧩 示例整合路径

以你项目结构为例：

```bash
h12project_ws/
└── src/
    ├── ros_gz_application/
    │   └── src/
    │       └── squat_controller_node.py  # 你的RL控制器包装成ROS节点
    ├── ros_gz_description/
    │   └── models/unitree_h1/  # Gazebo可识别模型
    ├── ros_gz_bringup/
    │   └── launch/unitree_squat.launch.py  # 启动模型 + 控制器 + 桥接
```

