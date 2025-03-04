import sys
from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import Crop

def transformar_video_vertical(input_path, output_path):
    # Carregar o vídeo original
    video = VideoFileClip(input_path)

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
    video_vertical = CompositeVideoClip([metade_esquerda, metade_direita], size=(nova_largura, nova_altura))

    # Salvar o novo vídeo em formato vertical
    video_vertical.write_videofile(output_path, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    input_video = sys.argv[1] if len(sys.argv) > 1 else "input_video.mp4"
    output_video = "output_video_vertical.mp4"

    transformar_video_vertical(input_video, output_video)
