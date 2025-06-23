from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet)
router.register(r"users", UserViewSet)
router.register(r"quiz-details", QuizDetailViewSet, basename="quiz-details")

urlpatterns = [
    path("", include(router.urls)),
    path("quizzes/<int:quiz_id>/submit/", QuizGradingView.as_view(), name="quiz-submit"),
]
