import cv2
import numpy as np
import mss
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from threading import Thread

class VideoRecorderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timelapse_fps = 30  # Inicializa a variável timelapse_fps

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

        # Botão para alternar entre os estados de timelapse
        self.timelapse_button = Button(text="Ativar Timelapse", size_hint=(1, 0.1))
        self.timelapse_button.bind(on_press=self.toggle_timelapse)
        self.root.add_widget(self.timelapse_button)

        return self.root

    def toggle_timelapse(self, instance):
        # Alterna entre ativado e desativado
        if self.timelapse_fps == 5:
            self.timelapse_fps = 30
            self.timelapse_button.text = "Ativar Timelapse"
        else:
            self.timelapse_fps = 5
            self.timelapse_button.text = "Desativar Timelapse"

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
        capture_interval = 1 / self.timelapse_fps
        last_frame_time = time.perf_counter()  # Armazenar o tempo inicial

        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Captura o monitor principal
            width, height = monitor["width"], monitor["height"]
            
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            output_fps = 30  # FPS ajustado
            out = cv2.VideoWriter(output_file, fourcc, output_fps, (width, height))

            print("Gravação iniciada.")
            try:
                while self.recording:  # Continua gravando até que seja interrompido
                    current_time = time.perf_counter()
                    elapsed_time = current_time - last_frame_time

                    # Verifica se o intervalo de captura foi atingido
                    if elapsed_time >= capture_interval:
                        screenshot = sct.grab(monitor)
                        frame = np.array(screenshot)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        out.write(frame)

                        # Atualiza a barra de progresso
                        self.progress_bar.value = min(100, self.progress_bar.value + 1)

                        # Atualiza o tempo do último frame capturado
                        last_frame_time = current_time

                        # Atualiza o intervalo com o novo FPS em tempo real
                        capture_interval = 1 / self.timelapse_fps

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
