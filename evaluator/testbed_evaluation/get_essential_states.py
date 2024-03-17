import os
import re
from typing import Dict, List, NamedTuple, Optional

from ..task_trace import DatasetHelper, UIState


class EssentialState(UIState):
    """pic_id, ui_state represents what UI state this essential state belongs to,
    e.g., 1.png, 2.png, 3.png"""

    pic_id: Optional[int] = None
    ui_state: Optional[UIState] = None

    """[keyword, node_id] colloborately represent the essential state it self
    that should be matched.

        - keyword (str): 
        [
            fuzzy_match, 
            activity, textbox, button, click, 
            check_install, check_uninstall
        ], 
        in which "textbox", "button", "click", "activity" should be exactly
        matched.

        - node_id (int):
        for keyword "fuzzy_match", "textbox", "click", node_id
        is an integer representing one specific UI components.
        example: "fuzzy_match<0>", "textbox<10>", "click<3>"

        for keyword "activity", the integer is always -1

        for keyword "button", it contains an integer with a string "on" or "off"
        to indicate whether this button is on or off.
        example: "button<4:on>", "button<13:off>"

        for keyword "check_install" and "check_uninstall", the value will be an
        app's name
        example: "check_install<Mircosoft Excel>"

    """
    keyword: str
    node_id: int

    """all three paths are used to locate the ground-truth data in the 
    established dataset of this essential state
    """
    # vh_path: str  # represent which vh file this essential state belongs to
    # json_path: str  # TODO: ???
    activity_path: str  # represent current activity

    """indicating whether this essential state has been matched by agent's task
    execution traces"""
    matched: bool = False
    capture_id = None


class EssentialStates:
    def __init__(self, episode: str, checkpoint_dir: str):
        self.episode: str = episode
        self.checkpoint_dir: str = checkpoint_dir
        self.essential_states: List[EssentialState] = []
        self._load_essential_states()

    def get_essential_states(self) -> List[EssentialState]:
        return self.essential_states

    def get_fuzzy_match_essential_states(self) -> List[EssentialState]:
        return [es for es in self.essential_states if es.keyword == "fuzzy_match"]

    def get_fuzzy_match_list(self) -> List[Dict[str, int]]:
        """
        Return: a fuzzy match list, each item contains pic_id and node_id

        Example: [
            {
                "pic_id": int,
                "node_id": int,
            },
            {},
            ...
        ]
        """
        fuzzy_match_list = []
        pic_id_dict = dict()
        for i in range(len(self.essential_states)):
            if self.essential_states[i].pic_id not in pic_id_dict.keys():
                pic_id_dict[self.essential_states[i].pic_id] = len(fuzzy_match_list)
                if self.essential_states[i].keyword == "fuzzy_match":
                    item = {
                        "pic_id": self.essential_states[i].pic_id,
                        "node_id": self.essential_states[i].node_id,
                    }
                else:
                    item = {"pic_id": self.essential_states[i].pic_id, "node_id": -1}
                fuzzy_match_list.append(item)
            else:
                if self.essential_states[i].keyword == "fuzzy_match":
                    item = {
                        "pic_id": self.essential_states[i].pic_id,
                        "node_id": self.essential_states[i].node_id,
                    }
                    fuzzy_match_list[pic_id_dict[self.essential_states[i].pic_id]] = (
                        item
                    )
                else:
                    continue

        return fuzzy_match_list

    def get_pic_exactly_match_list(self, pic_id: int) -> List[EssentialState]:
        """Except for fuzzy_match, all keywords should be exactly matched."""
        exactly_match_list: List[EssentialState] = []
        for i in range(len(self.essential_states)):
            if (
                self.essential_states[i].pic_id == pic_id
                and "fuzzy_match" not in self.essential_states[i].keyword
            ):
                exactly_match_list.append(self.essential_states[i])
        return exactly_match_list

    def _load_essential_states(self):
        """Load essential states from dir"""
        checkpoint_file_list = [
            f for f in os.listdir(self.checkpoint_dir) if f.split(".")[-1] == "text"
        ]
        # checkpoint_file_list: [8_drawed.png.text, 5_drawed.png.text] will sort by [5, 8]
        # Result will be [5_drawed.png.text, 8_drawed.png.text]
        checkpoint_file_list.sort(key=lambda x: int(x.split("_")[0]))
        for checkpoint_file in checkpoint_file_list:
            pic_id: int = int(checkpoint_file.split("_")[0])
            checkpoint_file_path = os.path.join(self.checkpoint_dir, checkpoint_file)
            with open(checkpoint_file_path, "r") as f:
                content = f.read()
                # split_content: ['keyword<id>', '...'], e.g., ['textbox<10>', 'click<72>']
                split_content = [item.strip() for item in content.split("|") if item]
                for item in split_content:
                    match = re.search(r"(?P<keyword>\w+)<(?P<content>.+)>", item)
                    if match:
                        keyword: str = match.group("keyword")
                        content: int = int(match.group("content"))
                        self.essential_states.append(
                            EssentialState(
                                pic_id=pic_id,
                                ui_state=UIState(
                                    screenshot_path=os.path.join(
                                        self.checkpoint_dir, f"{pic_id}.png"
                                    ),
                                    vh_path=os.path.join(
                                        self.checkpoint_dir, f"{pic_id}.xml"
                                    ),
                                    vh_json_path=os.path.join(
                                        self.checkpoint_dir, f"{pic_id}.json"
                                    ),
                                    activity=DatasetHelper._extract_activity_from_file(
                                        os.path.join(
                                            self.checkpoint_dir, f"{pic_id}.activity"
                                        )
                                    ),
                                    action=DatasetHelper._extract_actions_from_file(
                                        os.path.join(
                                            self.checkpoint_dir, f"{pic_id}.action"
                                        )
                                    ),
                                ),
                                keyword=keyword,
                                node_id=content,
                                activity_path=os.path.join(
                                    self.checkpoint_dir, f"{pic_id}.activity"
                                ),
                            )
                        )

    def print_essential_states(self):
        print(f"Essential states for episode: {self.episode}")
        checkpoint_list = self.essential_states
        for i in range(len(checkpoint_list)):
            print(f"\tessential_state: {i}")
            print(f"\tpic_id: {checkpoint_list[i].pic_id}")
            print(f"\tkeyword: {checkpoint_list[i].keyword}")
            print(f"\tnode_id: {checkpoint_list[i].node_id}")
            print(f"\tmatched: {checkpoint_list[i].matched}")
            print(f"\tcapture_id: {checkpoint_list[i].capture_id}")
            print("\t-------------------------")
