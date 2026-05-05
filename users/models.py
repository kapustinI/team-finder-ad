import io
import random
from pathlib import Path

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        extra_fields.setdefault("name", "Admin")
        extra_fields.setdefault("surname", "User")
        extra_fields.setdefault("phone", "+70000000000")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(
        max_length=12,
        blank=True,
        validators=[RegexValidator(r"^(8\d{10}|\+7\d{10})$", "Формат: 8XXXXXXXXXX или +7XXXXXXXXXX")],
    )
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        self.phone = self.normalize_phone(self.phone)
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and not self.avatar:
            self.avatar.save(self._default_avatar_name(), self._generate_avatar_file(), save=True)

    @staticmethod
    def normalize_phone(phone: str) -> str:
        if not phone:
            return ""
        if phone.startswith("8") and len(phone) == 11:
            return "+7" + phone[1:]
        return phone

    def _default_avatar_name(self) -> str:
        return f"avatars/user_{self.pk}.png"

    def _generate_avatar_file(self) -> ContentFile:
        width = 200
        height = 200
        bg_colors = [
            (58, 95, 145),
            (74, 122, 85),
            (127, 97, 163),
            (140, 98, 57),
            (73, 115, 122),
        ]
        img = Image.new("RGB", (width, height), color=random.choice(bg_colors))
        draw = ImageDraw.Draw(img)
        letter = (self.name[:1] or "U").upper()

        font = None
        font_size = 96
        font_candidates = [
            Path(settings.BASE_DIR) / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf",
            "arial.ttf",
        ]
        for candidate in font_candidates:
            try:
                font = ImageFont.truetype(str(candidate), font_size)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (width - text_w) / 2
        y = (height - text_h) / 2 - 8
        draw.text((x, y), letter, fill=(255, 255, 255), font=font)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return ContentFile(buf.getvalue())
