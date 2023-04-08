from rest_framework.response import Response
from rest_framework.views import APIView
from decouple import config, AutoConfig
import openai
from rest_framework import status
import random

def grammar_wrong_response():
    a = random.randrange(0,4)
    first = ['이런건 어때요?', '제가 한번 제안할게요!', '이게 더 자연스러울 수도 있어요!', '이게 더 나을 수도 있어요!', '이렇게 작문할 수도 있어요!']
    return f"{first[a]}"

def grammar_correct_response():
    a = random.randrange(0,4)
    first = ['완벽해요!', '틀린게 없는 문장이에요!', '너무 좋은걸요?', '완벽한 문장이에요!!', '굉장히 좋은 문장이에요!']
    return f"{first[a]}"

class GrammarCheckView(APIView):
    def post(self, request):
        openai.api_key = config('OPEN_AI')
        text = request.data.get('text')
        sentence = request.data.get('sentence')
        if not text:
            return Response({'response': "", 'ai': "검사할 문장이 없어요!", 'original': "", 'bool': False}, status=status.HTTP_400_BAD_REQUEST)
        
        response = openai.Completion.create(
            model="text-davinci-003",
            #prompt=f"'{text}' correct if grammar wrong. ",
            prompt=f"'{text}' correct grammar if wrong. Preserve contain '{sentence}' ",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        #return Response({'response': response, 'today': today_sentence}, status=status.HTTP_200_OK)
        target_res = response.choices[0].text.strip()
        if target_res[0] == "\"":
            cut_target = target_res.strip("\"")
            if text == cut_target:
                res = cut_target
                ai = grammar_correct_response()
                bool = True
            else:
                res = cut_target
                ai = grammar_wrong_response()
                bool = False

        else:
            if text == target_res:
                res = target_res
                ai = grammar_correct_response()
                bool = True
            else:
                res = target_res
                ai = grammar_wrong_response()
                bool = False

        # if text == response.choices[0].text.strip():
        #     res = response.choices[0].text.strip()
        #     ai = grammar_correct_response()
        #     bool = True

        return Response({'response': res, 'ai': ai, 'original': text, 'bool': bool}, status=status.HTTP_200_OK)