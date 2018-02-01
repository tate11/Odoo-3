# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'MMP Dossiês',
    'version': '10.0.333',
    'category': 'Customization',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Customização Melo, Martini & Parada ==
''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.thinkopensolution.com.br',
    'depends': [
                'board',
                'contacts', # to create contacts
                'mail',    # to send mails
                'l10n_br_base',  # cnpj e cpf de parceiros
                'l10n_br_data_base',  # lista de bancos
                ],
    'data': [
        'security/security.xml',
        'wizard/motivo_concluido_view.xml',
        'wizard/contraproposta_view.xml',
        'wizard/update_acordo_view.xml',
        'wizard/minuta_recebida_wizard_view.xml',
        'wizard/dossie_fila_wizard_view.xml',
        'data/mmp.pre.tppagamento.csv',
        'data/mmp.pre.phone.status.csv',
        'data/mmp.pre.phone.type.csv',
        'data/email_templates_view.xml',
        'data/update_situacao_acordo_scheduler_view.xml',
        'views/dossie_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/mail_template_view.xml',
        'views/res_partner_bank_view.xml',
        'views/dossie_cron.xml',
        'report/dossie_report_view.xml',
        'security/ir.model.access.csv',
    ],
    'init': [],
    'demo': [],
    'update_xml': [],
    'test': [],  # YAML files with tests
    'css': ['static/src/css/base.css', ],
    'installable': True,
    'application': True,
    'auto_install': False,  # If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
