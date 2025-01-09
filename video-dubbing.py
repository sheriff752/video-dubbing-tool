from pysrt import open as open_srt
import os
import subprocess
import shutil
from gtts import gTTS
import time  # إضافة مكتبة time للتأخير

def get_video_duration(video_path):
    """Get the duration of the video using ffprobe."""
    command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return float(result.stdout.strip())

def create_silent_audio(duration, output_file):
    """Create a silent audio file for a specified duration."""
    command = f'ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t {duration} -q:a 9 -acodec libmp3lame "{output_file}"'
    subprocess.run(command, shell=True, check=True)

def adjust_audio_duration(audio_path, target_duration):
    """Adjust the audio duration to match the target duration."""
    try:
        # Calculate the required speed
        current_duration = get_video_duration(audio_path)
        speed_factor = current_duration / target_duration

        # If the speed factor is too low or too high, split the process into steps
        if speed_factor < 0.5 or speed_factor > 2.0:
            print("⚠️ The time difference is too large. Please check the SRT file.")
            return False

        # Adjust the speed
        adjusted_audio = os.path.join(os.path.dirname(audio_path), "adjusted_audio.mp3")
        command = f'ffmpeg -i "{audio_path}" -af "atempo={speed_factor}" "{adjusted_audio}"'
        subprocess.run(command, shell=True, check=True)

        # Replace the original file with the adjusted file
        os.replace(adjusted_audio, audio_path)
        print(f"✅ Audio duration adjusted to match the target duration: {target_duration} seconds")
        return True
    except Exception as e:
        print(f"❌ Error adjusting audio duration: {e}")
        return False

def create_dubbed_video(srt_file, video_path, output_video_path, language='en'):
    # Open the SRT file
    try:
        subtitles = open_srt(srt_file)
        print(f"Number of texts in the SRT file {srt_file}: {len(subtitles)}")
    except FileNotFoundError:
        print(f"❌ Error: File {srt_file} not found. Please check the path.")
        return

    # Create a temporary folder to save audio files
    audio_dir = "temp_audio_clips"
    os.makedirs(audio_dir, exist_ok=True)

    # Convert each text to speech
    audio_files = []
    for i, sub in enumerate(subtitles):
        try:
            # Use gTTS for the specified language
            tts = gTTS(sub.text, lang=language)  # Language can be changed here
            audio_file = os.path.join(audio_dir, f"audio_{i}.mp3")
            tts.save(audio_file)
            audio_files.append(audio_file)
            print(f"✅ Created {audio_file}")

            # Add a delay of 1 second between requests
            time.sleep(1)  # Delay for 1 second
        except Exception as e:
            print(f"❌ Error converting text to speech: {e}")
            return

    # Merge audio clips into one file
    merged_audio = os.path.join(audio_dir, "output.mp3")
    try:
        audio_concat = "|".join(audio_files)
        command_concat = f'ffmpeg -i "concat:{audio_concat}" -acodec copy "{merged_audio}"'
        subprocess.run(command_concat, shell=True, check=True)
        print(f"✅ Merged audio clips into {merged_audio}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error merging audio clips: {e}")
        return

    # Calculate video and dubbing duration
    video_duration = get_video_duration(video_path)
    audio_duration = get_video_duration(merged_audio)

    # If the dubbing is longer or shorter than the video, adjust it
    if abs(audio_duration - video_duration) > 1.0:  # If the difference is more than 1 second
        print(f"⏳ Time difference between video and dubbing: {abs(audio_duration - video_duration)} seconds")
        if not adjust_audio_duration(merged_audio, video_duration):
            return

    # If the dubbing is shorter than the video, add silence
    if audio_duration < video_duration:
        silence_duration = video_duration - audio_duration
        silent_audio = os.path.join(audio_dir, "silence.mp3")
        create_silent_audio(silence_duration, silent_audio)
        
        final_audio = os.path.join(audio_dir, "final_output.mp3")
        command_concat_final = f'ffmpeg -i "{merged_audio}" -i "{silent_audio}" -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1" "{final_audio}"'
        subprocess.run(command_concat_final, shell=True, check=True)
        merged_audio = final_audio

    # Merge audio with video using FFmpeg
    if os.path.exists(video_path):
        print(f"🎥 Found video file: {video_path}")

        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", merged_audio],
                capture_output=True,
                text=True,
                check=True
            )
            audio_stream_index = result.stdout.strip().split('\n')[0] if result.stdout.strip() else "0"
            print(f"🎧 Selected audio stream: {audio_stream_index}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error selecting audio stream: {e}")
            return

        # Merge video and audio
        try:
            command = f'''
            ffmpeg -i "{video_path}" -i "{merged_audio}" -c:v copy -map 0:v:0 -map 1:a:{audio_stream_index} -shortest "{output_video_path}"
            '''
            subprocess.run(command, shell=True, check=True)
            print(f"✅ Created dubbed video: {output_video_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error merging audio with video: {e}")
    else:
        print(f"❌ Video file {video_path} not found.")

    # Delete the temporary audio folder
    try:
        shutil.rmtree(audio_dir)  # Delete the folder and its contents
        print(f"🗑️ Deleted temporary folder: {audio_dir}")
    except Exception as e:
        print(f"❌ Error deleting temporary folder: {e}")

def find_files_recursive(folder, extension):
    """
    Search for all files with a specific extension in a folder and its subfolders.
    
    :param folder: Path to the folder containing the files.
    :param extension: The extension to search for (e.g., ".srt" or ".mp4").
    :return: List of paths to all matching files.
    """
    matching_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(extension):
                matching_files.append(os.path.join(root, file))
    return matching_files

# Search for all video and subtitle files in the current folder and subfolders
video_files = find_files_recursive(".", ".mp4")
srt_files = find_files_recursive(".", ".srt")

# Match each video file with its corresponding subtitle file
for video_file in video_files:
    # Extract the file name without extension
    video_name = os.path.splitext(video_file)[0]

    # Find the matching subtitle file
    matching_srt = None
    for srt_file in srt_files:
        if os.path.splitext(srt_file)[0] == video_name:
            matching_srt = srt_file
            break

    if matching_srt:
        print(f"🎬 Processing video: {video_file} with subtitle: {matching_srt}")

        # Create the output dubbed video file name
        output_video_path = f"{video_name}_dub.mp4"

        # Create the dubbing
        create_dubbed_video(matching_srt, video_file, output_video_path, language='en')  # Change language here
        print(f"🎉 Finished processing video: {video_file}\n")
    else:
        print(f"⚠️ No matching subtitle file found for video: {video_file}")
