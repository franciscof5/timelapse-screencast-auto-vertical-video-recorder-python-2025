import cv2
import numpy as np
import mss
import time
import pyaudio
import wave
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from threading import Thread
import moviepy.video.fx as vfx
import os

class VideoRecorderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timelapse_fps = 30  # FPS inicial
        self.recording_audio = False  # Flag para gravação de áudio
        self.frames_audio = []  # Armazenar os frames de áudio
        self.timelapse_segments = []  # Armazenar os segmentos de timelapse (ligado/desligado)
        self.frames = []  # Armazenar frames de vídeo
        self.audio_clip = None  # Áudio final
        self.video_clip = None  # Vídeo final
        self.recording = False  # Flag para gravar o vídeo
        self.record_button = None
        self.status_label = None
        self.progress_bar = None
        self.stream = None
        self.video_count = 1  # Contador para os arquivos de vídeo numerados

    def build(self):
        self.root = BoxLayout(orientation='vertical')

        # Botão para iniciar/parar a gravação
        self.record_button = Button(text="Iniciar Gravação", size_hint=(1, 0.1), background_color=(0, 1, 0, 1))
        self.record_button.bind(on_press=self.toggle_recording)
        self.root.add_widget(self.record_button)

        # Status da gravação
        self.status_label = Label(text="Aguardando ação...", size_hint=(1, 0.1))
        self.root.add_widget(self.status_label)

        # Barra de progresso
        self.progress_bar = ProgressBar(max=100, size_hint=(1, 0.1))
        self.root.add_widget(self.progress_bar)

        # Botão para ativar/desativar o timelapse
        self.timelapse_button = Button(text="Ativar Timelapse", size_hint=(1, 0.1))
        self.timelapse_button.bind(on_press=self.toggle_timelapse)
        self.root.add_widget(self.timelapse_button)

        return self.root

    def toggle_timelapse(self, instance):
        # Para a gravação atual e salva o vídeo com áudio
        if self.recording:
            # self.recording = False
            self.record_button.text = "Iniciar Gravação"
            self.record_button.background_color = (0, 1, 0, 1)  # Fundo verde
            self.status_label.text = "Gravação finalizada."

            # Salva o vídeo temporário com áudio
            self.save_video_with_audio()
            self.video_count += 1  # Incrementa o contador para o próximo arquivo de vídeo

            # Limpa o progresso e prepara a gravação para o próximo segmento
            self.frames = []
            self.frames_audio = []
            self.timelapse_segments = []
            self.start_audio_recording()
            self.record_thread = Thread(target=self.record_screen, daemon=True)
            self.record_thread.start()

    def toggle_recording(self, instance):
        if self.recording:
            # self.recording = False
            self.record_button.text = "Iniciar Gravação"
            self.record_button.background_color = (0, 1, 0, 1)  # Fundo verde
            self.status_label.text = "Gravação finalizada."
            self.stop_audio_recording()
            self.save_video_with_audio()  # Salva o vídeo e áudio depois que a gravação parar
        else:
            self.recording = True
            self.record_button.text = "Parar Gravação"
            self.record_button.background_color = (1, 0, 0, 1)  # Fundo vermelho
            self.status_label.text = "Gravando vídeo..."
            self.progress_bar.value = 0
            self.frames = []  # Limpa a lista de frames
            self.frames_audio = []  # Limpa a lista de frames de áudio
            self.timelapse_segments = []  # Limpa os segmentos de timelapse

            # Chama a função para iniciar a gravação de áudio
            self.start_audio_recording()

            self.record_thread = Thread(target=self.record_screen, daemon=True)
            self.record_thread.start()

    def start_audio_recording(self):
        # Inicializa e começa a gravação de áudio
        if not self.recording_audio:
            self.recording_audio = True
            self.audio_thread = Thread(target=self.record_audio, daemon=True)
            self.audio_thread.start()

    def save_audio(self):
        # Salva o áudio gravado em um arquivo
        if self.frames_audio:
            try:
                with wave.open("output_audio.wav", 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                    wf.setframerate(44100)
                    wf.writeframes(b''.join(self.frames_audio))
                print("Áudio salvo em 'output_audio.wav'")
            except Exception as e:
                print(f"Erro ao salvar áudio: {e}")
        else:
            print("Nenhum áudio foi gravado.")

    def stop_audio_recording(self):
        # Para a gravação de áudio
        if self.stream:
            print("Parando a gravação de áudio...")
            self.stream.stop_stream()
            self.stream.close()
            self.recording_audio = False
        else:
            print("Stream de áudio não iniciado corretamente.")

    def record_audio(self):
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            input=True,
                            frames_per_buffer=1024)

        print("Gravando áudio...")

        self.recording_audio = True
        start_time = time.time()
        while self.recording_audio:
            data = self.stream.read(1024)
            self.frames_audio.append(data)  # Armazena o áudio
        self.save_audio()
        

    def record_screen(self):
        output_file = f"output_video_{self.video_count}.mp4"
        capture_interval = 1 / self.timelapse_fps
        last_frame_time = time.perf_counter()

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

    def save_video_with_audio(self):
        # Junta o vídeo e o áudio em um único arquivo
        video_clip = VideoFileClip(f"output_video_{self.video_count}.mp4")
        # audio_clip = AudioFileClip(f"output_audio_{self.video_count}.wav")

        # Adiciona o áudio no vídeo
        # video_with_audio = video_clip.with_audio(audio_clip)

        # Salva o vídeo final com áudio ajustado
        video_clip.write_videofile(f"output_final_{self.video_count}.mp4", codec="libx264")

        # Limpa os arquivos temporários
        # os.remove(f"output_video_{self.video_count}.mp4")
        # os.remove(f"output_audio_{self.video_count}.wav")
        # print(f"Arquivos temporários 'output_video_{self.video_count}.mp4' removidos.")

    def concatenate_videos(self):
        # Concatenar todos os vídeos temporários gerados
        video_files = [f"output_final_{i}.mp4" for i in range(1, self.video_count+1)]
        clips = [VideoFileClip(file) for file in video_files]
        final_clip = concatenate_videoclips(clips)

        # Salva o vídeo final concatenado
        final_clip.write_videofile("output_final_concat.mp4", codec="libx264")

        # Limpa os arquivos temporários
        for file in video_files:
            os.remove(file)
        print("Todos os vídeos concatenados e arquivos temporários removidos.")

if __name__ == "__main__":
    VideoRecorderApp().run()
