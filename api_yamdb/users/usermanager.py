from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, role, bio):
        if not username:
            raise ValueError('Необходимо ввести username')
        if not email:
            raise ValueError('Необходимо ввести email')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            role=role,
            bio=bio,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, role, bio):
        user = self.create_user(
            username,
            email,
            password=password,
            role=role,
            bio=bio,
        )
        user.is_admin = True
        user.role = 'superuser'
        user.save(using=self._db)
        return user
