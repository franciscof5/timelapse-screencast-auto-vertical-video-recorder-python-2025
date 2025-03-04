import cv2
import numpy as np
import mss
import time
import sys
from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import Crop

# Função para gravar o vídeo acelerado até pressionar Ctrl+C
def record_screen(output_file="output.mp4", capture_interval=1, speedup_factor=60):
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Captura o monitor principal
        width, height = monitor["width"], monitor["height"]
        
        # Define o codec e cria o gravador de vídeo com FPS elevado
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_fps = 60  # FPS acelerado (60 FPS)
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

# Função para transformar o vídeo em versão vertical
def transformar_video_vertical(video_path, output_path):
    video = VideoFileClip(video_path)

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
    metade_esquerda = metade_esquerda.with_position(("center", 0))  # Parte de cima
    metade_direita = metade_direita.with_position(("center", altura))  # Parte de baixo

    # Criar o vídeo final empilhando as duas partes
    vertical_video = CompositeVideoClip([metade_esquerda, metade_direita], size=(nova_largura, nova_altura))
    
    # Salvar o vídeo vertical
    vertical_video.write_videofile(output_path, codec="libx264", fps=60)

    print(f"Vídeo vertical salvo como {output_path}")

# Caminhos para os arquivos de vídeo
video_path = "screen_timelapse.mp4"
video_vertical_path = "screen_timelapse_vertical.mp4"

# Passos
record_screen(video_path, capture_interval=1, speedup_factor=1)  # Grava o vídeo até Ctrl+C
transformar_video_vertical(video_path, video_vertical_path)  # Cria o vídeo vertical
