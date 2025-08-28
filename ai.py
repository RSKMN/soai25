import difflib
import tempfile
from transformers import pipeline
import speech_recognition as sr
from gtts import gTTS

class AIProcessor:
    def __init__(self):
        # Initialize Speech Recognizer (uses Google Web API)
        self.recognizer = sr.Recognizer()
        # Initialize HuggingFace zero-shot classification for text analysis
        self.classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
        # gTTS for Telugu text-to-speech

    def speech_to_text(self, audio_path):
        # Convert audio to WAV format using pydub externally if needed
        # Here assumes a WAV audio file input
        with sr.AudioFile(audio_path) as source:
            audio = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio, language='te-IN')
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Recognition request error; {e}"

    def text_analysis(self, text, candidate_labels=None):
        if candidate_labels is None:
            candidate_labels = ['wisdom', 'life', 'humor', 'education', 'motivation',
                                'child', 'region:Andhra Pradesh', 'region:Telangana', 'difficulty:easy',
                                'difficulty:medium', 'difficulty:hard']
        result = self.classifier(text, candidate_labels)
        return [{"label": l, "score": s} for l, s in zip(result['labels'], result['scores']) if s > 0.1]

    def text_to_speech(self, text, lang='te'):
        tts = gTTS(text=text, lang=lang)
        audio_fp = tempfile.mktemp(suffix='.mp3')
        tts.save(audio_fp)
        return audio_fp

    def compare_texts(self, original, transcription):
        seq = difflib.SequenceMatcher(None, original, transcription)
        return seq.ratio()

# Example usage
if __name__ == '__main__':
    ai = AIProcessor()

    # Suppose you have a Telugu WAV audio file at 'telugu_audio.wav'
    # transcription = ai.speech_to_text('telugu_audio.wav')
    # print('Transcription:', transcription)

    proverb_text = "ముద్దుల పుద్ధుల, పుద్ధుల ముద్దుల"
    analysis = ai.text_analysis(proverb_text)
    print('Text Analysis:', analysis)

    tts_audio = ai.text_to_speech(proverb_text)
    print('TTS audio file generated at:', tts_audio)

    similarity = ai.compare_texts(proverb_text, "తెగిన వెన్న మీద ముసి దాలే లేదు")
    print('Similarity score:', similarity)

    print(ai.speech_to_text("C:\\Users\\DELL\\AppData\\Local\\Temp\\tmp_5ws12sd.mp3"))