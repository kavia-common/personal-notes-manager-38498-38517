from django.urls import path
from .views import (
    health,
    register,
    login,
    NoteListCreateView,
    NoteRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register', register, name='Register'),
    path('auth/login', login, name='Login'),
    path('notes/', NoteListCreateView.as_view(), name='NotesListCreate'),
    path('notes/<int:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='NotesDetail'),
]
