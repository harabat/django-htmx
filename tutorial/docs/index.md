# Django tutorial Readme

## Introduction

We'll build the [Thinkster's Django RealWorld Example
App](https://github.com/gothinkster/django-realworld-example-app.git)
from the ground up. The app is called Conduit and is a Medium clone.

Instead of only building the backend in Django, we'll do both frontend
and backend, to show that SSR is still going strong.

We'll be following a simplified version of the
[cookiecutter/cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django/)
architecture (made famous by the excellent book [Two Scoops of Django
3.x](https://www.feldroy.com/books/two-scoops-of-django-3-x)), but you
don't need to have read it to follow.

## Pre-requisites

-   [DjangoGirls tutorial](https://github.com/DjangoGirls/tutorial)

    You should have followed the [DjangoGirls
    tutorial](https://github.com/DjangoGirls/tutorial) before starting
    this one: it is excellent for getting you up to speed, and covers
    most of the introductory material you'll need, like HTML, CSS, and,
    of course, Django. We'll assume you have completed that tutorial and
    won't go into the specifics of anything that has already been
    covered there.

-   Python 3.9

-   Django 3.2 (or higher)

-   [conda](https://docs.conda.io/en/latest/miniconda.html) or
    [virtualenv](https://virtualenv.pypa.io/) for virtual environments

-   Optional

    -   [git](https://github.com/git-guides/install-git), to keep track
        of your work

        We assume that you know the basics of git. You should
        `git commit` at the end of every chapter.

    -   [faker](https://github.com/joke2k/faker), to avoid creating fake
        users, articles, etc. manually

## Virtual environment

Let's start this tutorial in earnest.

Before doing anything else, we need to create our virtual environment.

We're working with `conda`
([tutorial](https://docs.conda.io/en/latest/miniconda.html)), but you
can work with `virtualenv`
([tutorial](https://realpython.com/python-virtual-environments-a-primer/)).

``` shell
conda create --name django
conda activate django
conda install django
```

Now, you have a virtual environment with `django` installed.

## What we'll be doing

