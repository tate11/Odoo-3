# -*- coding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MMP Project',
    'summary': '',
    'description': 'Add dossie in Project and dynamic fields in Task',
    'author': 'TKO',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'contacts',
        'account',
        'br_base',
        'tko_project_task_type',
        'tko_project_task_actions_assign',
        'tko_base_server_action',
        'tko_partner_multiple_addresses',
        'tko_partner_multiple_phones',
        'tko_partner_multiple_emails',
        'tko_partner_multiple_assets',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'init_xml': [],
    'data': [
        'views/dossie_view.xml',
        'views/project_task_view.xml',
        'views/import_dossie_excel_view.xml',
        #'views/ir_attachment_view.xml',
        'views/res_partner_view.xml',
        'views/task_action_view.xml',
        'views/dossie_cron_view.xml',
    ],
    'css': [],
    'demo_xml': [],
    'test': [],

}
