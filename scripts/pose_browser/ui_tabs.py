import gradio as gr
import logging
import html
import os
from pathlib import Path
from modules import shared, scripts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

is_debug = getattr(shared.opts, "is_debug", False)

if is_debug:
    logger.setLevel(logging.DEBUG)

base_dir = Path(scripts.basedir())

class Pose:
    def __init__(self, preview):
        self.preview = preview
        self.pose = None
        self.depth = None
        self.canny = None
        self.desc = None

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

def filter_images(
    images: list[str], pose_token: str, depth_token: str, canny_token: str
):
    preview = []
    poses = []
    depths = []
    canny = []
    desc = []
    for image in images:
        if "." + pose_token + "." in image:
            poses.append(image)
        elif "." + depth_token + "." in image:
            depths.append(image)
        elif "." + canny_token + "." in image:
            canny.append(image)
        elif image.endswith(".txt"):
            desc.append(image)
        else:
            preview.append(image)

    return preview, poses, depths, canny, desc

def construct_poses(
    preview: list[str],
    poses: list[str],
    depths: list[str],
    cannys: list[str],
    descs: list[str],
    pose_token: str,
    depth_token: str,
    canny_token: str,
):
    full_images = []
    for image in preview:
        full_image = Pose(image)
        image_name, image_ext = os.path.splitext(image)

        try:
            pose = image_name + "." + pose_token + image_ext
            pose_index = poses.index(pose)
            full_image.pose = poses.pop(pose_index)
        except ValueError:
            full_image.pose = None

        try:
            depth = image_name + "." + depth_token + image_ext
            depth_index = depths.index(depth)
            full_image.depth = depths.pop(depth_index)
        except ValueError:
            full_image.depth = None

        try:
            canny = image_name + "." + canny_token + image_ext
            canny_index = cannys.index(canny)
            full_image.canny = cannys.pop(canny_index)
        except ValueError:
            full_image.canny = None

        try:
            desc = image_name + ".txt"
            desc_index = descs.index(desc)
            desc_file = descs.pop(desc_index)
            with open(desc_file, "r") as f:
                full_image.desc = f.read()

        except ValueError:
            full_image.desc = None

        full_images.append(full_image)

    return full_images

def get_preview(poses: list[Pose]):
    preview = []
    for pose in poses:
        if pose.desc is not None:
            preview.append([pose.preview, pose.desc])
        else:
            preview.append(pose.preview)
    return preview

def on_ui_tabs():
    poses_dir = get_poses_dir()
    pose_token = get_token_pose()
    depth_token = get_token_depth()
    canny_token = get_token_canny()

    images = img_path_get(poses_dir)

    preview_images, poses, depths, cannys, descs = filter_images(
        images, pose_token, depth_token, canny_token
    )

    tags = get_tags(preview_images, poses_dir)

    poses = construct_poses(
        preview=preview_images,
        poses=poses,
        depths=depths,
        cannys=cannys,
        descs=descs,
        pose_token=pose_token,
        depth_token=depth_token,
        canny_token=canny_token,
    )

    preview = get_preview(poses)

    def filter_poses(tag: str):
        if tag == "":
            return preview

        filtered = []

        for prev in preview:
            if type(prev) is list:
                preview_img = prev[0]
            else:
                preview_img = prev

            if tag in preview_img:
                filtered.append(prev)

        return filtered

    def get_select_index(evt: gr.SelectData):
        # Find the image path from index
        image = preview[evt.index]

        if type(image) is list:
            preview_img = image[0]
        else:
            preview_img = image

        # Find the pose from image path
        found_pose = None
        for pose in poses:
            if pose.preview == preview_img:
                found_pose = pose
                break

        depth_updater = gr.Image.update(value=None, visible=False)
        canny_updater = gr.Image.update(value=None, visible=False)
        updater = gr.Button.update(interactive=False)

        if found_pose:
            if found_pose.depth:
                depth_updater = gr.Image.update(value=found_pose.depth, visible=True)
            if found_pose.canny:
                canny_updater = gr.Image.update(value=found_pose.canny, visible=True)
            updater = gr.Button.update(interactive=True)

            return found_pose.pose, depth_updater, canny_updater, updater, updater

        return None, None, None, updater, updater

    subdirs_html = "".join(
        [
            f"""
<button class='lg secondary gradio-button custom-button{" search-all" if tag=="" else ""}' onclick='poses_browser_filter("{tag}")'>
{html.escape(tag if tag!="" else "all")}
</button>
"""
            for tag in tags
        ]
    )

    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            with gr.Column(scale=2):
                search_textbox = gr.Textbox(
                    "", show_label=False, elem_id="poses_browser_search", visible=False
                )
                with gr.Row():
                    gr.HTML(subdirs_html)
                with gr.Row():
                    gallerie = gr.Gallery(
                        value=preview,
                        preview=False,
                        allow_preview=False,
                        show_label=True,
                    ).style(columns=[4], rows=[4], object_fit="contain", height="auto")
            with gr.Column(scale=1):
                txt2img_button = gr.Button(
                    interactive=False,
                    value="Send to txt2img",
                    elem_id="poses_browser_txt2img_button",
                )
                img2img_button = gr.Button(
                    interactive=False,
                    value="Send to img2img",
                    elem_id="poses_browser_img2img_button",
                )
                pose_image = gr.Image(
                    # value=selected.value.pose if selected.value else None,
                    label="Pose",
                    interactive=False,
                    elem_id="poses_browser_pose_image",
                ).style(object_fit="contain", height=300)
                depth_image = gr.Image(
                    # value=selected.value.depth if selected.value else None,
                    label="Depth",
                    interactive=False,
                    visible=False,
                    elem_id="poses_browser_depth_image",
                ).style(object_fit="contain", height=300)
                canny_image = gr.Image(
                    # value=selected.value.depth if selected.value else None,
                    label="Canny",
                    interactive=False,
                    visible=False,
                    elem_id="poses_browser_canny_image",
                ).style(object_fit="contain", height=300)

            gallerie.select(
                get_select_index,
                None,
                [pose_image, depth_image, canny_image, txt2img_button, img2img_button],
            )
            txt2img_button.click(fn=None, _js="poses_browser_send_txt2img")
            img2img_button.click(fn=None, _js="poses_browser_send_img2img")

            search_textbox.change(
                fn=filter_poses, inputs=search_textbox, outputs=gallerie
            )

        return [(ui_component, "Poses Browser", "poses_browser")]
