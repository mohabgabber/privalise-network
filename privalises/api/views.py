from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class LoginUser(APIView):
    def post(self, request):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is not None and user.is_active :
            token, created = Token.objects.get_or_create(user = user)
            return Response({'message': 'Sucessfull', 'token': token.key}, status=200)
        else:
            return Response({'message':'Invalid username or password'}, status = 403)


class RegisterUser(APIView):
    def post (self, request):
    
        if request.data['password1'] !=  request.data['password2']:
    
            return Response({'message':'Password Not Matching'}, status = 401)
        try:
            user = User.objects.create_user(username=request.data['username'], password = request.data['password1'], email = request.data['email'])


            user.save()
            token = Token.objects.create(user=user)

            return Response({'message':'Sucessful'}, status = 200)
        except Exception as e:
            print(e)
            return Response({'message':'Username already exists'}, status = 422)