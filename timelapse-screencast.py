import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2
import numpy as np
import mss
import time
import pyaudio
import wave
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from threading import Thread
import os
from datetime import datetime

class VideoRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Recorder")
        self.root.geometry("300x200")

        self.timelapse_fps = 1 # FPS inicial
        self.recording_audio = False  # Flag para gravação de áudio
        self.frames_audio = []  # Armazenar os frames de áudio
        self.timelapse_segments = []  # Armazenar os segmentos de timelapse (ligado/desligado)
        self.frames = []  # Armazenar frames de vídeo
        self.audio_clip = None  # Áudio final
        self.video_clip = None  # Vídeo final
        self.recording = False  # Flag para gravar o vídeo

        # Botão para iniciar/parar a gravação
        self.record_button = tk.Button(self.root, text="Iniciar Gravação", command=self.toggle_recording)
        self.record_button.pack(pady=20)

        # Campo de entrada de texto abaixo do botão
        self.text_input_label = tk.Label(self.root, text="Texto adicional:")
        self.text_input_label.pack(pady=5)

        self.text_input = tk.Entry(self.root, width=40)
        self.text_input.pack(pady=5)

        # Status da gravação
        self.status_label = tk.Label(self.root, text="Aguardando ação...")
        self.status_label.pack(pady=10)

        # Barra de progresso
        self.progress_bar = tk.Scale(self.root, from_=0, to=100, orient="horizontal", length=200)
        self.progress_bar.pack(pady=10)

    def toggle_recording(self):
        if self.recording:
            self.recording = False
            self.record_button.config(text="Iniciar Gravação")
            self.status_label.config(text="Gravação finalizada.")
            self.save_video_with_audio()  # Salva o vídeo e áudio depois que a gravação parar
        else:
            self.recording = True
            self.record_button.config(text="Parar Gravação")
            self.status_label.config(text="Gravando vídeo...")
            self.progress_bar.set(0)
            self.frames = []  # Limpa a lista de frames
            self.frames_audio = []  # Limpa a lista de frames de áudio
            self.timelapse_segments = []  # Limpa os segmentos de timelapse
            self.start_time = time.time()  # Define o tempo de início da gravação

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
            self.save_audio()
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

    def record_screen(self):
        output_file = "output_video.mp4"
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
                        self.progress_bar.set(min(100, self.progress_bar.get() + 1))

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
        try:
            # Pergunta pelo complemento
            complement = simpledialog.askstring("Complemento", "Digite um complemento para o nome do arquivo (deixe em branco para 'timelapse-screencast'):")

            if not complement:
                complement = "timelapse-screencast"

            # Formata a data e hora
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

            # Define o nome do arquivo final
            file_name = f"{timestamp}-{complement}.mp4"

            # Carrega o vídeo e o áudio
            video_clip = VideoFileClip("output_video.mp4")
            if os.path.exists("output_audio.wav"):
                audio_clip = AudioFileClip("output_audio.wav")
            else:
                print("Arquivo de áudio não encontrado.")
                audio_clip = None

            # Adiciona o áudio no vídeo, se disponível
            if audio_clip:
                video_with_audio = video_clip.with_audio(audio_clip)
            else:
                video_with_audio = video_clip

            # Salva o vídeo final com áudio ajustado
            video_with_audio.write_videofile(file_name, codec="libx264", threads=1)

            # Limpa os arquivos temporários
            os.remove("output_video.mp4")
            if os.path.exists("output_audio.wav"):
                os.remove("output_audio.wav")
            print(f"Arquivo salvo como '{file_name}'.")

        except Exception as e:
            print(f"Erro ao salvar o vídeo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.config(bg="lightblue")
    app = VideoRecorderApp(root)
    root.mainloop()
