Cloudflare Stream 视频下载工具
一个简单易用的 Python 脚本，用于从 Cloudflare Stream 下载视频。该工具能够自动检查并尝试安装 FFmpeg (Windows 和 Linux)，然后将 Cloudflare Stream 的视频链接转换为可下载的 .mp4 文件。

✨ 功能
自动 FFmpeg 管理: 自动检测系统是否安装了 FFmpeg，并在 Windows 和主流 Linux 发行版上尝试自动下载和安装。

Cloudflare Stream URL 转换: 将 thumbnails/thumbnail.jpg 格式的 Cloudflare Stream URL 转换为可供 FFmpeg 下载的 manifest/video.m3u8 格式。

视频下载: 使用 FFmpeg 进行视频下载，并将视频保存为 .mp4 格式。

下载进度显示: 在下载过程中实时显示 FFmpeg 的进度输出。

🚀 如何使用
先决条件
Python 3.x

FFmpeg (工具会尝试自动为您安装，如果失败，您可能需要手动安装)

安装依赖
您只需要安装 requests 库来处理 HTTP 请求：
``` python
pip install requests
```

运行脚本

``` bash
git clone https://github.com/LovelyO0sam/cloudflare-stream-downloader.git
cd cloudflare-stream-downloader
python cloudflare-stream-downloader.py
```

根据提示输入 Cloudflare Stream 视频的 URL。请确保 URL 包含 thumbnails/thumbnail.jpg 或 manifest/video.m3u8 字样。

示例 URL 格式:

https://customer-XXXXX.cloudflarestream.com/YYYYYYYYYYYYYYYYYYYYYYYY/thumbnails/thumbnail.jpg

https://customer-XXXXX.cloudflarestream.com/YYYYYYYYYYYYYYYYYYYYYYYY/manifest/video.m3u8

输入您希望保存的视频文件名（无需扩展名，脚本会自动添加 .mp4）。

脚本将自动转换 URL 并开始下载。

💻 支持的操作系统
Windows: 支持自动下载和安装 FFmpeg。

Linux (Debian/Ubuntu, CentOS/RHEL/Fedora, Arch): 支持通过包管理器自动安装 FFmpeg。

macOS 及其他系统: 需要手动安装 FFmpeg (例如，macOS 用户可以使用 Homebrew: brew install ffmpeg)。

欢迎任何形式的贡献！如果您有改进建议、发现了 Bug 或想添加新功能，请随时提交 Issue 或 Pull Request。

本项目采用 MIT 许可证。有关详细信息，请参阅 LICENSE 文件。
