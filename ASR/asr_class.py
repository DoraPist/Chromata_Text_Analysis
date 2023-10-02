import whisper
from pyannote.audio import Pipeline
import torch
import numpy as np


class ASR():

    def __init__(self, do_vad=True, do_diarization=False):

        self.model = whisper.load_model("small")
        self.script = ''
        self.do_vad = do_vad
        self.do_diarization = do_diarization
        if self.do_vad:
            self.vad_pipeline = Pipeline.from_pretrained("pyannote/voice-activity-detection",
                                                         use_auth_token="")   # Get token from hugging face.
        if self.do_diarization:
            self.diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                                                 use_auth_token="")   # Get token from hugging face.

    def vad(self, signal, sample_rate):

        start = []
        end = []
        
        output = self.vad_pipeline({'waveform': torch.from_numpy(signal.reshape((1, -1))), 'sample_rate': sample_rate})

        for count, speech in enumerate(output.get_timeline().support()):
            if count == 0:
                s_vad = signal[int(speech.start * sample_rate):int(speech.end * sample_rate)]
                continue

            s_vad = np.concatenate((s_vad, signal[int(speech.start * sample_rate):int(speech.end * sample_rate)]))

        return s_vad

    def diarization(self, signal, sample_rate):

        speaker_seperated_audio_list = []
        # pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token="")  # Get token from hugging face.
        output = self.diarization_pipeline(
            {'waveform': torch.from_numpy(signal.reshape((1, -1))), 'sample_rate': sample_rate})

        for turn, _, speaker in output.itertracks(yield_label=True):
            #print('turn: ', turn)
            #print('speaker: ', speaker)
            speaker_seperated_audio_list.append(signal[round(turn.start * sample_rate):round(turn.end * sample_rate)])

        return speaker_seperated_audio_list

    def run_ASR(self, s, sr):
        if self.do_vad:
            s = self.vad(s, sr)
        if self.do_diarization:
            s = self.diarization(s, sr)
            temp_list = []
            for i in range(len(s)):
                temp_list.append('- ' + self.model.transcribe(s[i])['text'])

            self.script = '\n'.join(temp_list)
        else:
            self.script = self.model.transcribe(s)['text']

        return self.script
    
