from ..agent import AppAgent


def test_load_ui_annotations():
    aa = AppAgent()
    # print(aa.load_predicted_action_by_episode("339077771907758195"))
    ui_annotation_positions = aa.load_AITW_episode_ui_positions("339077771907758195")
    print(len(ui_annotation_positions))
    print(type(ui_annotation_positions))
    print(type(ui_annotation_positions[0]))
    print(type(ui_annotation_positions[0][0]))
    print(type(ui_annotation_positions[0][0][0]))
    for item in ui_annotation_positions:
        print(item)
    aa.load_AITW_episode_actions("339077771907758195")
    assert False  # make pytest failed to show print info
