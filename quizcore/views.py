from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework import renderers
from rest_framework.views import APIView

from quiz_api.permissions import IsOwnerOrReadOnly
from quizcore.models import Quiz, Grade
from quizcore.serializers import (
    QuizDetailSerializer,
    QuizListSerializer,
    UserSerializer,
    QuizSubmissionSerializer,
    GradeSerializer,
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


class QuizGradingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.prefetch_related('questions__answers', 'questions__correct_answer').get(pk=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {"error": "Quiz not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user already has a grade for this quiz
        existing_grade = Grade.objects.filter(quiz=quiz, user=request.user).first()
        if existing_grade:
            return Response(
                {
                    "error": "You have already completed this quiz",
                    "grade": GradeSerializer(existing_grade).data
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = QuizSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        submitted_answers = serializer.validated_data['answers']
        
        # Validate that all questions are answered
        quiz_questions = quiz.questions.all()
        question_ids = {q.id for q in quiz_questions}
        submitted_question_ids = {answer['question_id'] for answer in submitted_answers}
        
        if question_ids != submitted_question_ids:
            return Response(
                {"error": "You must answer all questions in the quiz"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate score
        correct_answers = 0
        total_questions = len(quiz_questions)
        
        # Create a mapping of submitted answers
        submitted_answer_map = {
            answer['question_id']: answer['answer_id'] 
            for answer in submitted_answers
        }
        
        for question in quiz_questions:
            submitted_answer_id = submitted_answer_map.get(question.id)
            if submitted_answer_id and question.correct_answer_id == submitted_answer_id:
                correct_answers += 1
        
        # Calculate percentage score
        score = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Create and save the grade
        grade = Grade.objects.create(
            quiz=quiz,
            user=request.user,
            score=score
        )
        
        return Response({
            "score": score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "grade_id": grade.id,
            "message": f"Quiz completed! You scored {score}% ({correct_answers}/{total_questions})"
        }, status=status.HTTP_201_CREATED)

    def get(self, request, quiz_id):
        try:
            grade = Grade.objects.get(quiz=quiz_id, user=request.user)
        except Grade.DoesNotExist:
            return Response(
                {"error": "Grade not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(GradeSerializer(grade).data)