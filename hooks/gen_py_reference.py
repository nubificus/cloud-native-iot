# SPDX-License-Identifier: Apache-2.0

import logging
import pkgutil
import sys
from pathlib import Path

from mkdocs.structure.files import File

HOOK_NAME = Path(__file__).stem
log = logging.getLogger(f"mkdocs.hooks.{HOOK_NAME}")


def get_hook_config(config):
    """Returns the hook's config section."""
    return config["extra"].get(f"{HOOK_NAME}", {})


def get_mkdocstrings_paths(config):
    """Returns the mkdocstrings' config section."""
    plugin = config["plugins"].get("mkdocstrings")
    if plugin:
        return plugin.config.get("handlers", {}).get("python", {}).get("paths", []) or [
            "src",
        ]
    return ["src"]


def find_top_level_packages(source_path: Path):
    """Discovers the top-level packages."""
    if not source_path.is_dir():
        return []
    return [
        name
        for _, name, ispkg in pkgutil.iter_modules([str(source_path)])
        if ispkg and (source_path / name).is_dir()
    ]


def walk_modules_in_package(package_path, package_prefix):
    """Recursively walks through package modules and returns module names."""
    init_path = Path(package_path) / "__init__.py"
    if init_path.is_file():
        yield package_prefix.rstrip(".") + ".__init__"

    for _, mod_name, ispkg in pkgutil.walk_packages(
        [str(package_path)],
        prefix=package_prefix,
    ):
        name_parts = mod_name.split(".")

        # Skip any modules or subpackages starting with "_"
        if any(part.startswith("_") for part in name_parts):
            continue

        if ispkg:
            # If it's a subpackage, continue walking
            subpackage_path = Path(package_path) / name_parts[-1]
            yield from walk_modules_in_package(subpackage_path, mod_name + ".")
        else:
            yield mod_name


def on_files(files, config):
    """Generates virtual markdown files for packages."""
    log.info("Generating Python API reference")

    hook_config = get_hook_config(config)
    source_paths = get_mkdocstrings_paths(config)
    out_path = hook_config.get("out_path", "reference")

    for source_path in source_paths:
        abs_path = Path(source_path).resolve()
        if abs_path not in sys.path:
            sys.path.insert(0, abs_path)

        for pkg_name in find_top_level_packages(abs_path):
            pkg_path = abs_path / pkg_name
            prefix = f"{pkg_name}."

            for mod_name in walk_modules_in_package(pkg_path, prefix):
                parts = mod_name.split(".")
                if parts[-1] == "__init__":
                    # Skip actual "__init__" name in path, use index.md instead
                    rel_path = Path(out_path) / Path(*parts[:-1]) / "index.md"
                    mod_display_name = ".".join(parts[:-1])
                else:
                    rel_path = Path(out_path) / Path(*parts).with_suffix(".md")
                    mod_display_name = mod_name

                content_string = f"::: {mod_display_name}"
                file = File.generated(config, rel_path, content=content_string)
                files.append(file)

    return files


def on_page_markdown(markdown, page, config, files):
    """Sets module file names as page titles."""
    hook_config = get_hook_config(config)
    out_path = Path(hook_config.get("out_path", "reference"))
    page_path = Path(page.file.src_uri)
    if page_path.is_relative_to(out_path) and page_path.name != "index.md":
        page.title = page.file.name
