# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Lincer Filter Option Date & Datetime',
    'summary': 'Lincer Filter Option Date & Datetime',
    'version': '10.0.0',
    'category': 'Lincer',
    'description': """
Filter Option Date & Datetime.
==============================
""",
    'author': 'Lincer',
    'website': 'https://lincer.lincersolucoes.com.br/',
    'license': 'AGPL-3',
    'depends': [
        'web',
    ],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/base.xml',
    ],
    'installable': True,
    'active': True,
    'application': True,
}
