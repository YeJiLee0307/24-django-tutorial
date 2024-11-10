# Create your views here.
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.mixins import (
    ListModelMixin,
    DestroyModelMixin,
    CreateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Study, StudyParticipation
from django.contrib.auth import login, authenticate
from main.serializers import (
    StudySerializer,
    LoginSerializer,
    UserSerializer, StudyParticipationSerializer
)
from rest_framework import generics, status
from main.models import StudyParticipation




class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if not user:
            raise AuthenticationFailed("아이디 또는 비밀번호가 틀렸습니다")

        login(request, user)

        return Response()


class SignupView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = UserSerializer


class StudyListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Study.objects.all()
    serializer_class = StudySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StudyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Study.objects.all()
    serializer_class = StudySerializer

    def get_queryset(self):
        if self.request.method == "GET":
            return super().get_queryset()

        return super().get_queryset().filter(created_by=self.request.user)


class StudyParticipationListView(
    ListModelMixin,
    CreateModelMixin,
    GenericAPIView,
):
    """
    GET: 내 스터디 참여 목록. 남의 것이 조회되면 안됩니다.
    POST: 내 스터디 참여 목록 추가. 남의 것을 추가할 수 없습니다(HTTP 403 에러)
    """

    ### assignment3: 이곳에 과제를 작성해주세요

class StudyParticipationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudyParticipationSerializer
    queryset = StudyParticipation.objects.all()

    def get_queryset(self):
        # 로그인한 사용자의 스터디 참여 이력만
        return StudyParticipation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 로그인한 사용자로 참여 이력을 생성
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.data.get('user') and int(request.data['user']) != request.user.id:
            return Response(
                {"detail": "내 스터디 참여 목록 추가. 남의 것을 추가할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        return self.create(request, *args, **kwargs)
    ### end assignment3


class StudyParticipationView(
    DestroyModelMixin,
    GenericAPIView,
):
    """
    DELETE: 내 스터디 참여 목록 제거. 남의 것을 제거할 수 없습니다(HTTP 404 에러)
    """

    ### assignment3: 이곳에 과제를 작성해주세요
    queryset = StudyParticipation.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StudyParticipationSerializer

    def get_queryset(self):
        # 로그인한 사용자의 참여 이력만 조회
        return StudyParticipation.objects.filter(user=self.request.user)

    # DELETE 요청 처리
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    ### end assignment3
