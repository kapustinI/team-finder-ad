from django import forms

from team_finder.constants import ALLOWED_REPOSITORY_HOST


class GitHubURLValidationMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "")
        if url and ALLOWED_REPOSITORY_HOST not in url.lower():
            raise forms.ValidationError(
                f"Ссылка должна вести на {ALLOWED_REPOSITORY_HOST}"
            )
        return url
