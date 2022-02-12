# Tags (coming soon)

## Model

The very last feature that we need to implement is tags.

First, we create the `Tag` object itself.

In `articles/models.py`:

``` { .python }
# ...
class Tag(models.Model):
    tag = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.tag
```

The `tag` field will contain the tag itself, while `slug` is just a way
for us to retrieve it more easily.

Now, we need a way to assign tags to an article: we can achieve this by
wadding a `ForeignKey` to the `Article` model. In `articles/models.py`:

``` { .python }
# ...
from django.utils.text import slugify

# ...
class Article(models.Model):
    # ...
    tags = models.ManyToManyField("articles.Tag", related_name= "articles", blank=True)

    def add_tag(self, tag):
        slug = slugify(tag)
        tag_object, created = Tag.objects.get_or_create(tag=tag, slug=slug)
        self.tags.add(tag_object)

    def remove_tag(self, tag):
        tag_object = Tag.objects.get(tag=tag)
        self.tags.remove(tag_object)

    # ...
```

We have modified the models: we need to `makemigrations` and `migrate`.

## Views

We will now enable users to specify the tags for their article in the
editor.

We want to be able to add and remove tags straight in the editor, like
in the following video:

[./assets/editor - tags.mp4](./assets/editor - tags.mp4)

The thing is, we can't do that in Django only: in order to have actions
triggered by the Enter button, we would need to write JavaScript, which
we're trying not to do in this tutorial.

Add tags to an article through CLI.

We need new form: create `articles/forms.py` to add new_tag field.

Add to `articles/views.py` in `EditorUpdateView`.

In `templates/editor.html`, expose tag template.

``` { .html hl_lines="11" }
<!-- ... -->
<fieldset class="form-group">
  <textarea
    class="form-control"
    rows="8"
    placeholder="Write your article (in markdown)"
    name="{{ form.body.name }}"
  >{{ form.body.value|default_if_none:'' }}</textarea>
</fieldset>
{{ form.body.errors }}
{% include 'article_tag.html' with article_slug=article.slug %} <!-- new -->
<button class="btn btn-lg pull-xs-right btn-primary">
  Publish Article
</button>
<!-- ... -->
```

We'll have to do a bit of a hack here, to achieve this kind of
functionality: we'll include a separate form for tags into the editor
form, and this form will update the page whenever a tag is added or
removed.

In `templates/article_tag.html`, expose new field and existing tags.

Create new buttons in `templates/article_tag.html`.

Override `post` in `EditorUpdateView` in `articles/views.py`.

Make tag field readonly and button disabled based on `request.path` in
`templates/article_tag.html`.

