import os
from omni.isaac.examples.base_sample import BaseSampleExtension
from omni.isaac.examples.COEX_Exhibition_project import SocialLearning
import asyncio
import omni.ui as ui
from omni.isaac.ui.ui_utils import btn_builder, str_builder

class SocialLearningExtension(BaseSampleExtension):     #BaseSampleExtension을 상속받음
    def on_startup(self, ext_id: str):
        super().start_extension(
            menu_name="COEX_Exhibition_project",
            submenu_name="",
            name="SocialLearning",
            title="SocialLearning",
            doc_link="",
            overview="This Example shows how Dofbots are sharing their knowledges via SocialLearning with help of Omniverse Isaac Sim."
            sample=SocialLearning(),
            file_path=os.path.abspath(__file__),
            number_of_extra_frames=2,
            window_width=700
        )
        self.task_ui_elements = {},
        frame = self.get_frame(index=0)
        self.build_teach_dofbots_ui(frame)
        frame = self.get_frame(index=1)
        self.build_synchronize_real_world_ui(frame)
        return
    
    def _on_follow_the_movement_event(self):
        asyncio.ensure_future(self._on_follow_the_movement_event_async())
        self.task_ui_elements["Follow the Movement"].enabled = False
        self.task_ui_elements["Send Data"].enabled = True
        self.task_ui_elements["Synchronize Real World"].enabled = False
        return
    
    def _on_send_data_event(self):
        self.sample._on_send_data_event(self.task_ui_elements["Mobius Server"])
        self.task_ui_elements["Send Data"].enabled = False
        self.task_ui_elements["Stop Sending Data"].enabled = True
        
    def _on_stop_sending_data_event(self):
        self.sample._on_stop_sending_data_event()
        self.task_ui_elements["Send Data"].enabled = True
        self.task_ui_elements["Stop Sending Data"].enabled = False

    def _on_synchronize_real_world_event(self):
        self.sample._on_synchronize_real_world_event()
        self.task_ui_elements["Synchronize Real World"].enabled = False
        self.task_ui_elements["Follow the Movement"].enabled = False
        
    def post_reset_button_event(self):
        self.task_ui_elements["Follow the Movement"].enabled = True
        self.task_ui_elements["Send Data"].enabled = False
        self.task_ui_elements["Stop Sending Data"].enabled = False
        self.task_ui_elements["Synchronize Real World"].enabled = True
        return
        
    def post_load_button_event(self):
        self.task_ui_elements["Follow the Movement"].enabled = True
        self.task_ui_elements["Send Data"].enabled = False
        self.task_ui_elements["Stop Sending Data"].enabled = False
        self.task_ui_elements["Synchronize Real World"].enabled = True
        return
        
    def post_clear_button_event(self):
        self.task_ui_elements["Follow the Movement"].enabled = False
        self.task_ui_elements["Send Data"].enabled = False
        self.task_ui_elements["Stop Sending Data"].enabled = False
        self.task_ui_elements["Synchronize Real World"].enabled = False
        return
        
    def shutdown_cleanup(self):
        return
    
    def build_teach_dofbots_ui(self, frame):
        with frame:
            with ui.VStack(spacing=5):
                frame.title = "Teach Dofbots"
                frame.visible = True
                dict = {
                    "label": "Follow The Movement",
                    "type": "button",
                    "text": "Follow The Movement",
                    "tooltip": "Follow The Movement",
                    "on_clicked_fn": self._on_follow_the_movement_event
                }
                
                self.task_ui_elements["Follow the Movement"] = btn_builder(**dict)
                self.task_ui_elements["Follow the Movement"].enabled = False
                dict = {
                    "label": "Send Data",
                    "type": "button",
                    "text": "Send Data",
                    "tooltip": "Send Data",
                    "on_clicked_fn": self._on_send_data_event
                }
                
                self.task_ui_elements["Stop Sending Data"] = btn_builder(**dict)
                self.task_ui_elements["Stop Sending Data"].enabled = False
                dict = {
                    "label": "Stop Sending Data",
                    "type": "button",
                    "text": "Stop Sending Data",
                    "tooltip": "Stop Sending Data",
                    "on_clicked_fn": self._on_stop_sending_data_event
                }
                self.task_ui_elements["Stop Sending Data"] = btn_builder(**dict)
                self.task_ui_elements["Stop Sending Data"].enabled = False