import pyaudio
import wave
import time

class AudioRecorder:
    def __init__(self):
        self.recording_audio = False
        self.frames_audio = []

    def record_audio(self):
        # Inicializa o PyAudio
        p = pyaudio.PyAudio()

        # Abre o stream de áudio
        self.stream = p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=44100,
                             input=True,
                             frames_per_buffer=1024)

        print("Gravando áudio...")

        # Inicia a gravação de áudio
        self.recording_audio = True
        start_time = time.time()
        while self.recording_audio:
            data = self.stream.read(1024)
            self.frames_audio.append(data)  # Armazena o áudio
            # Limita o tempo de gravação para 5 segundos
            if time.time() - start_time > 5:
                self.stop_audio_recording()
                break

        self.save_audio()

    def stop_audio_recording(self):
        # Para a gravação de áudio
        if self.stream:
            print("Parando a gravação de áudio...")
            self.stream.stop_stream()
            self.stream.close()
            self.recording_audio = False
        else:
            print("Stream de áudio não iniciado corretamente.")

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

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.record_audio()
