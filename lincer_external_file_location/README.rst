.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Attachment Metadata
====================

This module extend ir.attachment model with some new fields for a better control
for import and export of files.

The main feature is an integrity file check with a hash.

A file hash is short representation (signature) computed from file data.
Hashes computed before send file and after received file can be compared to be
sure of the content integrity.


Usage
=====

Go the menu Settings > Technical > Database Structure > Attachments

You can create / see standard attachments with additional fields



.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0


Known issues / Roadmap
======================

The purpose of this module is not to import the data of the file but only exchange files with external application.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.


Contributors
------------

* Tosin Komolafe <komolafetosin@gmail.com>
* Carlos Aguda <carlosaguda@gmail.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
