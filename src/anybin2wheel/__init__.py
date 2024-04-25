import argparse
import os.path
import re
import sys
import tempfile

from distlib.metadata import Metadata
from distlib.wheel import (
    ARCH,
    Wheel,
)


PROJECT_NAME = "anybin2wheel"
PROJECT_URL = "https://github.com/sergeykolosov/anybin2wheel"

# https://packaging.python.org/en/latest/specifications/name-normalization/#name-format
RE_PACKAGE_NAME = re.compile(
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", re.IGNORECASE
)


class BinWheel(Wheel):
    def process_shebang(self, data):
        # don't add shebang to executables
        return data


def main():
    args = parse_args()
    binary_basename = os.path.splitext(os.path.basename(args.binary))[0]

    if not RE_PACKAGE_NAME.match(args.name):
        sys.stderr.write(
            f"Invalid package name: '{args.name}'. It should match "
            f"'{RE_PACKAGE_NAME.pattern}' (case-insensitive).\n"
        )
        return 2

    package_name = args.name

    summary = args.summary or f"Wheel distribution for {binary_basename}"
    description = args.description or (
        f"# {package_name}\n"
        f"An executable packaged to be distributed as a wheel using [{PROJECT_NAME}]({PROJECT_URL}).\n"
    )
    if args.description_file:
        try:
            with open(args.description_file, "r") as f:
                description = f.read()
        except Exception as e:
            sys.stderr.write(f"Error reading description file: {e}\n")
            return 2

    # https://packaging.python.org/en/latest/specifications/core-metadata/
    metadata = Metadata(
        mapping={
            "name": package_name,
            "version": args.version,
            "summary": summary,
            # As distlib doesn't let the description from headers render nicely,
            # we manually put it into the body instead
            # "description": description,
            "description_content_type": args.description_content_type,
            "home_page": args.home_page,
            "author": args.author,
            "author_email": args.author_email,
            "maintainer": args.maintainer,
            "maintainer_email": args.maintainer_email,
            "license": args.license,
        }
    )

    wheel = BinWheel()
    wheel.name = package_name.replace("-", "_")
    wheel.version = args.version
    wheel.dirname = args.dist_dir

    with tempfile.TemporaryDirectory() as tempdir:
        os.makedirs(os.path.join(tempdir, "platlib", ".dist-info"))
        metadata_file = os.path.join(tempdir, "platlib", ".dist-info", "METADATA")
        with open(metadata_file, "w") as fp:
            metadata.write(fileobj=fp, legacy=True)
            fp.write("\n")
            fp.write(description)

        os.mkdir(os.path.join(tempdir, "scripts"))
        os.link(
            args.binary, os.path.join(tempdir, "scripts", os.path.basename(args.binary))
        )

        paths = {
            "platlib": os.path.join(tempdir, "platlib"),
            "scripts": os.path.join(tempdir, "scripts"),
        }
        tags = {
            "pyver": args.python_tag.split("."),
            "abi": ["none"],
            "arch": args.plat_name.split("."),
        }
        wheel_filename = wheel.build(paths, tags=tags, wheel_version=(1, 0))
        print(wheel_filename)

        return 0


def parse_args():
    parser = argparse.ArgumentParser(
        description="Package any executable as a Python wheel."
    )
    parser.add_argument("binary", help="Path to the executable to be packaged.")
    parser.add_argument("name", help="Name of the package.")
    parser.add_argument("version", help="Version of the package.")

    # bdist_wheel-like options
    parser.add_argument(
        "-d", "--dist-dir", help="Destination directory for the wheel.", default="."
    )
    parser.add_argument(
        "-p",
        "--plat-name",
        help="Platform for the package. Defaults to current one.",
        default=ARCH,
    )
    parser.add_argument(
        "--python-tag",
        help="Python compatibility tag. Defaults to 'py2.py3'.",
        default="py2.py3",
    )

    # metadata: for now, only the most essential fields
    parser.add_argument("--summary", help="Package metadata: summary.")
    parser.add_argument(
        "--description",
        help="Package metadata: description.",
    )
    parser.add_argument(
        "--description-content-type",
        help="Package metadata: description content type.",
        default="text/markdown",
        choices=["text/x-rst", "text/plain", "text/markdown"],
    )
    parser.add_argument(
        "--description-file",
        help="Package metadata: read description from a file.",
    )
    parser.add_argument("--home-page", help="Package metadata: home page URL.")
    parser.add_argument("--author", help="Package metadata: author.")
    parser.add_argument("--author-email", help="Package metadata: author email.")
    parser.add_argument("--maintainer", help="Package metadata: maintainer.")
    parser.add_argument(
        "--maintainer-email", help="Package metadata: maintainer email."
    )
    parser.add_argument("--license", help="Package metadata: license.")

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
