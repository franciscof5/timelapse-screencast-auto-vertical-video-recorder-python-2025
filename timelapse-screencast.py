import cv2
import numpy as np
import mss
import time
from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import Crop
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from threading import Thread

class VideoRecorderApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical')

        self.recording = False  # Flag para verificar o estado da gravação
        self.record_button = Button(text="Iniciar Gravação", size_hint=(1, 0.1), background_color=(0, 1, 0, 1))
        self.record_button.bind(on_press=self.toggle_recording)
        self.root.add_widget(self.record_button)

        self.status_label = Label(text="Aguardando ação...", size_hint=(1, 0.1))
        self.root.add_widget(self.status_label)

        self.progress_bar = ProgressBar(max=100, size_hint=(1, 0.1))
        self.root.add_widget(self.progress_bar)

        return self.root

    def toggle_recording(self, instance):
        if self.recording:
            self.recording = False
            self.record_button.text = "Iniciar Gravação"
            self.record_button.background_color = (0, 1, 0, 1)  # Fundo verde
            self.status_label.text = "Gravação finalizada."
        else:
            self.recording = True
            self.record_button.text = "Parar Gravação"
            self.record_button.background_color = (1, 0, 0, 1)  # Fundo vermelho
            self.status_label.text = "Gravando vídeo..."
            self.progress_bar.value = 0
            self.record_thread = Thread(target=self.record_screen, daemon=True)
            self.record_thread.start()

    def record_screen(self):
        output_file = "output.mp4"
        timelapse_fps = 30  # Ajustado para evitar aceleração excessiva
        capture_interval = 1 / timelapse_fps
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Captura o monitor principal
            width, height = monitor["width"], monitor["height"]
            
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            output_fps = 30  # FPS ajustado
            out = cv2.VideoWriter(output_file, fourcc, output_fps, (width, height))

            print("Gravação iniciada.")
            try:
                while self.recording:  # Continua gravando até que seja interrompido
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    out.write(frame)
                    self.progress_bar.value = min(100, self.progress_bar.value + 1)
                    time.sleep(capture_interval)
            except Exception as e:
                print(f"Erro na gravação: {e}")
            finally:
                out.release()
                print("Gravação finalizada.")

        self.status_label.text = "Gravação finalizada."
        self.record_button.text = "Iniciar Gravação"
        self.record_button.background_color = (0, 1, 0, 1)  # Fundo verde
        self.recording = False

if __name__ == "__main__":
    VideoRecorderApp().run()
