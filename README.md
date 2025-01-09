# video-dubbing-tool

This Python script allows you to dub a video using an SRT subtitle file. It converts the text in the SRT file to speech using Google Text-to-Speech (gTTS) and merges the generated audio with the original video using FFmpeg. The default language is English, but it can be easily changed to any language supported by gTTS.


## Features
- Convert SRT subtitles to speech.
- Adjust audio duration to match video length.

- Merge audio with video using FFmpeg.
- Support for Arabic language.

    Convert SRT subtitles to speech: The script reads the subtitles from an SRT file and converts them into audio files using gTTS.

    Adjust audio duration: The script ensures the generated audio matches the duration of the original video by speeding up or slowing down the audio.

    Merge audio with video: The final audio is merged with the original video using FFmpeg.

    Support for multiple languages: You can dub videos in any language supported by gTTS (e.g., English, Arabic, Spanish, etc.).

    Recursive file search: The script can search for video and subtitle files in the current directory and all subdirectories.


   تحويل النص إلى كلام: يتم تحويل النصوص الموجودة في ملف SRT إلى كلام باستخدام gTTS.

    ضبط مدة الصوت: يتم ضبط مدة الصوت المُنشأ لتتناسب مع مدة الفيديو الأصلي.

    دمج الصوت مع الفيديو: يتم دمج الصوت المُنشأ مع الفيديو الأصلي باستخدام FFmpeg.

    دعم المجلدات الفرعية: يمكن للبرنامج البحث عن ملفات الفيديو وملفات الترجمة في المجلدات الفرعية.

   دعم اللغة العربية
  

## Requirements
- Python 3.x
- FFmpeg (must be installed on your system)

## Installation
1. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt

       Make sure FFmpeg is installed on your system.

Usage

    Place your video file and corresponding SRT file in the same directory.

    Run the script   python dubbing_tool.py

        The dubbed video will be saved as [video_name]_dub.mp4.

Changing the Language

To change the language of the dubbing, modify the language parameter in the create_dubbed_video function. For example:

    English: 'en'

    Arabic: 'ar'

    Spanish: 'es'

    French: 'fr'

    Example:

To dub a video in Spanish, change this line in the script:

create_dubbed_video(matching_srt, video_file, output_video_path, language='es')


gTTS supports a wide range of languages. You can find the full list of supported languages in the  Supported Languageshttps: https://gtts.readthedocs.io/en/latest/module.html#languages 

License

This project is licensed under the MIT License.


---

### **Notes**
- Ensure FFmpeg is installed correctly and added to your system's PATH.
- If the audio duration is too long or too short, the script will adjust it automatically.
- If you encounter issues, check the FFmpeg installation and ensure the video and subtitle files are correctly formatted.

---

This explanation provides everything you need to understand, use, and share the project. Let me know if you need further assistance! 🚀

