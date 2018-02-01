# -*- coding: utf-8 -*-
# © 2017 LINCER <http://lincer.lincersolucoes.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MMP Juridical',
    'summary': '',
    'description': 'Add dynamic fields in Task',
    'author': 'Lincer',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'https://lincer.lincersolucoes.com.br',
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
    'data': ['views/project_task_view.xml', 
             'views/contestacao_priority_config_view.xml',
             'views/project_task_default_view.xml'],
    'css': [],
    'demo_xml': [],
    'test': [],

}
