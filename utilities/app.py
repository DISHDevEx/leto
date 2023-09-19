import pathlib
import subprocess
import sys

from config_handler import ConfigHandler

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

def main():
    path = str(pathlib.Path(__file__).parent.absolute())
    # path = str(pathlib.Path(__file__))
    print(path)

    if "leto" in path:
        print("it's in leto")
    else:
        print('nah dawg')

    config = ConfigHandler("reduction.fps_bitrate")
    s3_args = config.s3
    method_args = config.method

    section = config.method_section
    print(type(section))
    print(config.method_section)

if __name__ == "__main__":
    main()