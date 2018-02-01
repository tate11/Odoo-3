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
    'name': 'Import from Excel files',
    'version': '0.100',
    'category': 'Customization',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Import Dossie from Excel Files ==
''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'depends': ['base',
                'tko_mmp_pre',
                ],
    'data': [
        'dossie_view.xml',
        'res_partner_view.xml',
        'import_excel_view.xml',
        'import_phone_numbers_view.xml',
        'security/ir.model.access.csv',
    ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': True,
    'auto_install': False,  # If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
