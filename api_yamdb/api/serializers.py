from django.core.validators import RegexValidator
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import ROLE_CHOICES, User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+',
            message='Используйте допустимые символы в username'
        )])
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if (
            User.objects.filter(email=email).exists()
            or User.objects.filter(username=username).exists()
        ):
            raise serializers.ValidationError(
                'А Вы точно зедсь первый раз?!'
                'Я точно помню, что такие username и/или email уже видел :)'
            )
        if username is not None and username.lower() == 'me':
            raise serializers.ValidationError(
                f'username {username} зарезервировано!'
            )
        return data


class MeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+',
            message='Используйте допустимые символы в username'
        )])
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        read_only=True)

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+',
            message='Используйте допустимые символы в username'
        )])
    email = serializers.EmailField(max_length=254)

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if not User.objects.filter(username=username, email=email).exists():
            if (
                User.objects.filter(email=email).exists()
                or User.objects.filter(username=username).exists()
            ):
                raise serializers.ValidationError(
                    'А Вы точно зедсь первый раз?!'
                    'Я точно помню, что такие username и/или email уже видел!'
                )
        if username is not None and username.lower() == 'me':
            raise serializers.ValidationError(
                f'username {username} зарезервировано!'
            )
        return data

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(
        max_length=150,
    )
    token = serializers.CharField(
        max_length=255,
        required=False,
        read_only=True
    )

    class Meta:
        fields = ('username', 'confirmation_code', 'token')
        model = User

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if username is None:
            raise serializers.ValidationError(
                'Необходимо ввести username'
            )
        if confirmation_code is None:
            raise serializers.ValidationError(
                'Необходимо ввести присланный confirmation code'
            )
        return data


class CategorySerializer(serializers.ModelSerializer):
    lookup_field = 'slug'

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    lookup_field = 'slug'

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategoryListField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return CategorySerializer(value).data


class GenreListField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return GenreSerializer(value).data


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreListField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    category = CategoryListField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    description = serializers.CharField(
        required=False,
    )
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True,
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_field_only = ('title',)

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                author=self.context['request'].user,
                title=self.context['view'].kwargs.get('title_id'),
            ).exists():
                raise serializers.ValidationError(
                    'Нельзя оставить повторный отзыв на одно произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = (
            'id',
            'author',
            'text',
            'pub_date',
        )
        model = Comment
        read_only_fields = ('review',)
