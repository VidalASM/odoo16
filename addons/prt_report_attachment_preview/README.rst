===============================================
Open PDF Reports and PDF Attachments in Browser
===============================================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:c4169285f0b1ee7c950144d61c89511a07ea85761589abc4904db4ac015b51b1
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-cetmix%2Fcetmix--tools-lightgray.png?logo=github
    :target: https://github.com/cetmix/cetmix-tools/tree/16.0/prt_report_attachment_preview
    :alt: cetmix/cetmix-tools

|badge1| |badge2| |badge3|

By default Odoo downloads PDF reports. This module opens PDF reports in a new browser tab instead of downloading.

**Table of contents**

.. contents::
   :local:

Changelog
=========

16.0.1.0.7 (2024-05-13)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- Add same behavior as in standard Odoo report handlers: when close_on_report_download key is passed into an action object - do 'act_window_close' action after opening report preview (3603)


16.0.1.0.6 (2024-01-30)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Report name encoding error for some hieroglyphical languages (`#3233 <https://github.com/cetmix/cetmix-tools/issues/3233>`_)


16.0.1.0.5 (2024-01-08)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Created workaround to avoid exceptions caused by empty evaluation context keys (`#3179 <https://github.com/cetmix/cetmix-tools/issues/3179>`_)


16.0.1.0.2
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] product labels are not printed
* [FIX] OM accounting reports are not printed


16.0.1.0.1
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] multi-company issue


16.0.1.0.0
~~~~~~~~~~~~~~~~~~~~~~~

* Release for Odoo 16

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/cetmix/cetmix-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/cetmix/cetmix-tools/issues/new?body=module:%20prt_report_attachment_preview%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Ivan Sokolov
* Cetmix

Maintainers
~~~~~~~~~~~

This module is part of the `cetmix/cetmix-tools <https://github.com/cetmix/cetmix-tools/tree/16.0/prt_report_attachment_preview>`_ project on GitHub.

You are welcome to contribute.
