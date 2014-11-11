Contributing
============

Reporting issues
----------------
Please report all issues to our help desk by sending an email to
info@zenodo.org.

Developers should report issues via either our issue tracking system on
https://its.cern.ch/jira/ or directly to Invenio on http://github.com/inveniosoftware/invenio/issues depending on the nature of the issue.

.. _branches:

Branches
--------
Zenodo has three active branches:

* ``master`` - Default development branch (https://github.com/zenodo/zenodo/tree/master).
* ``qa`` - Quality assurance branch (https://github.com/zenodo/zenodo/tree/qa).
* ``production`` - Production branch (https://github.com/zenodo/zenodo/tree/production).

Zenodo depends on specific versions of Invenio, which are managed using
an Invenio fork located at https://github.com/zenodo/invenio. The Invenio fork has
three branches:

* ``pu-zenodo`` -- Default development branch that works with Zenodo ``master`` branch (https://github.com/zenodo/invenio/tree/master).
* ``qa`` -- Quality assurance branch that works with Zenodo ``qa`` branch (https://github.com/zenodo/invenio/tree/qa).
* ``production`` -- Production branch that works with Zenodo ``production`` branch (https://github.com/zenodo/invenio/tree/production).

The main purpose of the Invenio fork is to 1) manage which specific version of Invenio that Zenodo works with, and 2) allow for applying hot and quick fixes prior to their integration in upstream Invenio. Deviations from upstream must be kept at a bare minimum to make rebasing to latest upstream Invenio as easy as possible and prevent the fork from diverging.

.. note::
    Our Invenio fork is regularly rebased to the latest Invenio development version, thus be careful when fetching updates to not overwrite your own changes.

Tags
~~~~
Zenodo only uses tags to mark major changes in the code base. In particular releases are not tagged since they are managed through branches. Currently the following tags exists:

* ``legacy-20140305`` -- Zenodo prior to being rebased to Invenio's new module
  system (5 March 2014).
* ``legacy-20130508`` -- The OpenAIRE Orphan Record Repository prior to getting
  a make-over and being transformed into Zenodo (8 March 2013, which is also
  the Zenodo launch date).

Development process
-------------------
STUB

Release process
---------------
Zenodo is released (i.e. deployed) often and early to prevent "big splahes".
Features flow through the the following branches (in order):

* ``feature-X`` -- Branches for development of a new features.
* ``master`` (or ``pu-zenodo`` for Invenio). -- Main development branch in which features are matured. A self-contained feature may be integrated in the main development branch, but "switched off" in case it needs further work.
* ``qa`` -- The quality assurance branch is deployed on our quality assurance cluster which matches our production cluster in order to detect deployment and integration issues. Code from ``master`` is not merge into QA until its fully mature and ready to be deployed.
* ``production`` -- If all quality assurance tests passed, the code is merged to production and deployed on our production cluster.

Exceptions:

* Hot fixes: Emergency fixes to the code base may be merged directly to ``qa``, in which case they will be merge into master afterwards.

Schedule
~~~~~~~~
Currently there are no well-defined release schedule, but we may likely go with time-based released between 1-2 weeks in the future.
