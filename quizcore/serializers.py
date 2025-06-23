from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    quizzes = serializers.HyperlinkedRelatedField(
        many=True, view_name="quiz-detail", read_only=True
    )

    class Meta:
        model = User
        fields = ["id", "username", "quizzes"]


class QuizListSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "owner"]


class Grade(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grade
        fields = ("id", "score")


class QuestionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "quiz",
            "answer_1",
            "answer_2",
            "answer_3",
            "answer_4",
            "answer_5",
        )


class GradeListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grade
        fields = ("id", "score", "quiz", "user")
