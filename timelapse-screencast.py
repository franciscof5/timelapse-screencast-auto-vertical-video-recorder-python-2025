import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.boxlayout import BoxLayout
import cv2
import numpy as np
import mss
import time
import datetime
from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import Crop

kivy.require('2.1.0')  # Verifique a versão do Kivy

class ScreenRecorderApp(App):
    def build(self):
        # Layout com orientação vertical e limitações de tamanho
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint=(None, None), width=300, height=200)

        # Botão de gravar/Parar
        self.gravar_button = Button(text="Iniciar Gravação", size_hint=(None, None), width=200, height=40)
        self.gravar_button.bind(on_press=self.toggle_gravacao)
        
        # Campo para FPS
        self.fps_input = TextInput(text="30", multiline=False, size_hint=(None, None), width=100, height=30)
        
        # Switch para FPS personalizado
        self.fps_switch = Switch(active=False, size_hint=(None, None), width=100, height=50)
        
        # Adicionando widgets ao layout
        layout.add_widget(self.gravar_button)
        layout.add_widget(self.fps_input)
        layout.add_widget(self.fps_switch)

        return layout

    def toggle_gravacao(self, instance):
        if self.gravar_button.text == "Iniciar Gravação":
            self.gravar_button.text = "Parar Gravação"
            # Iniciar a gravação
            self.start_recording()
        else:
            self.gravar_button.text = "Iniciar Gravação"
            # Parar a gravação
            self.stop_recording()

    def start_recording(self):
        # Gerar o prefixo com data e hora
        prefix = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
        video_filename = f"{prefix}-f5-screen-rec.mp4"
        
        # Iniciar gravação da tela
        self.record_screen(video_filename)

    def stop_recording(self):
        print("Gravação parada!")
        # Aqui você poderia adicionar a lógica para parar a gravação, salvando o arquivo final
        
    def record_screen(self, output_file="output.mp4", capture_interval=1):
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Captura o monitor principal
            width, height = monitor["width"], monitor["height"]
            
            # Define o codec e cria o gravador de vídeo com FPS elevado
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            output_fps = int(self.fps_input.text) if self.fps_switch.active else 30  # FPS dinâmico
            out = cv2.VideoWriter(output_file, fourcc, output_fps, (width, height))

            print("Gravação iniciada. Pressione Ctrl+C para parar...")

            try:
                while True:  # Loop contínuo até Ctrl+C
                    screenshot = sct.grab(monitor)  # Captura a tela
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    # Adiciona o quadro capturado no arquivo com o tempo correto para aceleração
                    out.write(frame)
                    
                    # Espera para a próxima captura a cada 1 segundo
                    time.sleep(capture_interval)  # Aguarda 1 segundo para a próxima captura

            except KeyboardInterrupt:
                print("\nGravação finalizada.")
            finally:
                out.release()  # Libera o vídeo

        # Após a gravação, gerar o vídeo nos dois formatos: horizontal e vertical
        self.create_videos(output_file)

    def create_videos(self, input_file):
        video = VideoFileClip(input_file)

        # Formato Horizontal
        horizontal_output = f"horizontal-{input_file}"
        video.write_videofile(horizontal_output, codec="libx264", audio_codec="aac")
        print(f"Vídeo horizontal salvo como {horizontal_output}")

        # Formato Vertical
        vertical_output = f"vertical-{input_file}"
        video_vertical = self.transform_to_vertical(video)
        video_vertical.write_videofile(vertical_output, codec="libx264", audio_codec="aac")
        print(f"Vídeo vertical salvo como {vertical_output}")

    def transform_to_vertical(self, video):
        # Dimensões originais
        largura, altura = video.size

        # Calcular nova largura e altura
        nova_largura = largura // 2  # Metade da largura original
        nova_altura = altura * 2  # O dobro da altura original

        # Criar os cortes das metades usando Crop
        crop_esquerdo = Crop(x1=0, width=nova_largura)
        crop_direito = Crop(x1=nova_largura, width=nova_largura)

        metade_esquerda = crop_esquerdo.apply(video)
        metade_direita = crop_direito.apply(video)

        # Posicionar as metades corretamente
        metade_esquerda = metade_esquerda.with_position(("center", altura))  # Parte de cima
        metade_direita = metade_direita.with_position(("center", 0))  # Parte de baixo

        # Criar o vídeo final empilhando as duas partes
        vertical_video = CompositeVideoClip([metade_esquerda, metade_direita], size=(nova_largura, nova_altura))

        return vertical_video


if __name__ == '__main__':
    ScreenRecorderApp().run()
