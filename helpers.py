import logging
import os
from pathlib import Path
from modules import shared, scripts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

is_debug = getattr(shared.opts, "is_debug", False)

if is_debug:
    logger.setLevel(logging.DEBUG)

base_dir = Path(scripts.basedir())

def get_tags(images: list[str], poses_dir: Path = None):
    tags = set([""])
    for image in images:
        image_dir = str(os.path.dirname(image))
        image_name = image_dir.replace(str(poses_dir) + "/", "")

        image_parts = image_name.split("/")

        image_part = ""
        for i in range(len(image_parts)):
            if i == 0:
                image_part = image_parts[i]
            else:
                image_part = image_part + "/" + image_parts[i]
            tags.add(image_part)
    return list(tags)


def get_poses_dir() -> Path:
    poses_dir = getattr(shared.opts, "poses_dir", None)

    if poses_dir is None or poses_dir == "":
        poses_dir = base_dir / "poses"
    poses_dir = Path(poses_dir)
    try:
        poses_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        logger.exception(f"Failed to create poses directory {poses_dir}")
    return poses_dir


def get_token_pose() -> str:
    token = getattr(shared.opts, "poses_browser_pose_name", None)
    if token is None:
        token = "pose"
    return token

def get_token_depth() -> str:
    token = getattr(shared.opts, "poses_browser_depth_name", None)
    if token is None:
        token = "depth"
    return token

def get_token_canny() -> str:
    token = getattr(shared.opts, "poses_browser_canny_name", None)
    if token is None:
        token = "canny"
    return token

def img_path_get(img_path):
    images = []
    for item in os.listdir(img_path):
        item_path = os.path.join(img_path, item)
        if os.path.isfile(item_path):
            images.append(item_path)
        elif os.path.isdir(item_path):
            images += img_path_get(item_path)
    return images