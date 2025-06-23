from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework import renderers
from rest_framework.views import APIView

from quiz_api.permissions import IsOwnerOrReadOnly
from quizcore.models import Quiz
from quizcore.serializers import (
    QuizDetailSerializer,
    QuizListSerializer,
    UserSerializer,
)


# Create your views here.

# class QuizViewSet(viewsets.ModelViewSet):
#     queryset = Quiz.objects.all()
#     serializer_class = QuizListSerializer


# @api_view(["GET", "POST"])
# def quiz_list(request):
#     if request.method == "GET":
#         quizzes = Quiz.objects.all()
#         serializer = QuizListSerializer(quizzes, many=True)
#         return Response(serializer.data)
#     elif request.method == "POST":
#         serializer = QuizListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class QuizList(ListCreateAPIView):
#     queryset = Quiz.objects.all()
#     serializer_class = QuizListSerializer
#     permission_classes = [IsOwnerOrReadOnly]

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)


# @api_view(["GET", "PUT", "DELETE"])
# def quiz_detail(request, pk):
#     try:
#         quiz = Quiz.objects.get(pk=pk)
#     except Quiz.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == "GET":
#         serializer = QuizListSerializer(quiz)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = QuizListSerializer(quiz, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == "DELETE":
#         quiz.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class QuizDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Quiz.objects.all()
#     serializer_class = QuizListSerializer
#     permission_classes = [IsOwnerOrReadOnly]


# class QuestionList():
#     queryset = Question.objects.all()
#     serializer_class = QuestionListSerializer


# class QuizOwner(generics.GenericAPIView):
#     queryset = Quiz.objects.all()
#     serializer_class = QuizListSerializer

#     def get(self, request, *args, **kwargs):
#         quiz = self.get_object()
#         return Response(quiz.owner.username)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizListSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def owner(self, request, *args, **kwargs):
        quiz = self.get_object()
        return Response(quiz.owner.username)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class QuizDetailViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
