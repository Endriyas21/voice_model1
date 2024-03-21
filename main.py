import geocoder
import openai
import time
import numpy as np
import sounddevice as sd
import pygame
import soundfile as sf
import os
import requests
import vlc

# Code for recording
fs = 44100  # Sample rate (IDK)
seconds_inactive = 3  # maximum duration of recording when inactive
seconds_active = 5  # maximum duration of recording when inactive
threshold = 0.003  # Adjust this threshold as needed, it is good so far
wait = 3  # wait time between checking the silence
api_key = "OpenAI_API_Key"
weatherAPI = "WeatherAPI_Key"
client = openai.OpenAI(api_key=api_key)


# Function to fetch weather data
def get_weather():
    g = geocoder.ipinfo('me').latlng
    r = requests.get(url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{g[0]}%2C{g[1]}?unitGroup=metric&include=days&contentType=json", params = {"key":weatherAPI})
    data = r.json()['days'][0]
    # Make a request to the weather API and fetch the required data
    # Extract the relevant information from the response
    a = complete_chat("Answer as if you were talking to an old person in a simple language. Give me a breif about todays weather based on this data in less than 50 words and include the location as the city based on the latitude given."+str(data),[])
    return complete_chat("Translate this to Korean \n"+a[0],[{"role": "system", "content": system_message}]) 

# Function to fetch news headlines


def get_news_headlines():
    g = geocoder.ip('me')

    # Make a request to the news API and fetch the required data
    response = requests.get(
        "https://newsapi.org/v2/top-headlines?country=YOUR_COUNTRY&apiKey=YOUR_API_KEY")
    data = response.json()
    # Extract the relevant information from the response
    headlines = [article["title"] for article in data["articles"]]
    return "Today's news headlines are: " + ", ".join(headlines)

# Function to generate daily report


def generate_daily_report():
    weather = get_weather()
    #news_headlines = get_news_headlines()
    #return f"{weather}. {news_headlines}."
    return weather
# function for recording whenever called. It stops recording whenever the max volume over the last four seconds is below a threshold, i.e. silence for four seconds. It stops if time passed 10 sec regardless, though.
# It returns a variable with the audio recorded


def recording(fs, seconds, threshold, wait, filename):
    fs = fs  # Sample rate (IDK)
    seconds = seconds  # maximum duration of recording
    threshold = threshold  # Adjust this threshold as needed, it is good so far

    def is_silence(audio_chunk, threshold):
        return np.max(np.abs(audio_chunk)) < threshold

    print("Recording starts now")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)

    i = 0  # index for checking the silence in the my recording variable as it goes
    start = time.time()  # starting time
    t_end = time.time() + seconds  # maximum end time

    while True:   # check the silence for the maximum time of the recording
        time.sleep(wait)
        audio_chunk = myrecording[i:i + wait*int(fs / seconds)]
        if is_silence(audio_chunk, threshold) or time.time() > t_end:
            sd.stop()
            print("recording stopped", np.max(np.abs(audio_chunk)))
            break  # Stop recording when silence is detected
        print(np.max(np.abs(audio_chunk)), "still recording")
        i += wait*int(fs / seconds)
    print("length of recording", time.time()-start, "seconds")
    # testing
    # sd.play(myrecording, fs)
    # status = sd.wait()
    sf.write(filename, myrecording, fs)

    return filename
# uncomment the next line to test
# recording(fs, seconds, threshold, wait)


#########################################################################################

# this code uses OpenAI API (ChatGPT) for chat completion. I used chat GPT to make it as a starting point but I understand all of it.
# We can give it a personality by changing the system message provided. We will need to API key and also connect the return to the database instead of being in a list in the code.
# Set your OpenAI API key


def complete_chat(input_message, conversation_history):

    # Append the user's input message to the conversation history
    conversation_history.append({"role": "user", "content": input_message})

    # Send the conversation history to the OpenAI API for completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_history,
        max_tokens=100  # Adjust the max_tokens as needed
    )

    # Extract the assistant's reply from the API response
    assistant_reply = response.choices[0].message.content

    # Append the assistant's reply to the conversation history
    conversation_history.append({"role": "system", "content": "assistant"})
    conversation_history.append(
        {"role": "assistant", "content": assistant_reply})

    return assistant_reply, conversation_history


# You can continue the conversation by providing more user input and calling complete_chat again.


def transcribe(file2):
    audio_file = open(file2, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    print("Transcription", transcript)
    return transcript


def TTS(input, file):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input,
    )

    try:
        pygame.quit()
    except:
        pass
    try:
        os.remove(file)
    except:
        pass
    response.stream_to_file(file)
    pygame.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # You can adjust the tick value as needed

    return input


# testing
# TTS(complete_chat(transcribe(recording(fs, 5, threshold, wait,"tempo.wav")),[])[0],"output.mp3")

# building class for chat bot
system_message = "당신의 이름은 캐리입니다. 당신은 노인을 돌보는 가상 비서입니다. 간호사처럼 말합니다. 부드럽고 도움이 되며, 배려 깊고, 매우 친절하게 이야기하세요. 음성 챗봇이기 때문에 물리적인 도움을 제공하지 않습니다. 또한 토론을 도우며, 건강뿐만 아니라 노인들을 일반적으로 도와드리고 있습니다."
class assistantbot:
    def __init__(self) -> None:
        self.active = False
        self.history = [{"role": "system", "content": system_message}]
        self.question_counter = 0
        self.first_time = None


        ### I commented some of the questions please make sure to edit later

        self.questions = [
            "오늘의 주요 계획은 무엇인가요? 어떤 알림을 설정해 드릴까요?",
            "오늘 괴롭히는 것이 있나요?",
            "몸에 아픈 부분이나 나쁜 감각이 느껴지나요?",
            "오늘은 평소와 다른 일을 했나요?",
            "기억하거나 기록해 두길 원하는 순간이나 추억이 있나요?",
            "오늘 어떤 운동을 하셨나요?",
            "약을 가지고 계신가요? 만약 그렇다면, 오늘 복용하셨나요?",
            "누군가와 공유하고 싶은 우려 사항이 있나요? 비밀로 유지하거나 주치의와 공유할 수 있습니다.",
            "오늘 무엇을 먹었나요? 식습관과 식욕은 어떤가요?",
            "어떤 주제에 대해 이야기하고 싶으세요?",
            "오늘 밖에 나가셨나요?",
            "오늘 다른 장소를 방문하셨나요?"
        ]
        self.user_responses = []

    # the inactive state when it listens and then check for wake up word
    def inactive_state(self):
        pygame.init()
        pygame.mixer.music.load("starter.mp3")
        pygame.mixer.music.play()
        time.sleep(4)
        print("We started program")
        while not self.active:
            transcription = transcribe(
                recording(fs, seconds_inactive, threshold, wait, "tempo.wav"))
            if "안녕하세요" in transcription or "야기야" in transcription or "야야톡" in transcription:
                print("We quitting inactive")
                p = vlc.MediaPlayer("http://codeskulptor-demos.commondatastorage.googleapis.com/pang/pop.mp3")
                p.play()
                self.active = True
                self.active_state()
                print("We are back to inactive")

    # the function that listens to what's after the wake up call
    def active_state(self):
        transcription = transcribe(
            recording(fs, seconds_inactive, threshold, wait, "active.wav"))
        if "daily report" in transcription.lower() or "일일 보고서" in transcription or "매일 리포트" in transcription:
            report = generate_daily_report()[0]
            print(report, "This is daily report")
            TTS(report, "report.mp3")
            self.history.append({"role": "user", "content": transcription})
            self.history.append({"role": "assisstant", "content": report})
        else:
            response = complete_chat(transcription, self.history)
            print(response[0])
            TTS(response[0], "output.mp3")
            self.history = response[1]

        if self.question_counter < 3:
            if self.question_counter == 0: 
                self.ask_questions() 
                self.question_counter += 1
                self.first_question_time = time.time()
            if (time.time() - self.first_question_time) >= 10800:
                self.ask_questions()

        self.active = False
        return response[0] if 'response' in locals() else report
    
    def ask_questions(self):
        responses = []
        for i in range(len(self.questions)): 
            TTS(self.questions[i], f"question{i + 1}.mp3")
            response_file = f"response{i + 1}.wav"
            questions_response = transcribe(recording(fs, seconds_inactive, threshold, wait, response_file))
            responses.append(self.questions[i]+questions_response)
            self.history.append({"role": "user", "content": self.questions[i]})
            self.history.append({"role": "assisstant", "content": questions_response})
        self.user_responses.append(responses)
    

m = assistantbot()
m.inactive_state()