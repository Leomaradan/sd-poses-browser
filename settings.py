from modules import shared


def on_ui_settings():
    """
    Settings page for the Poses Browser.
    """
    section = ("poses_browser", "Poses Browser")

    poses_browser_options = [
        ("poses_dir", "", "Poses directory"),
        ("poses_browser_pose_name", "pose", "Pose token in filename"),
        ("poses_browser_depth_name", "depth", "Depth token in filename"),
        ("poses_browser_canny_name", "canny", "Canny token in filename"),
    ]

    for cur_setting_name, default_option, description in poses_browser_options:
        shared.opts.add_option(
            cur_setting_name,
            shared.OptionInfo(
                default=default_option,
                label=description,
                section=section,
            ).needs_restart(),
        )
