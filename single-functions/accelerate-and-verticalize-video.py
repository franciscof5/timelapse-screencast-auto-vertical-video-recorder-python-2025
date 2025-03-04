import sys
from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import MultiplySpeed, Crop

def acelerar_video(video, duracao_final=80):
    # Calcular o fator de aceleração necessário
    duracao_original = video.duration
    fator_aceleracao = duracao_original / duracao_final
    
    # Criar o efeito de aceleração
    efeito = MultiplySpeed(fator_aceleracao)
    
    # Aplicar o efeito ao vídeo
    return efeito.apply(video)

def transformar_video_vertical(video):
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
    return CompositeVideoClip([metade_esquerda, metade_direita], size=(nova_largura, nova_altura))

def processar_video(input_path, output_path, duracao_final=80):
    # Carregar o vídeo original
    video = VideoFileClip(input_path)
    
    # Acelerar o vídeo
    video_acelerado = acelerar_video(video, duracao_final)
    
    # Transformar o vídeo para a versão vertical
    video_vertical = transformar_video_vertical(video_acelerado)
    
    # Salvar o novo vídeo
    video_vertical.write_videofile(output_path, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    input_video = sys.argv[1] if len(sys.argv) > 1 else "input_video.mp4"
    output_video = "output_video_final.mp4"  # Caminho para salvar o vídeo final

    processar_video(input_video, output_video)
