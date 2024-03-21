class assistantbot:
    def __init__(self) -> None:
        self.active = False
        self.history = []
        self.question_counter = 0
        self.first_time = None 
        self.questions = [
            "How do you feel today?", 
            "Do you have any headaches or pain on your body?",
            "Have you felt any palpitations on your heart?",
            "Is your eyesight okay?"
        ]
        self.user_responses = []

    # the inactive state when it listens and then check for wake up word
    def inactive_state(self):
        print("We started program")
        while not self.active:
            transcription = transcribe(
                recording(fs, seconds_inactive, threshold, wait, "tempo.wav"))
            if "안녕하세요" in transcription.lower():
                print("We quitting inactive")
                self.active = True
                self.active_state()
                print("We are back to inactive")

    # the function that listens to what's after the wake up call
    def active_state(self):
        response = complete_chat(transcribe(
            recording(fs, seconds_inactive, threshold, wait, "active.wav")), self.history)
        print(response[0])
        TTS(response[0], "output.mp3")
        self.history = response[1]
        transcription = transcribe(
            recording(fs, seconds_inactive, threshold, wait, "active.wav"))
        if "daily report" in transcription.lower():
            report = generate_daily_report()
            print(report)
            TTS(report, "output.mp3")
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
        self.inactive_state()
        return response[0]
        return response[0] if 'response' in locals() else report
    
    def ask_questions(self):
        for i in range(len(self.questions)): 
            TTS(self.questions[i], f"question{i + 1}.mp3")
            response_file = f"response{i + 1}.wav"
            questions_response = transcribe(recording(fs, seconds_inactive, threshold, wait, response_file))
            self.user_responses.append([questions_response][i])


m = assistantbot()
