# -*- coding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Lincer External File Location',
    'summary': '',
    'description': 'Lincer External File Location',
    'author': 'Tosin Komolafe',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'https://lincer.lincersolucoes.com.br/',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['fs', 'paramiko',],
        'bin': [],
    },
    'init_xml': [],
    'depends': ['base','tko_mmp_project'],
    'data': [
        'views/menu.xml',
        'views/attachment_view.xml',
        'views/location_view.xml',
        'views/task_view.xml',
        'views/config_view.xml',
        'security/ir.model.access.csv'
    ],
    'css': [],
    'demo_xml': [],
    'test': [],
}
