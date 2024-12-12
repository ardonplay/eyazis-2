import asyncio
import subprocess
import vosk
import sys
import sounddevice as sd
import json
import queue
from ollama import Client
import weatherService
import tts


client = Client(
  host="https://bc28-34-142-151-188.ngrok-free.app/" 
)


class OfflineSpeechRecognitionTTS:
    def __init__(self, model_path='./model', sample_rate=16000):
        self.commands = {
            "пятница": lambda: self.say("Да, босс"),
            "включи музыку": self.play_music,
            "выключи музыку": self.stop_music,
            "какая сейчас температура": self.get_weather,
            "открой телегу": lambda: self.open_app("/Applications/Telegram.app"),
            "закрой телегу": lambda: self.close_app("Telegram"),
            "поменяй голос": self.change_voice
        }
        self.tts = tts.TTS()
        self.tts.open_stream()
        try:
            vosk.SetLogLevel(-1)  # Отключение логов
            self.model = vosk.Model(model_path)
            self.sample_rate = sample_rate
            self.device = None
            self.queue = queue.Queue()
            self.is_playing = False
            self.neuralmodule = None;
        except Exception as e:
            print(f"Ошибка инициализации: {e}")
            sys.exit(1)

        
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        if not self.is_playing:
            self.queue.put(bytes(indata))
    async def change_voice(self):
        if(self.tts.get_current_voice() == "ru-RU-DmitryNeural"):
            self.tts.change_voice("ru-RU-SvetlanaNeural")
        else:
            self.tts.change_voice("ru-RU-DmitryNeural")
        await self.say("Так лучше?")

    async def execute_command(self, text):
        for command, action in self.commands.items():
            if command in text:
                print(f"Команда распознана: {command}")
                await action()  # Теперь будет вызываться через лямбду
                return True
        return False

    def toggle_microphone(self, state):
        self.is_playing = not state

    async def play_music(self):
        self.toggle_microphone(False)
        await self.tts.synthese_text("Воспроизведение музыки...")
        self.toggle_microphone(True)

    async def open_app(self, app_name):
        try:
            # Используем асинхронный запуск процесса
            subprocess.run(["open", app_name], check=True)
            
        except Exception as e:
            await self.say(f"Простите, босс, не могу открыть {app_name}")
            
            print(f"Ошибка открытия приложения {app_name}: {e}")
            
    async def close_app(self, app_name):
        try:
            # Используем асинхронный запуск процесса
            subprocess.run(["pkill", app_name], check=True)
            
        except Exception as e:
            await self.say(f"Простите, босс, не могу закрыть {app_name}")
            
            print(f"Ошибка открытия приложения {app_name}: {e}")
            
    async def stop_music(self):
        await self.say("Остановка музыки...")
       

    async def get_weather(self):
        weather = await weatherService.get_weather("Minsk")
        print("Temperature: " + str(weather))
        await self.say("Сейчас в Минске " + str(weather) + "градуса по цельсию")
        
        
    async def say(self, text):
        self.toggle_microphone(False)
        await self.tts.synthese_text(text=text)
        self.toggle_microphone(True)

    async def synthesize_text(self, text):
        await self.tts.synthese_text(text)
        self.toggle_microphone(True)

    async def process_stream(self, text):
     
        if(self.neuralmodule is None):
            await self.say("Активирую нейромодуль...")
        self.neuralmodule = client.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': text}],
            stream=True,
        )
        result = []
        for chunk in self.neuralmodule:
            print(chunk['message']['content'], end='', flush=True)
            result.append(chunk['message']['content'])
            
        await self.say("".join(result).replace('*', ''))
        print("\n")


    async def recognize_speech(self):
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=self.audio_callback,
            device=self.device,
        ):
            recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            print("Начните говорить (нажмите Ctrl+C для остановки)...")

            try:
                while True:
                    data = self.queue.get()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get('text', '').strip()
                        if text:
                            print("User:", text)
                            if not await self.execute_command(text):
                                await self.process_stream(text)
            except KeyboardInterrupt:
                print("\nРаспознавание остановлено.")
            finally:
                self.tts.stop_stream()
                print("Завершение...")


async def main():
    recognizer = OfflineSpeechRecognitionTTS(model_path='./vosk-model-small-ru-0.22')
    await recognizer.recognize_speech()


if __name__ == "__main__":
    asyncio.run(main())
