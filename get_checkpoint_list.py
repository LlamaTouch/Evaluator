import os

class Checkpoint:
    def __init__(self, pic_id, keyword, node_id):
        self.pic_id = pic_id
        self.keyword = keyword
        self.node_id = node_id
        self.matched = False
        self.capture_id = None

class Checkpoints:
    def __init__(self, checkpoint_dir):
        # self.checkpoint_ls,self.installed_ls = _get_checkpoint_list(checkpoint_dir)
        self.checkpoint_ls  = _get_checkpoint_list(checkpoint_dir)

    def get_fuzzy_match_list(self):
        """
        function:返回fuzzy match list, each item contains pic_id and node_id 
        output: list of pair of pic_id and node_id
        """
        fuzzy_match_list = []
        pic_id_dict = dict()
        for i in range(len(self.checkpoint_ls)):
            if self.checkpoint_ls[i].pic_id not in pic_id_dict.keys():
                pic_id_dict[self.checkpoint_ls[i].pic_id] = len(fuzzy_match_list)
                if self.checkpoint_ls[i].keyword == "fuzzy_match":
                    item = {
                        "pic_id": self.checkpoint_ls[i].pic_id,
                        "node_id": self.checkpoint_ls[i].node_id
                    }
                else:
                    item  ={
                        "pic_id": self.checkpoint_ls[i].pic_id,
                        "node_id": -1
                    }
                fuzzy_match_list.append(item)
            else:
                if self.checkpoint_ls[i].keyword == "fuzzy_match":
                    item = {
                        "pic_id": self.checkpoint_ls[i].pic_id,
                        "node_id": self.checkpoint_ls[i].node_id
                    }
                    fuzzy_match_list[pic_id_dict[self.checkpoint_ls[i].pic_id]] = item
                else:
                    continue

        return fuzzy_match_list
    
    def get_pic_exactly_match_list(self, pic_id):
        """
        function: 根据pic_id, 返回该pic_id下的exactly checkpoint list
        input: pic_id 标准流程中的某一步的state
        output: exactly_match_list: 该pic_id下的exactly checkpoint list
        """
        exactly_match_list = []
        for i in range(len(self.checkpoint_ls)):
            if self.checkpoint_ls[i].pic_id == pic_id and "fuzzy_match" not in self.checkpoint_ls[i].keyword:
                exactly_match_list.append(self.checkpoint_ls[i])
        return exactly_match_list


def _get_checkpoint_list(checkpoint_dir):
    """
    function: 根据标注完的文件夹, 返回checkpoint列表
    input: checkpoint_dir: 标注完之后的文件夹
    output: checkpoint_list: checkpoint列表
    """
    checkpoint_file_list = [f for f in os.listdir(checkpoint_dir) if f.split(".")[-1] == "text"]
    checkpoint_file_list.sort(key=lambda x: int(x.split(".")[0][:-7]))
    checkpoint_ls = []
    # installed_ls = []
    for checkpoint_file in checkpoint_file_list:
        pic_id = checkpoint_file.split(".")[0][:-7]
        # 每个文件中的内容格式为 "keyword<content>|keyword<content>|keyword<content>|..."
        checkpoint_file_path = os.path.join(checkpoint_dir, checkpoint_file)
        with open(checkpoint_file_path, "r") as f:
            content = f.read()
            split_content = [item.strip() for item in content.split('|') if item]
            # 进一步解析每个字符串
            # parsed_content = []
            for item in split_content:
                # 格式总是 "keyword<content>"
                parts = item.split('<')
                if len(parts) == 2:
                    keyword, content = parts[0], parts[1].rstrip('>')
                    keyword = keyword.strip().lower()
                    # if keyword == "check_install":
                    #     installed_ls.append(Checkpoint(int(pic_id), keyword, str(content).lower()))
                    # else:
                    checkpoint_ls.append(Checkpoint(int(pic_id), keyword, content))
                    # parsed_content.append(Checkpoint(int(pic_id), keyword, int(content)))
        # checkpoint_list = checkpoint_ls + parsed_content
    
    return checkpoint_ls


def _print_checkpoint_list(checkpoint_list):
    """
    function: 打印checkpoint列表
    input: checkpoint_list: checkpoint列表
    """
    for i in range(len(checkpoint_list)):
        print(f"checkpoint {i}:")
        print(f"pic_id: {checkpoint_list[i].pic_id}")
        print(f"keyword: {checkpoint_list[i].keyword}")
        print(f"node_id: {checkpoint_list[i].node_id}")
        print(f"matched: {checkpoint_list[i].matched}")
        print(f"capture_id: {checkpoint_list[i].capture_id}")
        print("-------------------------")


    
if __name__ == "__main__":
    checkpoint_dir = "/data/jxq/mobile-agent/aitw_replay_data/general/trace_35"
    checkpoint_ls = Checkpoints(checkpoint_dir)
    fuzy_match_ls = checkpoint_ls.get_fuzzy_match_list()
    print(fuzy_match_ls)
    # _print_checkpoint_list(checkpoint_ls.checkpoint_ls)
    # _print_checkpoint_list(checkpoint_ls.installed_ls)
