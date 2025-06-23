from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

CHOICES = [
    (1, "Answer 1"),
    (2, "Answer 2"),
    (3, "Answer 3"),
    (4, "Answer 4"),
    (5, "Answer 5"),
]


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True, blank=False, related_name='quizzes')

    @property
    def avg_score(self):
        return 1

    class Meta:
        ordering = ["-created_at"]


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    answer_1 = models.CharField(max_length=200)
    answer_2 = models.CharField(max_length=200)
    answer_3 = models.CharField(max_length=200)
    answer_4 = models.CharField(max_length=200)
    answer_5 = models.CharField(max_length=200)
    correct_answer = models.IntegerField(blank=False, null=False, choices=CHOICES)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)


class Grade(models.Model):
    score = models.IntegerField(
        blank=False,
        null=False,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
