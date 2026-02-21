import os
import subprocess

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to your tools
VGMSTREAM_PATH = r"A:\RemakeEngine\Main\Tools\vgmstream-cli\vgmstream-cli.exe"
FFMPEG_PATH = r"A:\RemakeEngine\Main\Tools\ffmpeg\ffmpeg-n8.0-latest-win64-gpl-8.0\bin\ffmpeg.exe"

def test_vgmstream(filename="hub_mus.mus.raw"):
    filepath = os.path.join(MUS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    outpath = os.path.join(MUS_DIR, filename + ".wav")

    print(f"--- Running vgmstream on {filename} ---")

    # Command: vgmstream-cli.exe -o output.wav input.raw
    cmd = [
        VGMSTREAM_PATH,
        "-o", outpath,
        filepath
    ]

    try:
        # Run the command and capture the output
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Print what vgmstream says
        if result.stdout:
            print("[STDOUT]\n", result.stdout)
        if result.stderr:
            print("[STDERR]\n", result.stderr)

        if os.path.exists(outpath):
            print(f"SUCCESS! Decoded file saved to: {outpath}")

            # Optional: Show how you'd call FFmpeg right after
            # convert_to_mp3(outpath)
        else:
            print("FAILED. vgmstream did not produce a .wav file.")

    except Exception as e:
        print(f"Error executing vgmstream: {e}")

if __name__ == "__main__":
    test_vgmstream("hub_mus.mus.raw")