# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Studio Backend Theme v10',
    'category': 'Themes/Backend',
    'version': '1.0',
	'author': 'UNIBRAVO',
    'description':
        """
Professional Backend User Interface Web Client for Odoo.
===============================================
This Amazing backend theme module modifies the Odoo Backend User Interface to provide Professional design and responsiveness.
        """,
    'depends': ['web'],
	'images':['images/studio_theme_page.png', 'images/main_screenshot.png'],
	'application': False,
    'auto_install': False,
	'installable': True,
    'data': [
        'views/webclient.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'license': 'OPL-1',
	'price': 110,
	'currency': 'EUR',
	'live_test_url': 'http://31.192.213.202:8010/web?db=odoo10c_studio',
}
