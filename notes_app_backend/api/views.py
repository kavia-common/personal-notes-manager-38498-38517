from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics, mixins, pagination
from rest_framework.authtoken.models import Token

from .serializers import NoteSerializer, RegisterSerializer, LoginSerializer
from .models import Note

User = get_user_model()


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})


class DefaultPagination(pagination.PageNumberPagination):
    """
    Default pagination: page size from query param 'page_size' with default 10, max 100.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# PUBLIC_INTERFACE
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.

    Request body:
    - username: string
    - password: string

    Returns:
    - id, username, token
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"id": user.id, "username": user.username, "token": token.key},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint that returns an auth token.

    Request body:
    - username
    - password

    Returns:
    - token
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
class NoteListCreateView(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         generics.GenericAPIView):
    """
    List and create notes for the authenticated user.

    - GET: returns paginated list of the user's notes ordered by updated_at desc.
    - POST: creates a new note for the user.

    Query params for GET:
    - page: page number
    - page_size: items per page
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user).order_by("-updated_at")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# PUBLIC_INTERFACE
class NoteRetrieveUpdateDestroyView(mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    generics.GenericAPIView):
    """
    Retrieve, update, or delete a note belonging to the authenticated user.

    Path params:
    - pk: note id
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, partial=False, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
