Cloudflare Stream Video Downloader
A simple and easy-to-use Python script for downloading videos from Cloudflare Stream. This tool automatically checks for and attempts to install FFmpeg (on Windows and Linux), then converts Cloudflare Stream video links into downloadable .mp4 files.

✨ Features
Automatic FFmpeg Management: Automatically detects if FFmpeg is installed on the system and attempts to download and install it on Windows and major Linux distributions.

Cloudflare Stream URL Conversion: Converts Cloudflare Stream URLs in thumbnails/thumbnail.jpg format to manifest/video.m3u8 format, which is suitable for FFmpeg download.

Video Download: Uses FFmpeg to download videos and saves them in .mp4 format.

Download Progress Display: Shows real-time FFmpeg progress output during the download.

🚀 How to Use
Prerequisites
Python 3.x

FFmpeg (The tool will attempt to install it for you automatically; if it fails, you may need to install it manually)

Install Dependencies
You only need to install the requests library to handle HTTP requests:

``` python
pip install requests
```
Run the Script

``` bash 
git clone https://github.com/LovelyO0sam/cloudflare-stream-downloader.git
cd cloudflare-stream-downloader
python cloudflare-stream-downloader.py
```
Follow the prompts to enter the Cloudflare Stream video URL. Please ensure the URL contains thumbnails/thumbnail.jpg or manifest/video.m3u8.

Example URL Format:

https://customer-XXXXX.cloudflarestream.com/YYYYYYYYYYYYYYYYYYYYYYYY/thumbnails/thumbnail.jpg

https://customer-XXXXX.cloudflarestream.com/YYYYYYYYYYYYYYYYYYYYYYYY/manifest/video.m3u8

Enter the desired output filename for the video (no extension needed; the script will automatically add .mp4).

The script will automatically convert the URL and start the download.

💻 Supported Operating Systems
Windows: Supports automatic FFmpeg download and installation.

Linux (Debian/Ubuntu, CentOS/RHEL/Fedora, Arch): Supports automatic FFmpeg installation via package managers.

macOS and other systems: Requires manual FFmpeg installation (e.g., macOS users can use Homebrew: brew install ffmpeg).

🤝 Contributing
Contributions of any kind are welcome! If you have suggestions for improvement, found a bug, or want to add a new feature, feel free to submit an Issue or Pull Request.

📄 License
This project is licensed under the MIT License. For more details, please see the LICENSE file.