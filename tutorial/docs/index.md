# Readme

!!! Warning

    I'm rewriting this tutorial in depth, to improve the structure, the explanations, the code, and implement the "Coming soon" sections.
    
## Introduction

In this tutorial, we'll be building the [Thinkster's RealWorld Example App](https://github.com/gothinkster/realworld/) *from the ground up*.

The app is called *Conduit* and is a Medium clone: you can see it running at <https://demo.realworld.io>.

<figure width="600">
<img src="../assets/Conduit - RealWorld.png" />
<figcaption>The RealWorld app, in all its glory</figcaption>
</figure>

The common way to approach this would be to build the backend in Django, do the frontend with a JavaScript framework (React, Vue, Svelte, etc.) and glue everything together with an API (Flask, Django REST Framework, etc.).

Thanks to frameworks like HTMX and AlpineJS, the common way described above is getting closer and closer towards becoming an exercise in overengineering. We can built our whole app in Django, both the backend and the frontend, with some help from HTMX and AlpineJS, so we'll do just that, and along the way we'll show that server-side rendering is going strong.

## What to expect from this tutorial

This tutorial documents my own path to learning Django. I hope it will contribute to closing the gap in the learning materials available to “medium to advanced beginners”: those who have built every fake blog in existence, but who don't don't benefit from more in-depth resources because they don't have a real codebase to work on.

We are aiming to build a tutorial that will teach the user to debug Django, to read the docs, to implement features that are not built-in.

We will be bumping into errors, reading error messages, and sometimes even using actual debuggers to fix our app. We'll be jumping in and out of the shell to see how the internals function. Whenever we need to implement a feature, we'll take the path that teaches us Django (but also show the alternative that simply solves the specific problem).

Hopefully this will provide you (and us) with a good grasp of Django.

## Pre-requisites

- Tools
  - Python 3.9
  - Django 5.0 (the tutorial should work fine in Django 3.2 however)
  - [HTMX](https://htmx.org/)
  - [AlpineJS](https://alpinejs.dev/)
  - Strongly recommended
    - [conda](https://docs.conda.io/en/latest/miniconda.html) or [virtualenv](https://virtualenv.pypa.io/) for making virtual environments
    - [git](https://github.com/git-guides/install-git), to keep track of your work We assume that you know the basics of git. You should `git commit` at the end of every chapter.
    - [ipython](https://github.com/ipython/ipython), to have an interactive shell
  - Optional
    - [faker](https://github.com/joke2k/faker), to avoid creating placeholder users, articles and comments, manually
    - [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar) and [pudb](https://github.com/inducer/pudb) to help debug our web app
- Knowledge
  - [DjangoGirls tutorial](https://github.com/DjangoGirls/tutorial) You should have followed the [DjangoGirls tutorial](https://github.com/DjangoGirls/tutorial) before starting this one: it is great for getting you up to speed, and covers most of the introductory material you'll need, like HTML, CSS, and, of course, Django. We'll assume you have completed that tutorial and won't go into the specifics of anything that has already been covered there.

## What we'll be doing

1.  First, we'll decide on a project and folder structure, to keep the project's complexity in check. We'll also do the groundwork required by Django before we can get our app running online.
2.  We'll then dive into the tutorial proper: we'll make our first models, views, templates. We'll also create some articles through the Django admin app to have something nice to look at.
3.  Next, we'll spend some time on implementing features for viewing, creating, editing, and deleting articles.
4.  We'll then implement the same things for comments.
5.  After that, we'll spend a while on authentication and profile features (which includes follows, favorites, and tags). At this point, our app will be as finished as can be with Django alone.
6.  Finally, we'll implement HTMX and AlpineJS to make our app indistinguishable from a traditional SPA.

## Why no REST?

Because our entire frontend is integrated into Django (through HTML templates and HTMX), and given the scope of tutorial, we can implement the whole app without building a REST API. So we won't. This has a few benefits:

- we keep the structure of the app simple
- we keep the mental load light: no need to understand how Django REST Framework (the preferred way of implementing REST APIs in Django) works, no need to juggle with serializers, routers, renderers, etc., no need to complicate the codebase
- because we don't use a REST API, we don't need to implement JWT authentication, which is a general pain: we can just rely on Django's built-in authentication solutions, which are robust and simple to implement.

The cons of this decision are that we won't be able to learn what there is to learn about building REST APIs with Django, which is a major use case for the framework: maybe a future version of this tutorial will include a chapter on this (but for now we want to let HTMX and AlpineJS shine).

## Thanks

Thanks to the [Django project](https://www.djangoproject.com/). Does this even need to be said? But seriously, thank you Django for existing.

Thanks to [HTMX](https://htmx.org/) and [AlpineJS](https://alpinejs.dev/) for the SSR revolution.

Thanks to the [Realworld team](https://github.com/gothinkster/realworld/) for having been the catalyst for so many projects.

Thanks to the [Svelte](https://svelte.dev/) community: throughout this tutorial, for anything that has to do with templates, we're simply adapting the templates from the [Svelte implementation](https://github.com/sveltejs/realworld) of the Realworld app's frontend. Svelte and the Django templating language are so similar that “adapting” the code mostly meant copying it.

Thanks to the [Django docs](https://docs.djangoproject.com/en/5.0/), universally praised as some of the best documentation in existence.

Thanks to the excellent [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x) by Daniel and Audrey Feldroy: highly recommended if you want to be exposed to best practice in Django.

