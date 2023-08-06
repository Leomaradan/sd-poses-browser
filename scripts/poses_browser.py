from modules import script_callbacks
import settings
from ui_tabs import PosesBrowserPage

ui_tabs = PosesBrowserPage()

script_callbacks.on_ui_tabs(ui_tabs.on_ui_tabs)
script_callbacks.on_ui_settings(settings.on_ui_settings)
