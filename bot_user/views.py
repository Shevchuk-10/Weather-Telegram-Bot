from rest_framework.views import APIView
from rest_framework.response import Response
from bot_user.serializers import UserInfoSerializer



# Create your views here.
class UserInfo(APIView):
    def post(self,request):
        serializer = UserInfoSerializer(data = request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=201)


        return Response(data={}, status=400)



