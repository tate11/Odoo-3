# -*- coding: utf-8 -*-
# © 2017 LINCER <http://lincer.lincersolucoes.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Lincer MMP Galilai Cron',
    'summary': '',
    'description': '',
    'author': 'Tosin Komolafe',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'https://lincer.lincersolucoes.com.br',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'tko_mmp_project',
        'tko_galilai_api',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'init_xml': [],
    'data': ['views/mmp_galilai_cron_view.xml'],
    'css': [],
    'demo_xml': [],
    'test': [],

}
