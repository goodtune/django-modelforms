# django-modelforms

[![Codeship Status](https://codeship.com/projects/bb8fe870-b46c-0133-5bfb-2e1f5f4040fe/status?branch=master)](https://codeship.com/projects/133944)
[![Coverage Status](https://coveralls.io/repos/bitbucket/touchtechnology/django-modelforms/badge.svg?branch=master)](https://coveralls.io/bitbucket/touchtechnology/django-modelforms?branch=master)

This project came about because our reusable administration has to deal with
related models that have `unique_together` constraints that were not being
properly validated by the default implementation.

It occurs because our forms don't show the related field, it's not something we
want the user to be able to edit. This has the nasty side-effect of excluding
the related field from validation checks, so uniqueness (with respect to the
related field) is not tested.

The form therefore validates, and a database update is attempted - only to fail
when integrity constraints are enforced by the backend.

## Why?

Django bug [#13091](https://code.djangoproject.com/ticket/13091) was filed in
March 2010 and still has not been fixed.

There has been discussion on the mailing lists and a number of patches
proposed, but none have been accepted.

To stop encountering this in our projects we decided to write something generic
can easily be used without having to wait for an upstream fix, because that is
appearing less likely every day.
