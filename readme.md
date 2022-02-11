# Readme

## Introduction

We'll build the [Thinkster's RealWorld Example
App](https://github.com/gothinkster/realworld/) from the ground up. The
app is called Conduit and is a Medium clone: you can see it running at
<https://demo.realworld.io>.

<figure>
<img src="../assets/Conduit - RealWorld.png" width="600" alt="The RealWorld app, in all its glory" /><figcaption aria-hidden="true">The RealWorld app, in all its glory</figcaption>
</figure>

Instead of building the backend in Django and doing the frontend with a
JavaScript framework (like React or Vue), we'll do both frontend and
backend in Django (with some help from HTMX), to show that server-side
rendering is still going strong.

## Pre-requisites

-   [DjangoGirls tutorial](https://github.com/DjangoGirls/tutorial)

    You should have followed the [DjangoGirls
    tutorial](https://github.com/DjangoGirls/tutorial) before starting
    this one: it is great for getting you up to speed, and covers most
    of the introductory material you'll need, like HTML, CSS, and, of
    course, Django. We'll assume you have completed that tutorial and
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

## What we'll be doing

First, we'll decide on a project and folder structure, to keep the
project's complexity in check. We will then do the groundwork required
by Django before we can get our app running online.

We'll then dive into the tutorial proper: we'll make our first models,
views, templates. We'll also create some articles through the Django
admin app to have something nice to look at.

We'll then spend some time on implementing features for viewing,
creating, editing, and deleting articles.

We'll do the same for comments.

After that, we'll spend a while on authentication and profile features
(which includes follows, favorites, and tags).

Finally, we'll implement HTMX.

