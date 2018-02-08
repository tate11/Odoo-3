# -*- coding: utf-8 -*-
##############################################################################
#
#    Ballotnet Solutions Ltd.
#    Copyright (C) 2017-TODAY Ballotnet Solutions Ltd (komolafetosin@gmail.com).
#    Author: Tosin Komolafe(<komolafetosin@gmail.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Lincer Dashboards',
    'summary': """Create your custom dashboards""",
    'version': '10.0.1.0.0',
    'description': """Lincer Dashboards""",
    'author': 'Tosin Komolafe',
    'company': 'Ballotnet Solutions Ltd',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'website': 'http://www.ballotnet.com',
    'depends': ['board'],
    'sequence': '1000',
    'data': [
        'security/ir.model.access.csv',

        'views/board_view.xml',
        'views/board_templates.xml'
    ],
    'qweb': ['static/src/xml/board.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
