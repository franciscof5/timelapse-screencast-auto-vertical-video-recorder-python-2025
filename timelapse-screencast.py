import cv2
import numpy as np
import mss
import time
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import Crop

# Variável global para controle da gravação
recording = False

def get_filename():
    """Gera um nome de arquivo baseado na data e hora."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    return f"{timestamp}-screen-rec.mp4"

def record_screen():
    """Função para iniciar a gravação da tela."""
    global recording
    recording = True
    output_file = get_filename()
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Captura o monitor principal
        width, height = monitor["width"], monitor["height"]
        
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = 30  # Define FPS do vídeo
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        print("Gravação iniciada...")

        while recording:
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            out.write(frame)
            time.sleep(1 / fps)  # Controle de tempo entre capturas

        out.release()
        print(f"Gravação salva em {output_file}")

        # Converter para vertical automaticamente
        transformar_video_vertical(output_file)

def stop_recording():
    """Função para parar a gravação."""
    global recording
    recording = False
    messagebox.showinfo("Parar", "Gravação finalizada!")

def transformar_video_vertical(video_path):
    """Transforma o vídeo gravado para o formato vertical."""
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
    metade_esquerda = metade_esquerda.with_position(("center", altura))  # Parte de cima
    metade_direita = metade_direita.with_position(("center", 0))  # Parte de baixo

    # Criar o vídeo final empilhando as duas partes
    vertical_video = CompositeVideoClip([metade_esquerda, metade_direita], size=(nova_largura, nova_altura))

    # Salvar o vídeo vertical
    output_path = video_path.replace(".mp4", "_vertical.mp4")
    vertical_video.write_videofile(output_path, codec="libx264", fps=30)

    print(f"Vídeo vertical salvo como {output_path}")

# Criar a interface gráfica (GUI)
root = tk.Tk()
root.title("Gravador de Tela")

btn_start = tk.Button(root, text="Gravar", command=lambda: threading.Thread(target=record_screen).start(), height=2, width=15, bg="green", fg="white")
btn_start.pack(pady=10)

btn_stop = tk.Button(root, text="Parar", command=stop_recording, height=2, width=15, bg="red", fg="white")
btn_stop.pack(pady=10)

root.mainloop()
