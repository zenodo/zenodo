Project Life Cycle
==================

Zenodo development is planned 3-6 months in advance using 3-months road map. The 3-months road map is divided into 14-days sprints, where each sprint is planned at the beginning of the sprint cycle. After each sprint new features are deployed to our quality assurance cluster for one week, after which they are deployed to our production cluster. Tasks are assigned to the sprint in order to deliver the 3-months road map as well as solve support requests and/or operational issues.

Triaging process
----------------
**Milestones and task board**

GitHub `milestones <https://github.com/zenodo/zenodo/milestones>`_ are used for
planning both 3-months road maps and sprints.

`HuBoard <https://huboard.com/zenodo/zenodo>`_ is used as agile task board overlay on top of
GitHub issues.

**Labels**

Below labels are managed through HuBoard and used for the task board:

 * ``0 - Backlog``: Backlog
 * ``1 - Todo``: Issue assigned to a sprint and properly defined.
 * ``2 - In progress``: Issue is being worked on (must be assigned to a person as well).
 * ``3 - Done``: Issue is done.

Below labels are managed through either GitHub or HuBoard:

 * ``bug``: Defect in the service.
 * ``enhancement``: Enhancement/new feature.
 * ``road map``: High-level tasks used for road map planning.
 * ``i - Support``: Related to a support request.
 * ``i - ...``: Related to a particular partner.

Priority/urgency is purposely not defined as a label.

**New issues**

New issues should by default be assigned to ``0 - Backlog`` as well as ``bug``, ``enhancement`` or ``road map``.

Sprint cycles
~~~~~~~~~~~~~
The beginning of each sprint cycle roughly follows the following pattern:

* Previous sprint close-out
    - Integrate `pending pull-requests <https://github.com/zenodo/zenodo/pulls>`_ (or postpone to next sprint).
    - Verify and close issues labeled ``3 - Done``.
    - Move open milestone issues to backlog (``1 - Todo`` -> ``0 - Backlog``).
    - Close milestone (progress should be 100%).
* Requirements update
    - Update Python package requirements. Needed in order to ensure security fixes from packages are integrated (see :ref:`updateing_requirements`).
* Sprint planning
    - Create new milestone and assign end-date.
    - Assign issues to milestone (see below).
    - Assign issues to developer.
    - Assign ``1- Todo`` label to issues.

Checklist for assigning issues:

- Clear goal/no missing information?
- Specific enough to make an effort estimate?
- Good mix of bugs/enhancements?
- Can task be made in way that it can be merged in master


Release process
---------------
Zenodo is released (i.e. deployed) often and early to ensure high speed in delivering new features/bug fixes. To maintain high quality during the process, all code go through a quality assurance process. The deployment QA described below is only the last part of the QA process. Please see the section :ref:`development_process` for the QA process during development.

* **Regular deployment**: By default Zenodo is regularly deployed on Mondays after each sprint close-out (i.e. minimum every 2 weeks). Depending on stability and feature matureness in the master branch, deployment may happen every week (on Mondays to ensure staff is present to fix urgent problems).
* **Hotfix deployment**: Emergency fixes to the code base may deployed immediately after all CI tests passes. Hotfixes should be made directly on the ``production`` or ``qa`` branch depending on urgency.

Quality assurance
~~~~~~~~~~~~~~~~~
A reliable and rock solid service is a highly important business objective for Zenodo. All new features therefore go through a 1-week quality assurance process, where they are merged from the ``master``-branch  to the ``qa``-branch and afterwards deployed to our quality assurance cluster (which matches our production environment). This merge is depend on that the ``master``-branch is in a mature state after each sprint cycle (the sprint planning plays an important role in this respect).

During the 1-week QA review, each closed sprint issue is tested and reviewed on the QA environment. Also, core Zenodo features must be tested for regressions. If any problem is discovered, a hotfix deployment is made to the quality assurance cluster. If a larger problem are detected, the regular release process may be stopped. This should be considered an emergency stop, and all efforts directed towards addressing the issue. It is critical to maintain the development branch in a deployable state to enable high speed development and release process.

If no problems are detected during the 1-week QA review, the ``qa``-branch is merged to ``production``-branch and deployed to the production cluster.

All in all a new feature roughly go through the following process:

- Week 1-2:
    - Sprint planning
    - Package upgrades.
    - Feature development and maturing through ``master``.
- Week 3 (on Monday):
    - Sprint close-out
    - Merge ``master`` to ``qa``.
    - Deploy ``qa`` to QA cluster.
    - Test plan (prepare list of new features from closed sprint milestone)
    - Communication plan (prepare e.g. Twitter message to be send after production deployment).
    - Start next sprint.
- Week 4 (on Monday):
    - Merge ``qa`` to ``production``.
    - Deploy ``production`` to production cluster.
    - Rerun test plan.
    - Run communication plan.

Note that, sprints and the release process run in parallel.
