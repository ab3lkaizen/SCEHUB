import contextlib
import ctypes
import glob
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile
from typing import NoReturn

import requests

logger = logging.getLogger("CLI")


def download_innoextract(output_path: str, max_retries: int = 3) -> int:
    for attempt in range(max_retries):
        try:
            response = requests.get(
                "https://api.github.com/repos/dscharrer/innoextract/releases/latest",
                timeout=5,
            )
            response.raise_for_status()

            data = response.json()

            for asset in data["assets"]:
                file_name = asset["name"]
                if file_name.endswith("windows.zip"):
                    response = requests.get(asset["browser_download_url"], timeout=5)
                    response.raise_for_status()

                    temp_dir = tempfile.gettempdir()
                    file_path = os.path.join(temp_dir, file_name)

                    with open(file_path, "wb") as file:
                        file.write(response.content)

                    with zipfile.ZipFile(file_path, "r") as file:
                        file.extract("innoextract.exe", output_path)

            return 0  # indicate success

        except (requests.RequestException, zipfile.BadZipFile) as e:
            logger.warning(f"innoextract: Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info("Retrying after 5 seconds...")
                time.sleep(5)
                continue
            else:
                logger.error("Max retries exceeded. Download failed.")
                return 1

    return 1  # indicate failure: all retries failed without attempting download and extraction


def download_scripts(output_path: str, max_retries: int = 3) -> int:
    script_urls: list[str] = [
        "https://raw.githubusercontent.com/ab3lkaizen/SCEHUB/main/Export.bat",
        "https://raw.githubusercontent.com/ab3lkaizen/SCEHUB/main/Import.bat",
    ]

    for attempt in range(max_retries):
        for url in script_urls:
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()

                with open(
                    os.path.join(output_path, os.path.basename(url)), "wb"
                ) as file:
                    file.write(response.content)

            except requests.RequestException as e:
                logger.warning(f"scripts: Download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info("Retrying after 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    logger.error("Max retries exceeded. Download failed")
                    return 1

    return 0


def run_main() -> int:
    logging.basicConfig(
        format="[%(name)s] %(levelname)s: %(message)s", level=logging.INFO
    )

    current_dir = os.getcwd()

    if shutil.which("innoextract") is None:
        download_innoextract(current_dir)

    temp_dir = tempfile.gettempdir()
    msi_center_zip = os.path.join(temp_dir, "MSI-Center.zip")
    extract_path = os.path.join(temp_dir, "MSI-Center")

    response = requests.get(
        "https://download.msi.com/uti_exe/desktop/MSI-Center.zip",
        timeout=5,
    )

    # download MSI Center
    with open(msi_center_zip, "wb") as file:
        file.write(response.content)

    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(msi_center_zip, "r") as file:
        file.extractall(extract_path)

    msi_center_installer = glob.glob(os.path.join(extract_path, "MSI Center_*.exe"))

    if not msi_center_installer:
        logger.error("MSI Center executable installer not found")
        return 1

    # get version from file name
    msi_center_ver = re.search(
        r"_([\d.]+)\.exe$",
        os.path.basename(msi_center_installer[0]),
    )

    if not msi_center_ver:
        logger.error("Failed to obtain MSI Center version")
        return 1

    msi_center_version = msi_center_ver.group(1)

    subprocess.call(
        ["innoextract", msi_center_installer[0], "--output-dir", extract_path],
    )

    appxbundle = glob.glob(os.path.join(extract_path, "app", "*.appxbundle"))

    if not appxbundle:
        logger.error("Appx bundle file not found")
        return 1

    appx_file_name = f"MSI%20Center_{msi_center_version}_x64.appx"

    with zipfile.ZipFile(appxbundle[0], "r") as file:
        file.extract(appx_file_name, extract_path)

    msi_center_sdk_path = "DCv2/Package/MSI%20Center%20SDK.exe"

    with zipfile.ZipFile(os.path.join(extract_path, appx_file_name), "r") as file:
        file.extract(msi_center_sdk_path, extract_path)

    subprocess.call(
        [
            "innoextract",
            os.path.join(extract_path, msi_center_sdk_path),
            "--output-dir",
            extract_path,
        ],
    )

    prepackage_path = os.path.join(extract_path, "tmp", "PrePackage")

    engine_lib_installer = glob.glob(os.path.join(prepackage_path, "Engine Lib_*.exe"))

    if not engine_lib_installer:
        logger.error("Engine Lib installer not found")
        return 1

    subprocess.call(
        ["innoextract", engine_lib_installer[0], "--output-dir", extract_path],
    )

    scewin_path = os.path.join(extract_path, "app", "Lib", "SCEWIN")

    scewin_version_folder = glob.glob(os.path.join(scewin_path, "*", ""))
    if not scewin_version_folder:
        logger.error("SCEWIN version folder not found")
        return 1

    # remove residual files
    for file in ("BIOSData.db", "BIOSData.txt", "SCEWIN.bat"):
        with contextlib.suppress(FileNotFoundError):
            os.remove(os.path.join(scewin_version_folder[0], file))

    # download scripts to SCEWIN version folder
    download_scripts(scewin_version_folder[0])

    if not os.path.exists(os.path.join(current_dir, "SCEWIN")):
        shutil.move(scewin_path, ".")

    return 0


def main() -> NoReturn:
    exit_code = 0

    try:
        exit_code = run_main()  # call the main function
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        print(traceback.format_exc())
        exit_code = 1
    finally:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        process_array = (ctypes.c_uint * 1)()
        num_processes = kernel32.GetConsoleProcessList(process_array, 1)

        # only pause if script was run by double-clicking
        if num_processes < 3:
            input("press enter to exit")

        sys.exit(exit_code)


if __name__ == "__main__":
    main()
