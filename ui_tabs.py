import gradio as gr
import html
import os
import helpers

class Pose:
    def __init__(self, preview):
        self.preview = preview
        self.pose = None
        self.depth = None
        self.canny = None
        self.desc = None

class PosesBrowserPage:
    def __init__(self):
        self.poses_dir = helpers.get_poses_dir()
        self.pose_token = helpers.get_token_pose()
        self.depth_token = helpers.get_token_depth()
        self.canny_token = helpers.get_token_canny()

        images = helpers.img_path_get(self.poses_dir)

        preview_images, poses, depths, cannys, descs = self.filter_images(images)

        self.tags = helpers.get_tags(preview_images, self.poses_dir)

        self.poses = self.construct_poses(
            preview=preview_images,
            poses=poses,
            depths=depths,
            cannys=cannys,
            descs=descs,
        )

        self.initial_preview = self.get_preview()
        self.preview = self.initial_preview

    def filter_images(self, images: list[str]):
        preview = []
        poses = []
        depths = []
        canny = []
        desc = []
        for image in images:
            if "." + self.pose_token + "." in image:
                poses.append(image)
            elif "." + self.depth_token + "." in image:
                depths.append(image)
            elif "." + self.canny_token + "." in image:
                canny.append(image)
            elif image.endswith(".txt"):
                desc.append(image)
            else:
                preview.append(image)

        return preview, poses, depths, canny, desc

    def construct_poses(
        self,
        preview: list[str],
        poses: list[str],
        depths: list[str],
        cannys: list[str],
        descs: list[str],
    ):
        full_images = []
        for image in preview:
            full_image = Pose(image)
            image_name, image_ext = os.path.splitext(image)

            try:
                pose = image_name + "." + self.pose_token + image_ext
                pose_index = poses.index(pose)
                full_image.pose = poses.pop(pose_index)
            except ValueError:
                full_image.pose = None

            try:
                depth = image_name + "." + self.depth_token + image_ext
                depth_index = depths.index(depth)
                full_image.depth = depths.pop(depth_index)
            except ValueError:
                full_image.depth = None

            try:
                canny = image_name + "." + self.canny_token + image_ext
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

    def get_preview(self):
        preview = []
        for pose in self.poses:
            if pose.desc is not None:
                preview.append([pose.preview, pose.desc])
            else:
                preview.append(pose.preview)
        return preview

    def filter_poses(self, tag: str):
        buttons = self.get_buttons(tag)
        if tag == "":
            self.preview = self.initial_preview
            return self.initial_preview, buttons

        filtered = []

        for prev in self.initial_preview:
            if type(prev) is list:
                preview_img = prev[0]
            else:
                preview_img = prev

            if tag in preview_img:
                filtered.append(prev)

        self.preview = filtered
        return filtered, buttons

    def get_select_index(self, evt: gr.SelectData):
        # Find the image path from index
        image = self.preview[evt.index]

        if type(image) is list:
            preview_img = image[0]
        else:
            preview_img = image

        # Find the pose from image path
        found_pose = None
        for pose in self.poses:
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

            self.found_pose = found_pose

            return found_pose.pose, depth_updater, canny_updater, updater, updater

        return None, None, None, updater, updater

    def get_buttons(self, search_textbox: str):

        subdirs_html = "".join(
            [
                f"""
    <button class='lg gradio-button custom-button{" primary" if tag==search_textbox else " secondary"}' onclick='poses_browser_filter("{tag}")'>
    {html.escape(tag if tag!="" else "all")}
    </button>
    """
                for tag in self.tags
            ]
        )

        return subdirs_html

    def on_ui_tabs(self):


        with gr.Blocks(analytics_enabled=False) as ui_component:
            with gr.Row():
                with gr.Column(scale=2):
                    search_textbox = gr.Textbox(
                        "",
                        show_label=False,
                        elem_id="poses_browser_search",
                        visible=False,
                    )
                    with gr.Row():
                        buttons_html = gr.HTML(self.get_buttons(""))
                    with gr.Row():
                        gallerie = gr.Gallery(
                            value=self.preview,
                            preview=False,
                            allow_preview=False,
                            show_label=True,
                        ).style(
                            columns=[4], rows=[4], object_fit="contain", height="auto"
                        )
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
                    self.get_select_index,
                    None,
                    [
                        pose_image,
                        depth_image,
                        canny_image,
                        txt2img_button,
                        img2img_button,
                    ],
                )
                txt2img_button.click(fn=None, _js="poses_browser_send_txt2img")
                img2img_button.click(fn=None, _js="poses_browser_send_img2img")

                search_textbox.change(
                    fn=self.filter_poses, inputs=search_textbox, outputs=[gallerie, buttons_html]
                )

            return [(ui_component, "Poses Browser", "poses_browser")]
