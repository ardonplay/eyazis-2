import asyncio
import edge_tts
import pyaudio
from io import BytesIO
from pydub import AudioSegment

VOICE = "ru-RU-SvetlanaNeural"
CHUNK_SIZE = 20



class TTS:
    def __init__(self):
        self.voice = VOICE
        self.pyaudio_instance = None
        self.audio_stream = None
        
    def change_voice(self, voice):
        self.voice = voice
        
    def get_current_voice(self):
        return self.voice

    def open_stream(self):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    def stop_stream(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.pyaudio_instance.terminate()

    async def synthese_text(self, text: str) -> None:
        communicator = edge_tts.Communicate(text=text, voice=self.voice)
        audio_chunks = []

        async for chunk in communicator.stream():
            if chunk["type"] == "audio" and chunk["data"]:
                audio_chunks.append(chunk["data"])
                if len(audio_chunks) >= CHUNK_SIZE:
                    await self.play_audio_chunks(audio_chunks)
                    audio_chunks.clear()

        await self.play_audio_chunks(audio_chunks)

    async def play_audio_chunks(self, chunks: list[bytes]) -> None:
        audio_data = AudioSegment.from_mp3(BytesIO(b''.join(chunks))).raw_data
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.audio_stream.write, audio_data)