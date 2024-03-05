from ..utils.vh_simplify import extract_ui_positions_from_vh


def test_xml_items():
    xml_path = "./test_asset/1.xml"
    extract_ui_positions_from_vh(xml_path)

    xml_path = "./test_asset/2.xml"
    extract_ui_positions_from_vh(xml_path)

    assert False
