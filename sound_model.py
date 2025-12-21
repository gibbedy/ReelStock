from typing import Protocol
import sys
print(sys.version)

class Sound_backend(Protocol):

    def play_file(self,file_path:str,wait_time:int):
        """ Play a wave file
            file_path -> file path of the wave file to play
            wait_time -> time to wait if there is a sound already playing. Used to allow customisable overlap of multiple sounds"""
        ...

class Debug_sound_backend(Sound_backend):
    def __init__(self):
        ...
    def play_file(self,file_path:str,wait_time):
        """debug prints instead of sound"""
        print(f'playing {file_path} using direct_backend')

class pygame_sound_backend(Sound_backend):
    """implements Sound_backend audio using pygame"""
    
    def __init__(self):
        import os
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
        import pygame

        self.pygame = pygame
        self.pygame.mixer.init()

    def play_file(self,file_path:str,wait_time:int=0):
        if self.pygame.mixer.get_busy():
            self.pygame.time.wait(wait_time)  # 5 ms sleep to avoid pegging CPU - Look at threading at a later date for this
        sound = self.pygame.mixer.Sound(file_path)

        
        sound.play()

class Sound_model:
    def __init__(self,backend:Sound_backend=pygame_sound_backend()):
        self.backend = backend
    def play_file(self,file_path:str,wait_time:int=0):
        self.backend.play_file(file_path,wait_time=0)
    def play_duplicate_bc(self,wait_time=0):
        self.backend.play_file("assets/sounds/duplicate.wav",wait_time)
    def play_unknown_bc(self,wait_time=0):
        self.backend.play_file("assets/sounds/unknown.wav",wait_time)
    def play_found_bc(self,wait_time=0):
        self.backend.play_file("assets/sounds/found.wav",wait_time)
    def play_incorrect_bc(self,wait_time=0):
        self.backend.play_file("assets/sounds/incorrect_format.wav",wait_time)
    def play_good(self,wait_time=0):
        self.backend.play_file("assets/sounds/good.wav",wait_time)
    def play_bad(self,wait_time=0):
        self.backend.play_file("assets/sounds/bah_bow.wav",wait_time)
    def play_and(self,wait_time=0):
        self.backend.play_file("assets/sounds/and.wav",wait_time)
