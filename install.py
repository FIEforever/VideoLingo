import os
import platform
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ascii_logo = """
__     ___     _            _     _                    
\ \   / (_) __| | ___  ___ | |   (_)_ __   __ _  ___  
 \ \ / /| |/ _` |/ _ \/ _ \| |   | | '_ \ / _` |/ _ \ 
  \ V / | | (_| |  __/ (_) | |___| | | | | (_| | (_) |
   \_/  |_|\__,_|\___|\___/|_____|_|_| |_|\__, |\___/ 
                                          |___/        
"""

def install_package(*packages):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])

def check_gpu():
    try:
        subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ffmpeg():
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    
    system = platform.system()
    
    if system == "Linux":
        console.print(Panel("📦 Installing FFmpeg...", style="cyan"))
        try:
            subprocess.check_call(["sudo", "apt", "install", "-y", "ffmpeg"])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call(["sudo", "yum", "install", "-y", "ffmpeg"], shell=True)
            except subprocess.CalledProcessError:
                console.print(Panel("❌ Failed to install FFmpeg via package manager", style="red"))
    else:
        console.print(Panel("📦 Installing FFmpeg...", style="cyan"))
        download_and_extract_ffmpeg()

def download_and_extract_ffmpeg():
    import requests
    import zipfile
    import shutil
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    
    system = platform.system()
    if system == "Windows":
        ffmpeg_exe = "ffmpeg.exe"
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    elif system == "Darwin":
        ffmpeg_exe = "ffmpeg"
        url = "https://evermeet.cx/ffmpeg/getrelease/zip"
    else:
        console.print(Panel("❌ Unsupported system for manual FFmpeg installation", style="red"))
        return

    if os.path.exists(ffmpeg_exe):
        console.print(f"✅ {ffmpeg_exe} already exists")
        return

    # Download and extract logic
    console.print(Panel("📦 Downloading FFmpeg...", style="cyan"))
    response = requests.get(url)
    if response.status_code == 200:
        filename = "ffmpeg.zip" if system in ["Windows", "Darwin"] else "ffmpeg.tar.xz"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        console.print(Panel("📦 Extracting FFmpeg...", style="cyan"))
        if system == "Linux":
            import tarfile
            with tarfile.open(filename) as tar_ref:
                for member in tar_ref.getmembers():
                    if member.name.endswith("ffmpeg"):
                        member.name = os.path.basename(member.name)
                        tar_ref.extract(member)
        else:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith(ffmpeg_exe):
                        zip_ref.extract(file)
                        shutil.move(os.path.join(*file.split('/')[:-1], os.path.basename(file)), os.path.basename(file))
        
        # Clean up temporary files
        os.remove(filename)
        if system == "Windows":
            for item in os.listdir():
                if os.path.isdir(item) and "ffmpeg" in item.lower():
                    shutil.rmtree(item)
        console.print(Panel("✅ FFmpeg installation completed", style="green"))
    else:
        console.print(Panel("❌ FFmpeg download failed", style="red"))

def main():
    install_package("requests", "rich", "ruamel.yaml")
    from rich.console import Console
    from rich.panel import Panel
    from rich.box import DOUBLE
    console = Console()
    
    width = max(len(line) for line in ascii_logo.splitlines()) + 4
    welcome_panel = Panel(
        ascii_logo,
        width=width,
        box=DOUBLE,
        title="[bold green]🌏[/bold green]",
        border_style="bright_blue"
    )
    console.print(welcome_panel)
    
    console.print(Panel.fit("🚀 Starting Installation", style="bold magenta"))

    # Configure mirrors
    from core.pypi_autochoose import main as choose_mirror
    choose_mirror()

    # Detect system and GPU
    has_gpu = platform.system() != 'Darwin' and check_gpu()
    if has_gpu:
        console.print(Panel("🎮 NVIDIA GPU detected, installing CUDA version of PyTorch...", style="cyan"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch==2.0.0", "torchaudio==2.0.0", "--index-url", "https://download.pytorch.org/whl/cu118"])
    else:
        system_name = "🍎 MacOS" if platform.system() == 'Darwin' else "💻 No NVIDIA GPU"
        console.print(Panel(f"{system_name} detected, installing CPU version of PyTorch... However, it would be extremely slow for transcription.", style="cyan"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch==2.1.2", "torchaudio==2.1.2"])

    def install_requirements():
        try:
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                "-r", 
                "requirements.txt"
            ], env={**os.environ, "PIP_NO_CACHE_DIR": "0", "PYTHONIOENCODING": "utf-8"})
        except subprocess.CalledProcessError as e:
            console.print(Panel(f"❌ Failed to install requirements: {str(e)}", style="red"))

    def install_noto_font():
        # Detect Linux distribution type
        if os.path.exists('/etc/debian_version'):
            # Debian/Ubuntu systems
            cmd = ['sudo', 'apt-get', 'install', '-y', 'fonts-noto']
            pkg_manager = "apt-get"
        elif os.path.exists('/etc/redhat-release'):
            # RHEL/CentOS/Fedora systems
            cmd = ['sudo', 'yum', 'install', '-y', 'google-noto*']
            pkg_manager = "yum"
        else:
            console.print("⚠️ Unrecognized Linux distribution, please install Noto fonts manually", style="yellow")
            return
            
        try:
            subprocess.run(cmd, check=True)
            console.print(f"✅ Successfully installed Noto fonts using {pkg_manager}", style="green")
        except subprocess.CalledProcessError:
            console.print("❌ Failed to install Noto fonts, please install manually", style="red")

    if platform.system() == 'Linux':
        install_noto_font()
    
    install_requirements()
    install_ffmpeg()
    
    console.print(Panel.fit("Installation completed", style="bold green"))
    console.print("To start the application, run:")
    console.print("[bold cyan]streamlit run st.py[/bold cyan]")
    console.print("[yellow]Note: First startup may take up to 1 minute[/yellow]")
    
    # Add troubleshooting tips
    console.print("\n[yellow]If the application fails to start:[/yellow]")
    console.print("1. [yellow]Check your network connection[/yellow]")
    console.print("2. [yellow]Re-run the installer: [bold]python install.py[/bold][/yellow]")

    # start the application
    subprocess.Popen(["streamlit", "run", "st.py"])

if __name__ == "__main__":
    main()
