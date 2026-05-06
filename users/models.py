import io
import random
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont
from team_finder.constants import (
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from users.constants import (
    AVATAR_BG_COLORS,
    AVATAR_DEFAULT_LETTER,
    AVATAR_FILE_FORMAT,
    AVATAR_FONT_FALLBACK,
    AVATAR_FONT_PATH,
    AVATAR_FONT_SIZE,
    AVATAR_HEIGHT,
    AVATAR_TEXT_ANCHOR,
    AVATAR_TEXT_COLOR,
    AVATAR_TEXT_Y_SHIFT,
    AVATAR_WIDTH,
    USER_PHONE_COUNTRY_PREFIX,
    USER_PHONE_DIGITS_COUNT,
    USER_PHONE_LOCAL_PREFIX,
)
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
        validators=[RegexValidator(r"^(8\d{10}|\+7\d{10})$", "Формат: 8XXXXXXXXXX или +7XXXXXXXXXX")],
    )
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True)
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
        if (
            phone.startswith(USER_PHONE_LOCAL_PREFIX)
            and len(phone) == USER_PHONE_DIGITS_COUNT
        ):
            return USER_PHONE_COUNTRY_PREFIX + phone[1:]
        return phone

    def _default_avatar_name(self) -> str:
        return f"avatars/user_{self.pk}.png"

    def _generate_avatar_file(self) -> ContentFile:
        img = Image.new(
            "RGB",
            (AVATAR_WIDTH, AVATAR_HEIGHT),
            color=random.choice(AVATAR_BG_COLORS),
        )
        draw = ImageDraw.Draw(img)
        letter = (self.name[:1] or AVATAR_DEFAULT_LETTER).upper()

        font = None
        font_candidates = [
            Path(settings.BASE_DIR) / AVATAR_FONT_PATH,
            AVATAR_FONT_FALLBACK,
        ]
        for candidate in font_candidates:
            try:
                font = ImageFont.truetype(str(candidate), AVATAR_FONT_SIZE)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()

        bbox = draw.textbbox(AVATAR_TEXT_ANCHOR, letter, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (AVATAR_WIDTH - text_w) / 2
        y = (AVATAR_HEIGHT - text_h) / 2 + AVATAR_TEXT_Y_SHIFT
        draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

        buf = io.BytesIO()
        img.save(buf, format=AVATAR_FILE_FORMAT)
        return ContentFile(buf.getvalue())
