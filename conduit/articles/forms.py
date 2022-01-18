from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    new_tag = forms.CharField(required=False)

    class Meta:
        model = Article
        fields = ["title", "description", "body", "new_tag"]

    # def save(self, commit=True):
    #     article = super().save(commit=False)
    #     new_tag = self.cleaned_data.get("new_tag")
    #     if new_tag:
    #         article.add_tag(new_tag)
    #     article.save()
    #     return article
