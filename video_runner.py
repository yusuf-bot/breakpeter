#!/usr/bin/env python3
"""
Simple Video Runner - Streamlined version for easy execution
"""

import os
from moviepy.editor import *
from video_utils import VideoUtils
from text_to_speech import tts
from script_gen import get_latest_headlines_and_summaries, generate_script_with_mistral
from PIL import Image
if hasattr(Image, 'ANTIALIAS'):
       Image.RESAMPLE= Image.LANCZOS


def create_news_video():
    """Simplified video creation process"""
    
    # Configuration
    CONFIG = {
        'peter_image': 'peter.png',
        'stewie_image': 'stewie.png',
        'background_video': 'bg.mp4',
        'output_video': 'family_guy_news.mp4',
        'temp_audio_dir': 'temp_audio'
    }
    
    # Create temp directory
    os.makedirs(CONFIG['temp_audio_dir'], exist_ok=True)
    
    print("🚀 Starting Family Guy News Video Creation...")
    
    # Step 1: Get news and generate script
    print("📰 Fetching latest news...")
    articles = get_latest_headlines_and_summaries()
    
    if not articles:
        print("❌ No articles found!")
        return
    
    print("✍️ Generating Family Guy script...")
    script = generate_script_with_mistral(articles[0][0], articles[0][1])
    print(f"📝 Generated script:\n{script}\n")
    
    # Step 2: Parse script into dialogues
    dialogues = VideoUtils.parse_family_guy_script(script)
    print(f"🎭 Parsed {len(dialogues)} dialogue lines")
    
    # Step 3: Generate audio for each dialogue
    print("🎵 Generating speech audio...")
    audio_files = []
    
    for i, dialogue in enumerate(dialogues):
        character = dialogue['character']
        text = dialogue['clean_text']
        character+=' griffin'
        # Generate audio
        output_path = os.path.join(CONFIG['temp_audio_dir'], f"{character}_{i}.mp3")
        
        print(f"  🎤 Generating {character} audio: {text[:40]}...")
        
        try:
            tts(character, text, output_path)
            audio_files.append(output_path)
        except Exception as e:
            print(f"    ❌ Error: {e}")
            audio_files.append(None)
    
    # Step 4: Create video segments
    print("🎬 Creating video segments...")
    
    # Load background video
    bg_clip = VideoFileClip(CONFIG['background_video'])
    video_size = bg_clip.size
    
    segments = []
    current_time = 0
    
    for i, (dialogue, audio_path) in enumerate(zip(dialogues, audio_files)):
        if not audio_path or not os.path.exists(audio_path):
            print(f"  ⚠️ Skipping dialogue {i}: No audio file")
            continue
        
        print(f"  🎬 Creating segment {i+1}/{len(dialogues)} ({dialogue['character']})")
        
        # Load audio to get duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # Create background segment
        bg_segment = VideoUtils.create_background_segment(
            CONFIG['background_video'], 
            current_time % bg_clip.duration, 
            duration
        )
        
        if not bg_segment:
            print(f"    ❌ Failed to create background segment")
            continue
        
        # Create character animation
        image_path = CONFIG['peter_image'] if dialogue['character'] == 'peter' else CONFIG['stewie_image']
        char_animation = VideoUtils.create_slide_animation(
            image_path, 
            dialogue['character'], 
            duration, 
            video_size
        )
        
        # Create caption
        caption = VideoUtils.create_styled_caption(
            dialogue['text'], 
            duration, 
            video_size
        )
        
        # Combine all elements
        if char_animation and caption:
            segment = CompositeVideoClip([
                bg_segment,
                char_animation,
                caption
            ])
            
            # Add audio
            segment = segment.set_audio(audio_clip)
            
            # Add fade transitions
            segment = VideoUtils.add_fade_transitions(segment, fade_duration=0.2)
            
            segments.append(segment)
            current_time += duration
        else:
            print(f"    ⚠️ Missing elements for segment {i}")
    
    # Step 5: Combine all segments
    if not segments:
        print("❌ No valid segments created!")
        return
    
    print(f"🎬 Combining {len(segments)} segments into final video...")
    
    try:
        # Concatenate all segments
        final_video = concatenate_videoclips(segments)
        
        # Export final video
        print(f"💾 Exporting video: {CONFIG['output_video']}")
        final_video.write_videofile(
            CONFIG['output_video'],
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None  # Suppress moviepy logs
        )
        
        print(f"✅ Video created successfully: {CONFIG['output_video']}")
        print(f"📊 Final video duration: {final_video.duration:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error creating final video: {e}")
    
    finally:
        # Cleanup
        print("🧹 Cleaning up temporary files...")
        import shutil
        try:
            shutil.rmtree(CONFIG['temp_audio_dir'])
        except:
            pass



if __name__ == "__main__":
    print("🎬 Family Guy News Video Generator")
    print("=" * 40)
    
    # Check requirements
  
    # Run the video creation
    create_news_video()
