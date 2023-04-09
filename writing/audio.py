from django.http import StreamingHttpResponse
from google.cloud import texttospeech
import io
from rest_framework.views import APIView

class TextToSpeechAPI(APIView):
    def post(self, request):
        text = request.data.get('text')
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        audio_content = io.BytesIO(response.audio_content)
        response = StreamingHttpResponse(audio_content, content_type='audio/mpeg')
        response['Content-Disposition'] = 'attachment; filename="audio.mp3"'
        return response
    
#다운해서 확인하는용#
class TextToSpeechServerdownAPI(APIView):
    def post(self, request):
        text = request.data.get('text')
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        audio_content = io.BytesIO(response.audio_content)
        
        # 파일로 저장
        with open('audio.mp3', 'wb') as f:
            f.write(audio_content.getbuffer())
        
        # StreamingHttpResponse로 클라이언트에게 반환
        audio_content.seek(0)
        response = StreamingHttpResponse(audio_content, content_type='audio/mpeg')
        response['Content-Disposition'] = 'attachment; filename="audio.mp3"'
        return response