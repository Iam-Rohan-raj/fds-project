from django import forms
from .models import URL


class URLForm(forms.ModelForm):
    original_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com/your-very-long-url-here',
            'class': 'url-input',
            'id': 'original-url-input',
            'autocomplete': 'off',
        }),
        label='Long URL',
    )
    custom_alias = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'my-custom-alias (optional)',
            'class': 'alias-input',
            'id': 'custom-alias-input',
        }),
        label='Custom Alias (optional)',
        max_length=50,
    )
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Give your link a name (optional)',
            'class': 'title-input',
            'id': 'title-input',
        }),
        label='Title (optional)',
        max_length=200,
    )
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'expires-input',
            'id': 'expires-at-input',
        }),
        label='Expiry Date/Time (optional)',
    )

    class Meta:
        model = URL
        fields = ['original_url', 'custom_alias', 'title', 'expires_at']

    def clean_custom_alias(self):
        alias = self.cleaned_data.get('custom_alias')
        if alias:
            alias = alias.strip().lower().replace(' ', '-')
            if URL.objects.filter(custom_alias=alias).exists():
                raise forms.ValidationError("This alias is already taken. Please choose another.")
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', alias):
                raise forms.ValidationError("Alias can only contain letters, numbers, hyphens, and underscores.")
        return alias
