from omni.isaac.examples.base_sample import BaseSample
from omni.isaac.dofbot.tasks import FollowTarget as FollowTargetTask
from omni.isaac.dofbot.controllers import RMPFlowController
import omni
from omni.isaac.dynamic_control import _dynamic_control
import math
import socket
from _thread import *

HOST = '192.168.0.112'
PORT = 6100

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
# 서버로부터 메세지를 받는 메소드
# 스레드로 구동 시켜, 메세지를 보내는 코드와 별개로 작동하도록 처리
def recv_data(client_socket) :
    while True :
        data = client_socket.recv(1024)

        print("recieve : ",repr(data.decode()))
start_new_thread(recv_data, (client_socket,))
print ('>> Connect Server')

class DofbotSync(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._controller = None
        self._articulation_controller = None
        
    def setup_scene(self):
        world = self.get_world()
        world.add_task(FollowTargetTask())
        return
    
    async def setup_pre_reset(self):
        world = self.get_world()
        if world.physics_callback_exists("sim_step"):
            world.remove_physics_callback("sim_step")
        self._controller.reset()
        return
    
    def world_cleanup(self):
        self._controller = None
        return
    
    async def setup_post_load(self):
        self._dofbot_task = list(self._world.get_current_tasks().values())[0]
        self._task_params = self._dofbot_task.get_params()
        my_dofbot = self._world.scene.get_object(self._task_params["robot_name"]["value"])
        self._controller = RMPFlowController(name="target_follower_controller", robot_prim_path = my_dofbot.prim_path)
        self._articulation_controller = my_dofbot.get_articulation_controller()
        return 

    async def _on_follow_target_event_async(self):
        world = self.get_world()
        await world.play_async()
        world.add_physics_callback("sim_step", self._on_follow_target_simulation_step)
        return
    
    def _on_follow_target_simulation_step(self, step_size):
        observations = self._world.get_observations()
        actions = self._controller.forward(
            target_end_effector_position = observations[self._task_params["target_name"]["value"]]["position"],
            target_end_effector_orientation=observations[self._task_params["target_name"]["value"]]["orientation"],
        )
        self._articulation_controller.apply_action(actions)
        return
    
    def _on_add_obstacle_event(self):
        world = self.get_world()
        current_task = list(world.get_current_tasks().values())[0]
        cube = current_task.add_obstacle()
        self._controller.add_cube_obstacle(cube.prim)
        return

    def _on_remove_obstacle_event(self):
        world = self.get_world()
        current_task = list(world.get_current_tasks().values())[0]
        obstacle_to_delete = current_task.get_obstacle_to_delete()
        self._controller.remove_cube_obstacle(obstacle_to_delete.prim)
        current_task.remove_obstacle()
        return

    def _on_start_logging_event(self):
        world = self.get_world()
        data_logger = world.get_data_logger()
        robot_name = self._task_params["robot_name"]["value"]
        target_name = self._task_params["target_name"]["value"]

        def frame_logging_func(tasks, scene):
            omni.timeline.get_timeline_interface().play()
            dc = _dynamic_control.acquire_dynamic_control_interface()
            art = dc.get_articulation("/World/DofBot")
            dof_ptr = dc.find_articulation_dof(art, "joint1")
            ds1=int(math.degrees(dc.get_dof_state(dof_ptr,7).pos)+90)
            dof_ptr = dc.find_articulation_dof(art, "joint2")
            ds2=int(math.degrees(dc.get_dof_state(dof_ptr,7).pos)+90)
            dof_ptr = dc.find_articulation_dof(art, "joint3")
            ds3=int(math.degrees(dc.get_dof_state(dof_ptr,7).pos)+90)
            dof_ptr = dc.find_articulation_dof(art, "joint4")
            ds4=int(math.degrees(dc.get_dof_state(dof_ptr,7).pos)+90)
            dof_ptr = dc.find_articulation_dof(art, "Wrist_Twist_RevoluteJoint")
            ds5=int(math.degrees(dc.get_dof_state(dof_ptr,7).pos)+90)
            dof_ptr = dc.find_articulation_dof(art, "Finger_Left_01_RevoluteJoint")
            ds6=int(math.degrees(dc.get_dof_state(dof_ptr,7).pos)+90)
            
            if(ds1<10):
                ds1 = "00"+str(ds1)
            elif(ds1<100):
                ds1 = "0"+str(ds1)
            else:
                ds1 = str(ds1)
                
            if(ds2<10):
                ds2 = "00"+str(ds2)
            elif(ds2<100):
                ds2 = "0"+str(ds2)
            else:
                ds2 = str(ds2)
            
            if(ds3<10):
                ds3 = "00"+str(ds3)
            elif(ds3<100):
                ds3 = "0"+str(ds3)
            else:
                ds3 = str(ds3)
            
            if(ds4<10):
                ds4 = "00"+str(ds4)
            elif(ds4<100):
                ds4 = "0"+str(ds4)
            else:
                ds4 = str(ds4)
                
            if(ds5<10):
                ds5 = "00"+str(ds5)
            elif(ds5<100):
                ds5 = "0"+str(ds5)
            else:
                ds5 = str(ds5)
                
            if(ds6<10):
                ds6 = "00"+str(ds6)
            elif(ds6<100):
                ds6 = "0"+str(ds6)
            else:
                ds6 = str(ds6)
                
            print(ds1,ds2,ds3,ds4,ds5,ds6)
            message = "$20"+ds1+ds2+ds3+ds4+ds5+ds6+"#"
            client_socket.send(message.encode())


            
            
            # print(math.degrees(dof_state.pos))
            # print(math.degrees(scene.get_object(robot_name).get_joint_positions()))
            # print(scene.get_object(robot_name).get_joint_positions())
            return {
                "joint_positions": scene.get_object(robot_name).get_joint_positions().tolist(),
                "applied_joint_positions": scene.get_object(robot_name).get_applied_action().joint_positions.tolist(),
                "target_position": scene.get_object(target_name).get_world_pose()[0].tolist(),
            }

        data_logger.add_data_frame_logging_func(frame_logging_func)
        data_logger.start()
        return

    def _on_save_data_event(self, log_path):
        world = self.get_world()
        data_logger = world.get_data_logger()
        data_logger.save(log_path=log_path)
        data_logger.reset()
        client_socket.close()
        return
