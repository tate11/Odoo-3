# © 2017 Lincer <http://lincer.lincersolucoes.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Module List Updater',
    'summary': '',
    'description': 'Allows to update module list from terminal',
    'author': 'Lincer',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'website': 'http://lincer.lincersolucoes.com.br',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
                'base',
    ],
    'external_dependencies': {
                                'python': [],
                                'bin': [],
                                },
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'data': [
             'views/module_view.xml',
    ],
}
