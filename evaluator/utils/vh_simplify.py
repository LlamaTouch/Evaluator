import xml.etree.ElementTree as ET
import numpy as np
import ast
from typing import List, Dict


def generate_id(element, parent_ids=None):
    if parent_ids is None:
        parent_ids = []

    # Get the index of the element among its siblings
    index = element.get("index") if element.tag != "hierarchy" else "0"
    # Generate the path string by joining parent IDs and current index
    current_id = "".join(parent_ids + [index])

    # Add the generated ID as a new attribute 'id'
    element.set("id", current_id)

    # Recursively call generate_id for children elements
    for child in element:
        generate_id(child, parent_ids + [index])


def filter_condition(item):
    null_state = ["", None]
    switch_class = [
        "android.widget.Switch",
        "android.widget.CheckBox",
        "android.widget.RadioButton",
        "android.widget.ToggleButton",
        "android.widget.Button",
        "android.widget.ImageButton",
        "android.widget.ImageView",
        "android.widget.TextView",
        "android.widget.EditText",
        "android.widget.ProgressBar",
        "android.widget.SeekBar",
        "android.widget.Spinner",
    ]
    condition = (
        item.get("child_count") == 0
        and item.get("visible") == True
        and (
            item.get("text", None) not in null_state
            or item.get("content_description", None) not in null_state
            or item.get("class", None) in switch_class
        )
        # and "Image" not in item.get("class")
        # and "Button" not in item.get("class")
        and "Menu" not in item.get("class")
        and item.get("class") != "android.view.ViewGroup"
        and item.get("class") != "android.widget.FrameLayout"
        and item.get("class") != "android.widget.LinearLayout"
        and item.get("class") != "android.widget.RelativeLayout"
        and item.get("class") != "android.widget.HorizontalScrollView"
    )
    return condition


def extract_clickable_components(root) -> List[Dict]:
    elements = []
    # Iterate through XML elements
    for elem in root.iter():
        if (
            elem.tag == "node"
            and elem.get("clickable") == "true"
            and elem.get("class") != "android.view.ViewGroup"
            and elem.get("class") != "android.widget.FrameLayout"
            and elem.get("class") != "android.widget.LinearLayout"
            and elem.get("class") != "android.widget.RelativeLayout"
            and elem.get("class") != "android.widget.HorizontalScrollView"
        ):
            # Extract desired attributes
            element_info = {
                "id": elem.get("id"),
                "class": elem.get("class"),
                "text": elem.get("text"),
                "resource-id": elem.get("resource-id"),
                "content-desc": elem.get("content-desc"),
                "bounds": elem.get("bounds"),
                "clickable": elem.get("clickable"),
            }
            elements.append(element_info)
    return elements


def extract_ui_positions_from_vh(xml_path: str) -> np.ndarray[np.ndarray]:
    xml_root = ET.parse(xml_path).getroot()
    ui_positions = []
    ui_components = extract_clickable_components(xml_root)
    for item in ui_components:
        # convert string "[x,y][x,y]" to "[x,y],[x,y]", and then eval it
        temp = ast.literal_eval(item["bounds"].replace("][", "],["))
        # convert [[x, y], [x1, y1]] to (y, x, height, width)
        y, x = temp[0][1], temp[0][0]
        height, width = temp[1][1] - y, temp[1][0] - x
        # normalize (y, x, height, width)
        bounds = np.array([y, x, height, width], dtype=np.int64)
        ui_positions.append(bounds)
    return np.array(ui_positions)
