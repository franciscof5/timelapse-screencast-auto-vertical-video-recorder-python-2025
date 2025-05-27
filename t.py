import mss
import time
import numpy as np
from PIL import Image
import imageio
import os

def record_screen(timelapse_fps, recording_time, output_file="output_video.mp4"):
    capture_interval = 1 / timelapse_fps  # Ajustado para utilizar o FPS de timelapse
    last_frame_time = time.perf_counter()

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Captura o monitor principal
        width, height = monitor["width"], monitor["height"]

        print("Gravação iniciada.")
        try:
            start_time = time.perf_counter()
            frame_counter = 0
            frames = []  # Lista para armazenar os frames como imagens PIL

            while time.perf_counter() - start_time < recording_time:  # Grava por 5 segundos
                current_time = time.perf_counter()
                elapsed_time = current_time - last_frame_time

                # Verifica se o intervalo de captura foi atingido
                if elapsed_time >= capture_interval:
                    print(f"current_time: {current_time}")
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)
                    frame = frame[..., :3]  # Remove o canal alfa (BGRA para BGR)

                    # Converte o frame de BGRA para RGB
                    frame = frame[..., ::-1]  # Inverte a ordem das cores para RGB

                    # Converte para imagem PIL
                    image = Image.fromarray(frame)
                    frames.append(np.array(image))  # Converte de volta para array NumPy e adiciona à lista

                    # Atualiza o tempo do último frame capturado
                    last_frame_time = current_time
                    frame_counter += 1

        except Exception as e:
            print(f"Erro na gravação: {e}")
        finally:
            # Após a captura de todos os frames, cria o vídeo
            print("Gravação finalizada. Criando vídeo...")
            
            # Usando imageio para criar o vídeo
            writer = imageio.get_writer(output_file, fps=timelapse_fps)

            for frame in frames:
                writer.append_data(frame)  # Adiciona cada frame ao vídeo

            writer.close()  # Finaliza a escrita do vídeo
            print(f"Vídeo gerado: {output_file}")

# Chama a função para iniciar a gravação
if __name__ == "__main__":
    timelapse_fps = 30  # FPS para o timelapse (captura um frame a cada 1/30 segundos)
    recording_time = 5  # Tempo total de gravação (5 segundos)
    
    record_screen(timelapse_fps, recording_time)
