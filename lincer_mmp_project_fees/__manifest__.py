# -*- coding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MMP Project Fees',
    'summary': '',
    'description': 'Add Legal Fees Control',
    'author': 'Lincer',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'http://lincer.lincer.com.br',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'tko_mmp_project',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'init_xml': [],
    'data': [
        'views/dossie_view.xml',
        'security/project_security.xml',
    ],
    'css': [],
    'demo_xml': [],
    'test': [],
}
