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
from kivy.uix.textinput import TextInput  # Importa o TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from threading import Thread
import moviepy.video.fx as vfx
import os

class VideoRecorderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (300, 200)
        self.timelapse_fps = 5  # FPS inicial
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
        self.start_time = None  # Tempo de início da gravação
        self.timelapse_text = None  # Campo de texto para registrar os tempos

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
        # self.timelapse_button = Button(text="Ativar Timelapse", size_hint=(1, 0.1))
        # self.timelapse_button.bind(on_press=self.toggle_timelapse)
        # self.root.add_widget(self.timelapse_button)

        # # Campo de texto para registrar os tempos de timelapse
        # self.timelapse_text = TextInput(hint_text="Tempos de timelapse", size_hint=(1, 0.2), multiline=True)
        # self.root.add_widget(self.timelapse_text)

        return self.root
    
    def toggle_timelapse(self, instance):
        # Alterna entre ativado e desativado
        if self.timelapse_fps == 1:
            self.timelapse_fps = 30
            self.timelapse_button.text = "Ativar Timelapse"
            state = "Desativado"
            self.timelapse_segments.append((False, time.time()))  # Marca o tempo em que foi desativado
        else:
            self.timelapse_fps = 1
            self.timelapse_button.text = "Desativar Timelapse"
            state = "Ativado"
            self.timelapse_segments.append((True, time.time()))  # Marca o tempo em que foi ativado

        # Atualiza o campo de texto com o tempo decorrido e o estado
        elapsed_time = time.time() - self.start_time
        # self.timelapse_text.text += f"Timelapse {state} em {elapsed_time:.2f} segundos\n"

    def toggle_recording(self, instance):
        if self.recording:
            self.recording = False
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
            # self.timelapse_text.text = ""  # Limpa o campo de texto
            self.start_time = time.time()  # Define o tempo de início da gravação

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
        try:
            # Carrega o vídeo e o áudio
            video_clip = VideoFileClip("output_video.mp4")
            if os.path.exists("output_audio.wav"):
                audio_clip = AudioFileClip("output_audio.wav")
            else:
                print("Arquivo de áudio não encontrado.")
                audio_clip = None

            audio_clip = None
            # Aplica o efeito de timelapse nos segmentos anotados
            # for state, timestamp in self.timelapse_segments:
            #     relative_time = timestamp - self.start_time  # Tempo relativo ao vídeo
            #     if state:  # Timelapse ativado
            #         video_clip = video_clip.subclipped(relative_time, video_clip.duration)  # Pega o clipe da ativação até o final
            #         # video_clip = vfx.speedx(video_clip, factor=0.03)  # Aplica o efeito de aceleração

            # Adiciona o áudio no vídeo, se disponível
            if audio_clip:
                video_with_audio = video_clip.with_audio(audio_clip)
            else:
                video_with_audio = video_clip

            # Salva o vídeo final com áudio ajustado
            video_with_audio.write_videofile("output_final.mp4", codec="libx264", threads=1)

            # Limpa os arquivos temporários
            os.remove("output_video.mp4")
            if os.path.exists("output_audio.wav"):
                os.remove("output_audio.wav")
            print("Arquivos temporários removidos.")

            # time.sleep(3)
            # self.split_video_based_on_timelapse()
        except Exception as e:
            print(f"Erro ao salvar o vídeo: {e}") 
    
    def split_video_based_on_timelapse(self, video_file="output_final.mp4"):
        try:
            # Carrega o vídeo final
            video_clip = VideoFileClip(video_file)

            # Lista para armazenar os segmentos de vídeo
            video_segments = []

            # Variáveis de controle para o segmento atual
            last_timestamp = 0  # Tempo inicial do vídeo

            # Processa os segmentos de timelapse
            for state, timestamp in self.timelapse_segments:
                # Converte o timestamp absoluto para um tempo relativo ao vídeo
                relative_time = timestamp - self.start_time

                # Garante que o tempo não ultrapasse a duração do vídeo
                if relative_time > video_clip.duration:
                    break

                # Adiciona o segmento normal (antes do timelapse)
                if last_timestamp < relative_time:
                    normal_segment = video_clip.subclipped(last_timestamp, relative_time)
                    video_segments.append(normal_segment)

                # Adiciona o segmento acelerado (timelapse)
                if state:  # Timelapse ativado
                    # Encontra o próximo timestamp (ou o final do vídeo)
                    next_timestamp = (
                        self.timelapse_segments[self.timelapse_segments.index((state, timestamp)) + 1][1] - self.start_time
                        if self.timelapse_segments.index((state, timestamp)) + 1 < len(self.timelapse_segments)
                        else video_clip.duration
                    )
                    # Garante que o próximo timestamp não ultrapasse a duração do vídeo
                    next_timestamp = min(next_timestamp, video_clip.duration)

                    # Cria o segmento acelerado
                    timelapse_segment = video_clip.subclipped(relative_time, next_timestamp)
                    # timelapse_segment = timelapse_segment.fx(vfx.speedx, factor=10)  # Acelera 10x
                    video_segments.append(timelapse_segment)

                    # Atualiza o último timestamp processado
                    last_timestamp = next_timestamp

            # Adiciona o último segmento (se houver)
            if last_timestamp < video_clip.duration:
                final_segment = video_clip.subclipped(last_timestamp, video_clip.duration)
                video_segments.append(final_segment)

            # Salva os segmentos de vídeo
            for i, segment in enumerate(video_segments):
                segment_file = f"segment_{i + 1}.mp4"
                segment.write_videofile(segment_file, codec="libx264", threads=1)
                print(f"Segmento {i + 1} salvo em {segment_file}")

            print(f"{len(video_segments)} segmentos salvos com sucesso.")
        except Exception as e:
            print(f"Erro ao dividir o vídeo: {e}")

if __name__ == "__main__":
    VideoRecorderApp().run()
