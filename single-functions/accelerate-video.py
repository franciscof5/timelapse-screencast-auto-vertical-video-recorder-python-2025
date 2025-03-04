import sys
from moviepy import VideoFileClip
from moviepy.video.fx import MultiplySpeed

def acelerar_video(input_path, output_path, duracao_final=50):
    # Carregar o vídeo original
    video = VideoFileClip(input_path)
    
    # Calcular o fator de aceleração necessário
    duracao_original = video.duration
    fator_aceleracao = duracao_original / duracao_final
    
    # Criar o efeito de aceleração
    efeito = MultiplySpeed(fator_aceleracao)
    
    # Aplicar o efeito ao vídeo
    video_acelerado = efeito.apply(video)
    
    # Salvar o vídeo acelerado
    video_acelerado.write_videofile(output_path, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    # Verificar se o caminho do vídeo foi passado como argumento
    input_video = sys.argv[1] if len(sys.argv) > 1 else "input_video.mp4"
    output_video = "output_video_acelerado.mp4"  # Caminho para salvar o vídeo acelerado

    acelerar_video(input_video, output_video)
