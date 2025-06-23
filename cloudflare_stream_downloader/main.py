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

def check_ffmpeg_installed():
    """检查系统是否安装了FFmpeg（包括当前目录下的ffmpeg目录）"""
    try:
        # 检查全局安装的ffmpeg
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if "ffmpeg version" in result.stdout or "ffmpeg version" in result.stderr:
            return True
        
        # 检查当前目录下的ffmpeg安装
        if platform.system() == "Windows":
            # 检查可能的安装路径
            possible_paths = [
                Path("ffmpeg") / "bin" / "ffmpeg.exe",
                Path("ffmpeg") / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe",
                Path("ffmpeg") / "ffmpeg.exe"
            ]
            
            for ffmpeg_path in possible_paths:
                if ffmpeg_path.exists():
                    # 添加当前目录到PATH环境变量
                    os.environ["PATH"] += os.pathsep + str(ffmpeg_path.parent)
                    return True
        
        return False
    except (FileNotFoundError, OSError):
        return False

def install_ffmpeg():
    """根据操作系统自动安装FFmpeg"""
    system = platform.system()
    
    print("FFmpeg未安装，正在尝试自动安装...")
    
    if system == "Windows":
        # 检查是否已经安装过
        possible_paths = [
            Path("ffmpeg") / "bin" / "ffmpeg.exe",
            Path("ffmpeg") / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe",
            Path("ffmpeg") / "ffmpeg.exe"
        ]
        
        for ffmpeg_path in possible_paths:
            if ffmpeg_path.exists():
                print(f"使用已存在的FFmpeg安装: {ffmpeg_path}")
                os.environ["PATH"] += os.pathsep + str(ffmpeg_path.parent)
                return True
        
        # Windows安装流程
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        install_dir = Path("ffmpeg")
        
        print(f"下载FFmpeg: {ffmpeg_url}")
        
        try:
            # 创建安装目录
            install_dir.mkdir(exist_ok=True)
            
            # 下载ZIP文件
            response = requests.get(ffmpeg_url, stream=True)
            zip_path = install_dir / "ffmpeg.zip"
            
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 解压ZIP文件
            print("解压FFmpeg...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(install_dir)
            
            # 清理ZIP文件
            zip_path.unlink()
            
            # 检查解压后的目录结构
            extracted_dir = None
            for item in install_dir.iterdir():
                if item.is_dir() and "ffmpeg" in item.name.lower():
                    extracted_dir = item
                    break
            
            # 如果找到特定的子目录
            if extracted_dir and (extracted_dir / "bin" / "ffmpeg.exe").exists():
                # 添加bin目录到PATH
                bin_path = extracted_dir / "bin"
                os.environ["PATH"] += os.pathsep + str(bin_path)
                print(f"FFmpeg已安装到: {bin_path / 'ffmpeg.exe'}")
                return True
            else:
                # 尝试在解压后的目录中搜索ffmpeg.exe
                for root, dirs, files in os.walk(install_dir):
                    if "ffmpeg.exe" in files:
                        ffmpeg_path = Path(root) / "ffmpeg.exe"
                        # 添加当前目录到PATH环境变量
                        os.environ["PATH"] += os.pathsep + str(ffmpeg_path.parent)
                        print(f"FFmpeg已安装到: {ffmpeg_path}")
                        return True
            
            print("无法找到ffmpeg.exe，请尝试手动安装")
            print("解压后的目录结构:")
            for item in install_dir.iterdir():
                print(f" - {item.name}{' (dir)' if item.is_dir() else ''}")
            return False
            
        except Exception as e:
            print(f"安装失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    elif system == "Linux":
        # Linux安装流程
        print("尝试使用包管理器安装FFmpeg...")
        
        try:
            # 检测Linux发行版
            if Path("/etc/debian_version").exists():
                # Debian/Ubuntu
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
                print("FFmpeg已通过apt安装")
                return True
                
            elif Path("/etc/redhat-release").exists():
                # CentOS/RHEL/Fedora
                if "centos" in platform.platform().lower():
                    subprocess.run(["sudo", "yum", "install", "-y", "ffmpeg"], check=True)
                else:  # Fedora
                    subprocess.run(["sudo", "dnf", "install", "-y", "ffmpeg"], check=True)
                print("FFmpeg已通过yum/dnf安装")
                return True
                
            elif Path("/etc/arch-release").exists():
                # Arch Linux
                subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", "ffmpeg"], check=True)
                print("FFmpeg已通过pacman安装")
                return True
                
            else:
                print("无法自动识别Linux发行版，请手动安装FFmpeg")
                print("参考命令:")
                print("   Debian/Ubuntu: sudo apt install ffmpeg")
                print("   RHEL/CentOS: sudo yum install ffmpeg")
                print("   Fedora: sudo dnf install ffmpeg")
                print("   Arch: sudo pacman -S ffmpeg")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"安装失败: {e}")
            return False
    
    else:
        # macOS和其他系统
        print("无法自动安装FFmpeg，请手动安装:")
        print("   macOS: brew install ffmpeg")
        print("   其他系统: 请参考 https://ffmpeg.org/download.html")
        return False

def convert_to_m3u8_url(url):
    """将Cloudflare Stream URL转换为可下载的m3u8格式"""
    # 如果已经是m3u8地址，直接清理后返回
    if "manifest/video.m3u8" in url:
        # 直接使用这个URL
        new_url = url
    elif "thumbnails/thumbnail.jpg" in url:
        # 替换路径部分
        new_url = url.replace("thumbnails/thumbnail.jpg", "manifest/video.m3u8")
    else:
        raise ValueError("URL必须包含 'thumbnails/thumbnail.jpg' 或 'manifest/video.m3u8'")

    # 确保URL编码正确
    parsed = urllib.parse.urlparse(new_url)
    # 保留原始查询参数（如果有）
    clean_url = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        None  # 忽略片段标识
    ))
    
    return clean_url

def run_ffmpeg_download(m3u8_url, output_file):
    """运行FFmpeg下载命令"""
    # 确保输出文件名有.mp4后缀
    if not output_file.lower().endswith(".mp4"):
        output_file += ".mp4"
    
    # 构建FFmpeg命令
    command = [
        "ffmpeg",
        "-i", m3u8_url,
        "-c", "copy",
        output_file
    ]
    
    print("\n" + "-" * 50) # 简化分隔符
    print("正在执行下载命令:")
    print(" ".join(command))
    print("-" * 50 + "\n") # 简化分隔符
    
    try:
        # 运行FFmpeg命令
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1  # 行缓冲
        )
        
        # 实时输出进度
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # 显示进度信息（过滤掉不必要的信息）
                if "time=" in output and "speed=" in output:
                    print(output.strip())
        
        # 检查返回码
        if process.returncode == 0:
            print("\n下载完成! 文件已保存为:", output_file)
            return True
        else:
            print("\n下载失败! FFmpeg返回错误码:", process.returncode)
            print("可能的解决方案:")
            print("1. 检查URL是否正确且可访问")
            print("2. 尝试使用不同的网络连接")
            print("3. 确保有足够的磁盘空间")
            return False
            
    except Exception as e:
        print(f"\n执行FFmpeg时出错: {e}")
        return False

def main():
    print("Cloudflare Stream视频下载工具")
    print("=" * 50)
    
    # 检查并安装FFmpeg
    if not check_ffmpeg_installed():
        if not install_ffmpeg():
            print("FFmpeg安装失败，无法继续")
            return
        # 再次检查是否安装成功
        if not check_ffmpeg_installed():
            print("FFmpeg仍然不可用，请手动安装")
            return
    
    print("\nFFmpeg已准备好")
    
    # 获取用户输入
    original_url = input("\n请输入Cloudflare Stream URL(包含thumbnails/thumbnail.jpg或manifest/video.m3u8): ").strip()
    output_file = input("请输入输出文件名(无需扩展名，将自动添加.mp4): ").strip()
    
    if not output_file:
        output_file = "downloaded_video"
    
    try:
        # 转换URL
        m3u8_url = convert_to_m3u8_url(original_url)
        print("\n转换后的视频流URL:")
        print(m3u8_url)
        
        # 执行下载
        run_ffmpeg_download(m3u8_url, output_file)
        
    except ValueError as e:
        print(f"\n错误: {e}")
        print("请确保输入的URL包含'thumbnails/thumbnail.jpg'或'manifest/video.m3u8'")
    except Exception as e:
        print(f"\n发生意外错误: {e}")

if __name__ == "__main__":
    main()
