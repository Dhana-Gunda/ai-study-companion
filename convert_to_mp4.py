import os
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print("Using full static ffmpeg at:", ffmpeg_exe)

src_webm = r"C:\Users\gunda\OneDrive\Desktop\AI_Study_Companion_Demo.webm"
dest_mp4 = r"C:\Users\gunda\OneDrive\Desktop\AI_Study_Companion_Demo.mp4"
project_mp4 = r"c:\Users\gunda\OneDrive\Desktop\newProject\AI_Study_Companion_Demo.mp4"

# Convert to standard MP4 with H.264 video codec and yuv420p pixel format
# This guarantees 100% instant playback in Google Drive, QuickTime, Windows Media Player, and web
cmd = [
    ffmpeg_exe,
    "-y",
    "-i", src_webm,
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "22",
    "-pix_fmt", "yuv420p",
    dest_mp4
]

print("Running command:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(dest_mp4):
    print(f"SUCCESS! MP4 generated at: {dest_mp4} (Size: {os.path.getsize(dest_mp4)} bytes)")
    import shutil
    shutil.copyfile(dest_mp4, project_mp4)
    shutil.copyfile(dest_mp4, r"c:\Users\gunda\OneDrive\Desktop\newProject\frontend\public\demo_video.mp4")
else:
    print("FAILED! Stderr:", result.stderr)
