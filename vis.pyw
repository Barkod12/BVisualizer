import tkinter as tk
import soundcard as sc
import numpy as np
import threading
import time

#mmmmmm                        mm                        mm    mmm      mmmmm   
 ##""""##                      ##                        ##   #"##     #""""##m 
 ##    ##   m#####m   ##m####  ## m##"    m####m    m###m##     ##           ## 
 #######    " mmm##   ##"      ##m##     ##"  "##  ##"  "##     ##         m#"  
 ##    ##  m##"""##   ##       ##"##m    ##    ##  ##    ##     ##       m#"    
 ##mmmm##  ##mmm###   ##       ##  "#m   "##mm##"  "##mm###  mmm##mmm  m##mmmmm 
#"""""""    """" ""   ""       ""   """    """"      """ ""  """"""""  """""""" 
                                                                                
class AudioVisualizer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("BVis")
        self.window.geometry("400x200")
        
        # Create canvas for visualization
        self.canvas = tk.Canvas(self.window, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add sensitivity control
        self.sensitivity = 0.02  # Initial sensitivity value
        self.window.bind('<MouseWheel>', self.on_scroll)  # Windows
        self.window.bind('<Button-4>', self.on_scroll)    # Linux up
        self.window.bind('<Button-5>', self.on_scroll)    # Linux down
        
        # Create bars
        self.bars = []
        self.num_bars = 20
        self.audio_data = np.zeros(self.num_bars)
        
        # Create initial bars
        self.create_bars()
        
        # Bind resize event
        self.window.bind('<Configure>', self.on_resize)
        
        # Bind F11 for fullscreen toggle
        self.fullscreen = False
        self.window.bind('<F11>', self.toggle_fullscreen)
        self.window.bind('<Escape>', self.end_fullscreen)
        
        # Audio capture settings
        self.running = True
        
        # Start audio capture in a separate thread
        self.audio_thread = threading.Thread(target=self.capture_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
        
    def create_bars(self):
        # Clear existing bars
        for bar in self.bars:
            self.canvas.delete(bar)
        self.bars = []
        
        # Get window dimensions
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Calculate bar dimensions
        self.bar_width = (width - 100) // (self.num_bars * 2)  # Automatic bar width
        self.bar_spacing = self.bar_width
        
        # Create new bars
        for i in range(self.num_bars):
            x = i * (self.bar_width + self.bar_spacing) + 50
            bar = self.canvas.create_rectangle(x, height, x + self.bar_width, height, fill='cyan')
            self.bars.append(bar)
            
    def on_resize(self, event):
        # Recreate bars when window is resized
        self.create_bars()
    
    def capture_audio(self):
        # Get the loopback device (records system audio)
        speakers = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
        with speakers.recorder(samplerate=44100) as mic:
            while self.running:
                data = mic.record(1024)
                # Convert stereo to mono and get frequency magnitudes
                mono = np.mean(data, axis=1)
                magnitudes = np.abs(np.fft.fft(mono))[:self.num_bars]
                # Normalize and scale the magnitudes
                self.audio_data = np.clip(magnitudes * 0.7, 0, 150)
    
    def update(self):
        if self.running:
            # Get current window height
            height = self.window.winfo_height()
            
            # Update bars with real audio data
            for i, bar in enumerate(self.bars):
                # Scale height based on window size and sensitivity
                bar_height = int(self.audio_data[i] * height * self.sensitivity)
                x1, y1, x2, y2 = self.canvas.coords(bar)
                self.canvas.coords(bar, x1, height, x2, height - bar_height)
            
            self.window.after(50, self.update)
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.window.attributes('-fullscreen', self.fullscreen)
    
    def end_fullscreen(self, event=None):
        self.fullscreen = False
        self.window.attributes('-fullscreen', False)

    def on_scroll(self, event):
        # Windows mouse wheel
        if event.num == 5 or event.delta < 0:
            self.sensitivity = max(0.001, self.sensitivity - 0.001)  # Decrease sensitivity
        else:  # event.num == 4 or event.delta > 0
            self.sensitivity = min(0.1, self.sensitivity + 0.001)   # Increase sensitivity

    def on_closing(self):
        self.running = False
        time.sleep(0.1)  # Give audio thread time to close
        self.window.destroy()

if __name__ == "__main__":
    visualizer = AudioVisualizer()
