# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Lincer Project',
    'summary': '',
    'description': 'Adds Lincer project structure.',
    'author': 'Lincer',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'https://lincersolucoes.com.br',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
                'tko_project_task_type',
    ],
    'external_dependencies': {
                                'python': [],
                                'bin': [],
                                },
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'test': [],
    'data': [
             'views/res_company_view.xml',
             'views/project_task_view.xml',
    ],
}
