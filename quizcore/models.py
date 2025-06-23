from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="quizzes",
    )

    @property
    def avg_score(self):
        return 1

    class Meta:
        ordering = ["-created_at"]


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    correct_answer = models.OneToOneField(
        "Answer",
        on_delete=models.CASCADE,
        related_name="correct_answer_for",
        null=True,
        blank=True,
    )


class Answer(models.Model):
    answer_text = models.CharField(max_length=200)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )


class Grade(models.Model):
    score = models.IntegerField(
        blank=False,
        null=False,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
