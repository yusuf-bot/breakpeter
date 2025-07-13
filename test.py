from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import textwrap
import os

def generate_captioned_video(text, filename="captioned_video.mp4",
                              width=720, height=1280, duration_per_line=2,
                              font_path=None):
    # Uppercase the text and wrap it
    lines = textwrap.wrap(text.upper(), width=30)
    
    clips = []
    for i, line in enumerate(lines):
        # Create TikTok-style text with stroke
        caption = TextClip(
            line,
            fontsize=70,
            color='white',
            stroke_color='black',
            stroke_width=4,
            font=font_path if font_path else "Impact",  # use font path or fallback
            method='caption',
            size=(width - 100, None),  # fit within width
        ).set_position(("center", "bottom")) \
         .set_duration(duration_per_line) \
         .set_start(i * duration_per_line)

        clips.append(caption)

    total_duration = duration_per_line * len(lines)

    # Background: black portrait video
    background = ColorClip(size=(width, height), color=(0, 0, 0), duration=total_duration)

    final = CompositeVideoClip([background] + clips)
    final.write_videofile(filename, fps=30, codec='libx264', audio=False)

if __name__ == "__main__":
    # Optional: use a custom TTF font path
    font_path = "test.tff"  # Put the .ttf file in the same folder or give full path

    text = "THIS IS A TIKTOK STYLE CAPTION. BLOCKY, BOLD, WHITE TEXT WITH A STROKE."
    generate_captioned_video(text, font_path=font_path)
