import os
import re
from moviepy.editor import *
from moviepy.video.fx.all import resize
import tempfile
from PIL import Image
import numpy as np

# Handle PIL version compatibility for ANTIALIAS
try:
    RESAMPLING_FILTER = Image.LANCZOS
except AttributeError:
    RESAMPLING_FILTER = Image.ANTIALIAS

class VideoUtils:
    """Utility class for video processing operations"""
    
    @staticmethod
    def parse_family_guy_script(script_text):
        """Parse Family Guy script format into structured dialogue data"""
        lines = script_text.strip().split('\n')
        dialogues = []
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                # Split on first colon to separate character from dialogue
                parts = line.split(':', 1)
                character_name = parts[0].strip().lower()
                dialogue_text = parts[1].strip()
                
                # Map character names
                if character_name in ['peter', 'peter griffin']:
                    character = 'peter'
                elif character_name in ['stewie', 'stewie griffin']:
                    character = 'stewie'
                else:
                    continue  # Skip unknown characters
                
                dialogues.append({
                    'character': character,
                    'text': dialogue_text,
                    'clean_text': VideoUtils.clean_text_for_speech(dialogue_text)
                })
        
        return dialogues
    
    @staticmethod
    def clean_text_for_speech(text):
        """Clean text for better text-to-speech conversion"""
        # Remove quotes and special characters
        text = re.sub(r'["\'`]', '', text)

        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '...', text)
        # Remove parenthetical expressions
        text = re.sub(r'\([^)]*\)', '', text)
        # Clean up spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def create_slide_animation(image_path, character, duration, video_size, slide_speed=0.5):
        """Create character slide-in animation"""
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return None
        
        try:
            # Load and resize character image
            char_img = ImageClip(image_path).set_duration(duration)
            
            # Calculate size (character should be about 1/4 of video height)
            target_height = video_size[1] // 4
            char_img = char_img.resize(height=target_height)
            
            # Position character at bottom of screen
            y_pos = video_size[1] - char_img.h - 30
            
            # Set slide positions based on character
            if character == 'peter':
                # Peter slides in from left
                start_x = -char_img.w
                end_x = 30
            else:  # stewie
                # Stewie slides in from right
                start_x = video_size[0]
                end_x = video_size[0] - char_img.w - 30
            
            # Create smooth slide animation
            def position_func(t):
                progress = min(t / slide_speed, 1)  # Complete slide in slide_speed seconds
                # Smooth easing function
                progress = progress * progress * (3 - 2 * progress)  # Smoothstep
                x = start_x + (end_x - start_x) * progress
                return (x, y_pos)
            
            char_img = char_img.set_position(position_func)
            
            return char_img
            
        except Exception as e:
            print(f"❌ Error creating animation for {character}: {e}")
            return None
    
    @staticmethod
    def create_text_image_with_stroke(text, fontsize=54, color='white', stroke_color='black', stroke_width=6, video_size=(1080, 1920)):
        """Create text image with stroke using PIL - Fixed for newer Pillow versions"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a larger canvas for the text
        canvas_width = video_size[0]
        canvas_height = 200  # Adjust based on text height needed
        
        # Create image with transparent background
        img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fall back to default if not available
        try:
            # Try different font paths for Windows
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/Arial.ttf",
                "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
                "arial.ttf",
                "Arial.ttf"
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, fontsize)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (canvas_width - text_width) // 2
        y = (canvas_height - text_height) // 2
        
        # Draw stroke (outline) - create thick border
        for adj_x in range(-stroke_width, stroke_width + 1):
            for adj_y in range(-stroke_width, stroke_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=stroke_color)
        
        # Draw main text on top
        draw.text((x, y), text, font=font, fill=color)
        
        # Convert to RGB array for MoviePy
        img_rgb = Image.new('RGB', img.size, (0, 0, 0))
        img_rgb.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
        
        return np.array(img_rgb)
    
    @staticmethod
    def create_styled_caption(text, total_duration, video_size, style='tiktok'):
        """Create TikTok-style caption using PIL instead of TextClip to avoid ImageMagick issues"""
        display_text = text.replace('"', '').replace("'", "")
        
        # Split into phrases (~7-10 words per line)
        words = display_text.split()
        chunks = []
        chunk = []
        for word in words:
            chunk.append(word)
            if len(chunk) >= 7:  # Adjust for pacing
                chunks.append(' '.join(chunk))
                chunk = []
        if chunk:
            chunks.append(' '.join(chunk))

        # Duration per chunk
        duration_per_chunk = total_duration / len(chunks)

        clips = []
        for i, phrase in enumerate(chunks):
            # Create text image using PIL
            if style == 'tiktok':
                text_img = VideoUtils.create_text_image_with_stroke(
                    phrase, 
                    fontsize=54, 
                    color='white', 
                    stroke_color='black', 
                    stroke_width=6,
                    video_size=video_size
                )
            else:
                text_img = VideoUtils.create_text_image_with_stroke(
                    phrase, 
                    fontsize=32, 
                    color='white', 
                    stroke_color='black', 
                    stroke_width=2,
                    video_size=video_size
                )
            
            # Create video clip from image
            def make_frame(t, img=text_img):
                return img
            
            txt_clip = VideoClip(make_frame, duration=duration_per_chunk)
            txt_clip = txt_clip.set_position(('center', 'center')).set_start(i * duration_per_chunk)
            clips.append(txt_clip)

        return CompositeVideoClip(clips, size=video_size)
    
    @staticmethod
    def create_background_segment(bg_video_path, start_time, duration):
        """Create background video segment with loop if needed"""
        if not os.path.exists(bg_video_path):
            print(f"❌ Background video not found: {bg_video_path}")
            return None
        
        try:
            bg_clip = VideoFileClip(bg_video_path)
            
            # If requested duration exceeds video length, loop the video
            if start_time + duration > bg_clip.duration:
                # Create looped version
                loops_needed = int((start_time + duration) / bg_clip.duration) + 1
                bg_clip = concatenate_videoclips([bg_clip] * loops_needed)
            
            # Extract the needed segment
            bg_segment = bg_clip.subclip(start_time, start_time + duration)
            
            return bg_segment
            
        except Exception as e:
            print(f"❌ Error creating background segment: {e}")
            return None
    
    @staticmethod
    def add_fade_transitions(video_clip, fade_duration=0.3):
        """Add fade in/out transitions to video clip"""
        try:
            # Add fade in
            video_clip = video_clip.fadein(fade_duration)
            # Add fade out
            video_clip = video_clip.fadeout(fade_duration)
            return video_clip
        except Exception as e:
            print(f"❌ Error adding fade transitions: {e}")
            return video_clip
    
    @staticmethod
    def create_title_screen(title, duration=3, video_size=(1920, 1080)):
        """Create an optional title screen using PIL instead of TextClip"""
        # Create colored background
        bg_color = ColorClip(size=video_size, color=(0, 0, 0), duration=duration)
        
        # Create title text using PIL
        title_img = VideoUtils.create_text_image_with_stroke(
            title,
            fontsize=48,
            color='white',
            stroke_color='blue',
            stroke_width=2,
            video_size=video_size
        )
        
        # Create video clip from image
        def make_frame(t):
            return title_img
        
        title_clip = VideoClip(make_frame, duration=duration)
        title_clip = title_clip.set_position('center')
        
        # Combine
        title_screen = CompositeVideoClip([bg_color, title_clip])
        
        return title_screen
    
    @staticmethod
    def get_video_info(video_path):
        """Get basic info about a video file"""
        if not os.path.exists(video_path):
            return None
        
        try:
            clip = VideoFileClip(video_path)
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'format': os.path.splitext(video_path)[1]
            }
            clip.close()
            return info
        except Exception as e:
            print(f"❌ Error getting video info: {e}")
            return None
    
    @staticmethod
    def create_debug_info_overlay(dialogue_info, video_size):
        """Create debug overlay showing current dialogue info using PIL"""
        debug_text = f"Character: {dialogue_info['character']}\nText: {dialogue_info['text'][:50]}..."
        
        # Create debug text using PIL
        debug_img = VideoUtils.create_text_image_with_stroke(
            debug_text,
            fontsize=16,
            color='red',
            stroke_color='black',
            stroke_width=1,
            video_size=video_size
        )
        
        # Create video clip from image
        def make_frame(t):
            return debug_img
        
        debug_clip = VideoClip(make_frame, duration=3)
        debug_clip = debug_clip.set_position((10, 10))
        
        return debug_clip
