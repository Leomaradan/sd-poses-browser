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


def log_debug(message: str):
    """
    Log a debug message.
    """
    logger.debug(message)


def get_tags(images: list[str], poses_dir: Path = None):
    """
    Get the list of tags based on images paths relative to the poses directory.
    If an image is in a deep subdirectory of the poses directory, the subdirectory is used as tag.
    Example: A pose image is in the directory "character/man/pose.png", generated tags will be  "character" and "character/tags".
    """
    tags = set([""])
    poses_dir_str = str(poses_dir)

    log_debug("poses_dir " + str(poses_dir))

    for image in images:
        image_dir = str(os.path.dirname(image))
        log_debug("image_dir " + image_dir)

        if poses_dir_str == image_dir:
            image_name = ""
        else:
            image_name = image_dir.replace(poses_dir_str + "/", "")
        log_debug("image_name " + image_name + " for image source " + image)

        image_parts = image_name.split("/")

        image_part = ""
        for i in range(len(image_parts)):
            if i == 0:
                image_part = image_parts[i]
            else:
                image_part = image_part + "/" + image_parts[i]
            tags.add(image_part)
    log_debug("tags " + str(tags))
    return list(tags)


def get_poses_dir() -> Path:
    """
    Get the path to the directory where pose images are stored.
    """
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
    """
    Get the token used to identify pose images.
    """
    token = getattr(shared.opts, "poses_browser_pose_name", None)
    if token is None:
        token = "pose"
    return token


def get_token_depth() -> str:
    """
    Get the token used to identify depth images.
    """
    token = getattr(shared.opts, "poses_browser_depth_name", None)
    if token is None:
        token = "depth"
    return token


def get_token_canny() -> str:
    """
    Get the token used to identify canny images.
    """
    token = getattr(shared.opts, "poses_browser_canny_name", None)
    if token is None:
        token = "canny"
    return token


def img_path_get(img_path):
    """
    Recursively get all images in a directory and its subdirectories, ignoring hidden files and directories.
    """
    images = []
    for item in os.listdir(img_path):
        item_path = os.path.join(img_path, item)
        if str(item).startswith("."):
            continue
        if os.path.isfile(item_path):
            images.append(item_path)
        elif os.path.isdir(item_path):
            images += img_path_get(item_path)
    return images
