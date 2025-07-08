import os
import re
from moviepy.editor import *
from moviepy.video.fx.all import resize
import tempfile

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
    def create_styled_caption(text, duration, video_size, style='modern'):
        """Create styled caption with different visual styles"""
        # Clean text for display
        display_text = text.replace('"', '').replace("'", "")
        
        # Wrap long text
        if len(display_text) > 60:
            words = display_text.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 60:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            display_text = '\n'.join(lines)
        
        if style == 'modern':
            # Modern style with shadow
            txt_clip = TextClip(display_text,
                               fontsize=32,
                               color='white',
                               font='Arial-Bold',
                               stroke_color='black',
                               stroke_width=3,
                               align='center')
        elif style == 'classic':
            # Classic subtitle style
            txt_clip = TextClip(display_text,
                               fontsize=28,
                               color='yellow',
                               font='Arial',
                               stroke_color='black',
                               stroke_width=2,
                               align='center')
        
        # Position at bottom center with some padding
        txt_clip = txt_clip.set_position(('center', video_size[1] - 120)).set_duration(duration)
        
        return txt_clip
    
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
        """Create an optional title screen"""
        # Create colored background
        bg_color = ColorClip(size=video_size, color=(0, 0, 0), duration=duration)
        
        # Create title text
        title_clip = TextClip(title,
                             fontsize=48,
                             color='white',
                             font='Arial-Bold',
                             stroke_color='blue',
                             stroke_width=2)
        
        title_clip = title_clip.set_position('center').set_duration(duration)
        
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
        """Create debug overlay showing current dialogue info (for development)"""
        debug_text = f"Character: {dialogue_info['character']}\nText: {dialogue_info['text'][:50]}..."
        
        debug_clip = TextClip(debug_text,
                             fontsize=16,
                             color='red',
                             font='Arial')
        
        debug_clip = debug_clip.set_position((10, 10)).set_duration(3)
        
        return debug_clip