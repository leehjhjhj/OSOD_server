from django.test import TestCase

import base64

# 이미지 파일을 바이너리 모드로 읽어옵니다.
with open('server/static/image/logo.png', 'rb') as f:
    image_data = f.read()

# 이미지 데이터를 Base64로 인코딩합니다.
encoded_image = base64.b64encode(image_data).decode('utf-8')

# HTML 템플릿에서 사용할 수 있는 형식으로 변환합니다.
image_src = f"data:image/png;base64,{encoded_image}"
print(image_src)