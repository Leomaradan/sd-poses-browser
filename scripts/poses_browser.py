from modules import script_callbacks
import scripts.pose_browser.settings
import scripts.pose_browser.ui_tabs

script_callbacks.on_ui_tabs(scripts.pose_browser.ui_tabs.on_ui_tabs)
script_callbacks.on_ui_settings(scripts.pose_browser.settings.on_ui_settings)