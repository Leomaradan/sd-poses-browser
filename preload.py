from pathlib import Path
import modules.scripts as scripts

def preload(parser):
    """
    Add the --poses-dir argument to the parser.
    """
    default_poses_dir = Path(scripts.basedir()) / "poses"
    parser.add_argument(
        "--poses-dir",
        type=str,
        help="Path to directory with poses files.",
        default=default_poses_dir,
    )
