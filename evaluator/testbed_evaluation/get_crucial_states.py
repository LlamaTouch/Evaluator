import os
import re
from typing import List, NamedTuple


class CrucialState(NamedTuple):
    pic_id: int
    node_id: int
    keyword: str
    vh_path: str  # represent which vh file this crucial state belongs to
    matched: bool = False
    capture_id = None


class CrucialStates:
    def __init__(self, episode: str, checkpoint_dir: str):
        self.episode: str = episode
        self.checkpoint_dir: str = checkpoint_dir
        self.crucial_states: List[CrucialState] = []
        self._load_crucial_states()

    def get_crucial_states(self) -> List[CrucialState]:
        return self.crucial_states

    def get_fuzzy_match_list(self):
        """
        function:返回fuzzy match list, each item contains pic_id and node_id
        output: list of pair of pic_id and node_id
        """
        fuzzy_match_list = []
        pic_id_dict = dict()
        for i in range(len(self.crucial_states)):
            if self.crucial_states[i].pic_id not in pic_id_dict.keys():
                pic_id_dict[self.crucial_states[i].pic_id] = len(fuzzy_match_list)
                if self.crucial_states[i].keyword == "fuzzy_match":
                    item = {
                        "pic_id": self.crucial_states[i].pic_id,
                        "node_id": self.crucial_states[i].node_id,
                    }
                else:
                    item = {"pic_id": self.crucial_states[i].pic_id, "node_id": -1}
                fuzzy_match_list.append(item)
            else:
                if self.crucial_states[i].keyword == "fuzzy_match":
                    item = {
                        "pic_id": self.crucial_states[i].pic_id,
                        "node_id": self.crucial_states[i].node_id,
                    }
                    fuzzy_match_list[pic_id_dict[self.crucial_states[i].pic_id]] = item
                else:
                    continue

        return fuzzy_match_list

    def get_pic_exactly_match_list(self, pic_id: int) -> List[CrucialState]:
        """
        function: 根据pic_id, 返回该pic_id下的exactly checkpoint list
        input: pic_id 标准流程中的某一步的state
        output: exactly_match_list: 该pic_id下的exactly checkpoint list
        """
        exactly_match_list: List[CrucialState] = []
        for i in range(len(self.crucial_states)):
            if (
                self.crucial_states[i].pic_id == pic_id
                and "fuzzy_match" not in self.crucial_states[i].keyword
            ):
                exactly_match_list.append(self.crucial_states[i])
        return exactly_match_list

    def _load_crucial_states(self):
        """Load crucial states from dir"""
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
                        self.crucial_states.append(
                            CrucialState(
                                pic_id=pic_id,
                                keyword=keyword,
                                node_id=content,
                                vh_path=f"{pic_id}.xml",
                            )
                        )

    def print_crucial_states(self):
        print(f"Crucial states for episode: {self.episode}")
        checkpoint_list = self.crucial_states
        for i in range(len(checkpoint_list)):
            print(f"\tcrucial_state: {i}")
            print(f"\tpic_id: {checkpoint_list[i].pic_id}")
            print(f"\tkeyword: {checkpoint_list[i].keyword}")
            print(f"\tnode_id: {checkpoint_list[i].node_id}")
            print(f"\tmatched: {checkpoint_list[i].matched}")
            print(f"\tcapture_id: {checkpoint_list[i].capture_id}")
            print("\t-------------------------")
