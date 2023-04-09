from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.decorators import api_view, authentication_classes
from rest_framework import status
from .models import *
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def change_sub(request):
    user = request.user
    target = User.objects.get(id=user.id)
    if target.subscription:
        target.subscription = False
    else:
        target.subscription = True
    target.save(update_fields=['subscription'])

    return Response({
        "subscription": user.subscription,
    },status = status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def make_nickname(request):
    try:
        user = request.user
        get_nick = request.data.get('nickname')
        #get_name = request.data.get('name')
        if user.first_name:
            user.name = user.last_name + user.first_name
        user.nickname = get_nick
        user.save(update_fields=['nickname', 'name'])
        return Response({
            "nickname": user.nickname,
            'name': user.name
        },status = status.HTTP_200_OK)
    except:
        return Response({
            "detail": "중복이거나 형식이 잘못됐습니다.",
        },status = status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def change_nickname(request):
    user = request.user
    new_nick = request.data.get('nickname')
    if User.objects.filter(nickname=new_nick).exists():
        return Response({"detail": "중복된 닉네임 입니다."},status = status.HTTP_400_BAD_REQUEST)
    elif user.nickname == new_nick:
        return Response({"detail": "기존 닉네임과 동일합니다."},status = status.HTTP_400_BAD_REQUEST)
    
    user.nickname = new_nick
    user.save(update_fields=['nickname'])
    return Response({"nickname": user.nickname},status = status.HTTP_200_OK)