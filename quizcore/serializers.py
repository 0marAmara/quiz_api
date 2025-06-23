from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction

from .models import *


class UserSerializer(serializers.ModelSerializer):
    quizzes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "quizzes"]


class QuizListSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "owner"]


class Grade(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grade
        fields = ("id", "score")


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ("id", "answer_text")


class QuestionListSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    correct_answer_index = serializers.IntegerField(write_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "answers",
            "correct_answer_index",
        )


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionListSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ("id", "title", "description", "questions")

    def create(self, validated_data):

        questions_list = validated_data.pop("questions", [])

        with transaction.atomic():
            quiz = Quiz.objects.create(**validated_data)

            for question_data in questions_list:
                original_answers_list = question_data["answers"].copy()

                answers_list = question_data.pop("answers", [])

                correct_answer_index = question_data.pop("correct_answer_index", None)

                question = Question.objects.create(quiz=quiz, **question_data)

                answers = []

                for answer_data in answers_list:
                    answer = Answer.objects.create(question=question, **answer_data)
                    answers.append(answer)

                if correct_answer_index is None:
                    raise serializers.ValidationError(
                        "correct_answer_index is required for each question."
                    )

                if not (0 <= correct_answer_index < len(original_answers_list)):
                    raise serializers.ValidationError(
                        f"correct_answer_index {correct_answer_index} is out of range for question with {len(original_answers_list)} answers."
                    )

                correct_answer_text = original_answers_list[correct_answer_index][
                    "answer_text"
                ]

                correct_answer_object = Answer.objects.filter(
                    question=question, answer_text=correct_answer_text
                ).first()

                if not correct_answer_object:
                    raise serializers.ValidationError(
                        f"Could not find answer with text '{correct_answer_text}' for the question."
                    )

                question.correct_answer = correct_answer_object

                question.save()

        return quiz


class GradeListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grade
        fields = ("id", "score", "quiz", "user")
