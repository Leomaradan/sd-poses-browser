import os
from pathlib import Path
import modules.scripts as scripts
from modules.paths_internal import data_path


def preload(parser):
    default_poses_dir = Path(scripts.basedir()) / "poses"
    parser.add_argument("--poses-dir", type=str, help="Path to directory with poses files.", default=default_poses_dir)
