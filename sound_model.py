from typing import Protocol
import sys
print(sys.version)

class Sound_backend(Protocol):
    def __init__(self):
        ...
    def play_file(self,file_path:str):
        """ Play a wave file
            file_path -> file path of the wave file to play"""
        ...

class Debug_sound_backend(Sound_backend):
    def __init__(self):
        ...
    def play_file(self,file_path:str):
        """debug prints instead of sound"""
        print(f'playing {file_path} using direct_backend')

class pygame_sound_backend(Sound_backend):
    """implements Sound_backend audio using pygame"""
    
    def __init__(self):
        import pygame
        self.pygame = pygame
        self.pygame.mixer.init()

    def play_file(self,file_path:str):
        while self.pygame.mixer.get_busy():
            self.pygame.time.wait(5)  # 5 ms sleep to avoid pegging CPU - Look at threading at a later date for this

        sound = self.pygame.mixer.Sound(file_path)

        
        sound.play()

class Sound_model:
    def __init__(self,backend:Sound_backend=pygame_sound_backend()):
        self.backend = backend
    def play_file(self,file_path:str):
        self.backend.play_file(file_path)
    def play_duplicate_bc(self):
        self.backend.play_file("assets/sounds/duplicate_bc.wav")
    def play_unknown_bc(self):
        self.backend.play_file("assets/sounds/unknown_bc.wav")
    def play_found_bc(self):
        self.backend.play_file("assets/sounds/bc_found.wav")
    def play_incorrect_bc(self):
        self.backend.play_file("assets/sounds/incorrect_bc_format.wav")
