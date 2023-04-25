from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import IsAdmin, IsModerator, IsSuperuser, IsUser, ReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    MeSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer
)


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdmin | IsSuperuser,)

    @action(url_path='me', methods=['get', 'patch'], detail=False,
            permission_classes=(IsUser,))
    def me(self, request):
        serializer_class = MeSerializer
        if request.method == 'GET':
            serializer = serializer_class(request._user, many=False)
            return Response(serializer.data)

        if request.method == 'PATCH':
            user = User.objects.get(username=request._user)
            serializer = serializer_class(
                user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class SignUp(APIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            username=request.data.get('username'),
            email=request.data.get('email')
        )

        user.save()

        send_mail(
            'Confirmation code from YaMDB',
            default_token_generator.make_token(user),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        if created:
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_200_OK)


class TokenView(APIView):
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not User.objects.filter(username=username).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(username=username)
        if default_token_generator.check_token(user, confirmation_code):
            return Response(
                {
                    'token': user.token
                },
                status=status.HTTP_201_CREATED
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PostDeleteListViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoriesViewSet(PostDeleteListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin | ReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'


class GenresViewSet(PostDeleteListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdmin | ReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    )
    serializer_class = TitleSerializer
    permission_classes = (IsAdmin | ReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        ReadOnly
        | IsSuperuser
        | IsAdmin
        | IsModerator
        | IsUser,
    )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        ReadOnly
        | IsSuperuser
        | IsAdmin
        | IsModerator
        | IsUser,
    )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
