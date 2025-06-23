import os
import re
import sys
import platform
import subprocess
import urllib.parse
import requests
import zipfile
import tarfile
import shutil
from pathlib import Path

# Dictionary to hold translatable messages
MESSAGES = {
    'zh': {
        'tool_title': "Cloudflare Stream视频下载工具",
        'separator': "=" * 50,
        'ffmpeg_not_installed': "FFmpeg未安装，正在尝试自动安装...",
        'ffmpeg_existing_install': "使用已存在的FFmpeg安装: {}",
        'downloading_ffmpeg': "下载FFmpeg: {}",
        'extracting_ffmpeg': "解压FFmpeg...",
        'ffmpeg_installed_at': "FFmpeg已安装到: {}",
        'ffmpeg_exe_not_found': "无法找到ffmpeg.exe，请尝试手动安装",
        'extracted_dir_structure': "解压后的目录结构:",
        'install_failed': "安装失败: {}",
        'trying_pkg_manager': "尝试使用包管理器安装FFmpeg...",
        'ffmpeg_installed_apt': "FFmpeg已通过apt安装",
        'ffmpeg_installed_yum_dnf': "FFmpeg已通过yum/dnf安装",
        'ffmpeg_installed_pacman': "FFmpeg已通过pacman安装",
        'linux_distro_unrecognized': "无法自动识别Linux发行版，请手动安装FFmpeg",
        'linux_commands_ref': "参考命令:",
        'manual_install_mac_other': "无法自动安装FFmpeg，请手动安装:",
        'mac_brew_cmd': "macOS: brew install ffmpeg",
        'other_systems_ref': "其他系统: 请参考 https://ffmpeg.org/download.html",
        'ffmpeg_install_failed_continue': "FFmpeg安装失败，无法继续",
        'ffmpeg_still_unavailable': "FFmpeg仍然不可用，请手动安装",
        'ffmpeg_ready': "FFmpeg已准备好",
        'enter_url_prompt': "请输入Cloudflare Stream URL(包含thumbnails/thumbnail.jpg或manifest/video.m3u8): ",
        'enter_output_filename_prompt': "请输入输出文件名(无需扩展名，将自动添加.mp4): ",
        'default_output_filename': "downloaded_video",
        'converted_url': "转换后的视频流URL:",
        'executing_download_command': "正在执行下载命令:",
        'download_complete': "下载完成! 文件已保存为:",
        'download_failed': "下载失败! FFmpeg返回错误码:",
        'possible_solutions': "可能的解决方案:",
        'check_url_correct': "1. 检查URL是否正确且可访问",
        'try_diff_network': "2. 尝试使用不同的网络连接",
        'ensure_disk_space': "3. 确保有足够的磁盘空间",
        'ffmpeg_execution_error': "执行FFmpeg时出错: {}",
        'url_value_error': "URL必须包含 'thumbnails/thumbnail.jpg' 或 'manifest/video.m3u8'",
        'ensure_url_format': "请确保输入的URL包含'thumbnails/thumbnail.jpg'或'manifest/video.m3u8'",
        'unexpected_error': "发生意外错误: {}",
        'choose_language': "请选择语言 (输入 'zh' 代表中文，'en' 代表英文): ",
        'invalid_language_choice': "无效的选择，默认为中文。",
    },
    'en': {
        'tool_title': "Cloudflare Stream Video Downloader",
        'separator': "=" * 50,
        'ffmpeg_not_installed': "FFmpeg is not installed, attempting automatic installation...",
        'ffmpeg_existing_install': "Using existing FFmpeg installation: {}",
        'downloading_ffmpeg': "Downloading FFmpeg: {}",
        'extracting_ffmpeg': "Extracting FFmpeg...",
        'ffmpeg_installed_at': "FFmpeg installed at: {}",
        'ffmpeg_exe_not_found': "Could not find ffmpeg.exe, please try manual installation",
        'extracted_dir_structure': "Extracted directory structure:",
        'install_failed': "Installation failed: {}",
        'trying_pkg_manager': "Attempting to install FFmpeg using package manager...",
        'ffmpeg_installed_apt': "FFmpeg installed via apt",
        'ffmpeg_installed_yum_dnf': "FFmpeg installed via yum/dnf",
        'ffmpeg_installed_pacman': "FFmpeg installed via pacman",
        'linux_distro_unrecognized': "Could not automatically identify Linux distribution, please install FFmpeg manually",
        'linux_commands_ref': "Reference commands:",
        'manual_install_mac_other': "Could not automatically install FFmpeg, please install manually:",
        'mac_brew_cmd': "macOS: brew install ffmpeg",
        'other_systems_ref': "Other systems: Please refer to https://ffmpeg.org/download.html",
        'ffmpeg_install_failed_continue': "FFmpeg installation failed, cannot continue",
        'ffmpeg_still_unavailable': "FFmpeg is still unavailable, please install manually",
        'ffmpeg_ready': "FFmpeg is ready",
        'enter_url_prompt': "Please enter the Cloudflare Stream URL (containing thumbnails/thumbnail.jpg or manifest/video.m3u8): ",
        'enter_output_filename_prompt': "Please enter the output filename (no extension needed, .mp4 will be added automatically): ",
        'default_output_filename': "downloaded_video",
        'converted_url': "Converted video stream URL:",
        'executing_download_command': "Executing download command:",
        'download_complete': "Download complete! File saved as:",
        'download_failed': "Download failed! FFmpeg returned error code:",
        'possible_solutions': "Possible solutions:",
        'check_url_correct': "1. Check if the URL is correct and accessible",
        'try_diff_network': "2. Try a different network connection",
        'ensure_disk_space': "3. Ensure sufficient disk space",
        'ffmpeg_execution_error': "Error executing FFmpeg: {}",
        'url_value_error': "URL must contain 'thumbnails/thumbnail.jpg' or 'manifest/video.m3u8'",
        'ensure_url_format': "Please ensure the input URL contains 'thumbnails/thumbnail.jpg' or 'manifest/video.m3u8'",
        'unexpected_error': "An unexpected error occurred: {}",
        'choose_language': "Please choose your language (type 'zh' for Chinese, 'en' for English): ",
        'invalid_language_choice': "Invalid choice, defaulting to Chinese.",
    }
}

# Default language
current_language = 'en'

def get_text(key, *args):
    """Retrieves text in the current language, with optional formatting."""
    return MESSAGES[current_language].get(key, f"Missing text for key: {key}").format(*args)

def check_ffmpeg_installed():
    """Checks if FFmpeg is installed on the system (including in the current directory's ffmpeg folder)."""
    try:
        # Check globally installed ffmpeg
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if "ffmpeg version" in result.stdout or "ffmpeg version" in result.stderr:
            return True
        
        # Check for ffmpeg installation in the current directory on Windows
        if platform.system() == "Windows":
            # Check possible installation paths
            possible_paths = [
                Path("ffmpeg") / "bin" / "ffmpeg.exe",
                Path("ffmpeg") / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe",
                Path("ffmpeg") / "ffmpeg.exe"
            ]
            
            for ffmpeg_path in possible_paths:
                if ffmpeg_path.exists():
                    # Add current directory to PATH environment variable
                    os.environ["PATH"] += os.pathsep + str(ffmpeg_path.parent)
                    return True
        
        return False
    except (FileNotFoundError, OSError):
        return False

def install_ffmpeg():
    """Automatically installs FFmpeg based on the operating system."""
    system = platform.system()
    
    print(get_text('ffmpeg_not_installed'))
    
    if system == "Windows":
        # Check if already installed in known local paths
        possible_paths = [
            Path("ffmpeg") / "bin" / "ffmpeg.exe",
            Path("ffmpeg") / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe",
            Path("ffmpeg") / "ffmpeg.exe"
        ]
        
        for ffmpeg_path in possible_paths:
            if ffmpeg_path.exists():
                print(get_text('ffmpeg_existing_install', ffmpeg_path))
                os.environ["PATH"] += os.pathsep + str(ffmpeg_path.parent)
                return True
        
        # Windows installation process
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        install_dir = Path("ffmpeg")
        
        print(get_text('downloading_ffmpeg', ffmpeg_url))
        
        try:
            # Create installation directory
            install_dir.mkdir(exist_ok=True)
            
            # Download ZIP file
            response = requests.get(ffmpeg_url, stream=True)
            zip_path = install_dir / "ffmpeg.zip"
            
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract ZIP file
            print(get_text('extracting_ffmpeg'))
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(install_dir)
            
            # Clean up ZIP file
            zip_path.unlink()
            
            # Check extracted directory structure
            extracted_dir = None
            for item in install_dir.iterdir():
                if item.is_dir() and "ffmpeg" in item.name.lower():
                    extracted_dir = item
                    break
            
            # If a specific subdirectory is found
            if extracted_dir and (extracted_dir / "bin" / "ffmpeg.exe").exists():
                # Add bin directory to PATH
                bin_path = extracted_dir / "bin"
                os.environ["PATH"] += os.pathsep + str(bin_path)
                print(get_text('ffmpeg_installed_at', bin_path / 'ffmpeg.exe'))
                return True
            else:
                # Try to search for ffmpeg.exe in the extracted directory
                for root, dirs, files in os.walk(install_dir):
                    if "ffmpeg.exe" in files:
                        ffmpeg_path = Path(root) / "ffmpeg.exe"
                        # Add current directory to PATH environment variable
                        os.environ["PATH"] += os.pathsep + str(ffmpeg_path.parent)
                        print(get_text('ffmpeg_installed_at', ffmpeg_path))
                        return True
            
            print(get_text('ffmpeg_exe_not_found'))
            print(get_text('extracted_dir_structure'))
            for item in install_dir.iterdir():
                print(f" - {item.name}{' (dir)' if item.is_dir() else ''}")
            return False
            
        except Exception as e:
            print(get_text('install_failed', e))
            import traceback
            traceback.print_exc()
            return False
    
    elif system == "Linux":
        # Linux installation process
        print(get_text('trying_pkg_manager'))
        
        try:
            # Detect Linux distribution
            if Path("/etc/debian_version").exists():
                # Debian/Ubuntu
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
                print(get_text('ffmpeg_installed_apt'))
                return True
                
            elif Path("/etc/redhat-release").exists():
                # CentOS/RHEL/Fedora
                if "centos" in platform.platform().lower():
                    subprocess.run(["sudo", "yum", "install", "-y", "ffmpeg"], check=True)
                else:  # Fedora
                    subprocess.run(["sudo", "dnf", "install", "-y", "ffmpeg"], check=True)
                print(get_text('ffmpeg_installed_yum_dnf'))
                return True
                
            elif Path("/etc/arch-release").exists():
                # Arch Linux
                subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", "ffmpeg"], check=True)
                print(get_text('ffmpeg_installed_pacman'))
                return True
                
            else:
                print(get_text('linux_distro_unrecognized'))
                print(get_text('linux_commands_ref'))
                print("   Debian/Ubuntu: sudo apt install ffmpeg")
                print("   RHEL/CentOS: sudo yum install ffmpeg")
                print("   Fedora: sudo dnf install ffmpeg")
                print("   Arch: sudo pacman -S ffmpeg")
                return False
                
        except subprocess.CalledProcessError as e:
            print(get_text('install_failed', e))
            return False
    
    else:
        # macOS and other systems
        print(get_text('manual_install_mac_other'))
        print(get_text('mac_brew_cmd'))
        print(get_text('other_systems_ref'))
        return False

def convert_to_m3u8_url(url):
    """Converts a Cloudflare Stream URL to a downloadable m3u8 format."""
    # If it's already an m3u8 address, return it directly after cleaning
    if "manifest/video.m3u8" in url:
        new_url = url
    elif "thumbnails/thumbnail.jpg" in url:
        # Replace the path part
        new_url = url.replace("thumbnails/thumbnail.jpg", "manifest/video.m3u8")
    else:
        raise ValueError(get_text('url_value_error'))

    # Ensure URL encoding is correct
    parsed = urllib.parse.urlparse(new_url)
    # Preserve original query parameters (if any)
    clean_url = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        None  # Ignore fragment identifier
    ))
    
    return clean_url

def run_ffmpeg_download(m3u8_url, output_file):
    """Runs the FFmpeg download command."""
    # Ensure the output filename has a .mp4 extension
    if not output_file.lower().endswith(".mp4"):
        output_file += ".mp4"
    
    # Construct FFmpeg command
    command = [
        "ffmpeg",
        "-i", m3u8_url,
        "-c", "copy",
        output_file
    ]
    
    print("\n" + "-" * 50)
    print(get_text('executing_download_command'))
    print(" ".join(command))
    print("-" * 50 + "\n")
    
    try:
        # Run FFmpeg command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1  # Line buffering
        )
        
        # Output progress in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Display progress information (filter out unnecessary info)
                if "time=" in output and "speed=" in output:
                    print(output.strip())
        
        # Check return code
        if process.returncode == 0:
            print(f"\n{get_text('download_complete')} {output_file}")
            return True
        else:
            print(f"\n{get_text('download_failed')} {process.returncode}")
            print(get_text('possible_solutions'))
            print(get_text('check_url_correct'))
            print(get_text('try_diff_network'))
            print(get_text('ensure_disk_space'))
            return False
            
    except Exception as e:
        print(get_text('ffmpeg_execution_error', e))
        return False

def main():
    global current_language # Declare global to modify
    
    # Language selection at the start
    # FIX: Removed the 'language=current_language' keyword argument as get_text does not expect it.
    lang_choice = input(get_text('choose_language')).strip().lower()
    if lang_choice in MESSAGES:
        current_language = lang_choice
    else:
        print(get_text('invalid_language_choice', language='zh')) # Use 'zh' to get the default message
        current_language = 'zh' # Default to Chinese if invalid input
        
    print(get_text('tool_title'))
    print(get_text('separator'))
    
    # Check and install FFmpeg
    if not check_ffmpeg_installed():
        if not install_ffmpeg():
            print(get_text('ffmpeg_install_failed_continue'))
            return
        # Check again if installation was successful
        if not check_ffmpeg_installed():
            print(get_text('ffmpeg_still_unavailable'))
            return
    
    print(f"\n{get_text('ffmpeg_ready')}")
    
    # Get user input
    original_url = input(get_text('enter_url_prompt')).strip()
    output_file = input(get_text('enter_output_filename_prompt')).strip()
    
    if not output_file:
        output_file = get_text('default_output_filename')
    
    try:
        # Convert URL
        m3u8_url = convert_to_m3u8_url(original_url)
        print(f"\n{get_text('converted_url')}")
        print(m3u8_url)
        
        # Execute download
        run_ffmpeg_download(m3u8_url, output_file)
        
    except ValueError as e:
        # Use a more specific key for ValueErrors related to URL format
        print(f"\n{get_text('install_failed', e)}") # Reusing 'install_failed' for general error output, could add a new key if needed
        print(get_text('ensure_url_format'))
    except Exception as e:
        print(get_text('unexpected_error', e))

if __name__ == "__main__":
    main()
