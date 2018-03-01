# -*-coding:utf-8-*-

from odoo import models, fields, api
from operator import itemgetter
from textwrap import dedent


class Board(models.AbstractModel):
    _inherit = 'board.board'

    @api.model
    def list(self):
        Actions = self.env['ir.actions.act_window']
        Menus = self.env['ir.ui.menu']
        IrValues = self.env['ir.values']

        act_ids = Actions.search([('res_model', '=', self._name)])
        refs = ['%s,%s' % (Actions._name, act_id.id) for act_id in act_ids]

        # cannot search "action" field on menu (non stored function field without search_fnct)
        irv_ids = IrValues.search([
            ('model', '=', 'ir.ui.menu'),
            ('key', '=', 'action'),
            ('key2', '=', 'tree_but_open'),
            ('value', 'in', refs),
        ])
        menu_ids = map(itemgetter('res_id'),
                       IrValues.read(irv_ids.ids, ['res_id']))
        menu_names = Menus.name_get(menu_ids)
        return [dict(id=m[0], name=m[1]) for m in menu_names]


class BoardCreate(models.Model):
    _name = 'board.create'
    _description = 'Board Creation'

    def _default_menu_parent_id(self):
        ir_model_obj = self.env['ir.model.data']
        model, menu_id = ir_model_obj.get_object_reference(
            'base', 'menu_board_root')
        return menu_id

    name = fields.Char('Board Name', size=64, required=True)
    menu_parent_id = fields.Many2one(
        'ir.ui.menu', u'Parent Menu', required=True, default=_default_menu_parent_id)

    def board_create(self):
        this = self.browse(self.id)

        view_arch = dedent("""<?xml version="1.0" encoding="utf-8"?>
            <form string="%s">
            <board style="2-1">
                <column/>
                <column/>
            </board>
            </form>
        """.strip() % (this.name,))

        view_obj = self.env['ir.ui.view']
        view = view_obj.create({
            'name': this.name,
            'model': 'board.board',
            'priority': 16,
            'type': 'form',
            'arch': view_arch,
        })

        act_window_obj = self.env['ir.actions.act_window']
        action = act_window_obj.create({
            'name': this.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'board.board',
            'usage': 'menu',
            'view_id': view.id,
            'help': dedent('''<div class="oe_empty_custom_dashboard">
              <p>
                <b>This dashboard is empty.</b>
              </p><p>
                To add the first report into this dashboard, go to any
                menu, switch to list or graph view, and click <i>'Add to
                Dashboard'</i> in the extended search options.
              </p><p>
                You can filter and group data before inserting into the
                dashboard using the search options.
              </p>
          </div>
            ''')
        })

        menu_obj = self.env['ir.ui.menu']
        menu = menu_obj.create({
            'name': this.name,
            'parent_id': this.menu_parent_id.id,
            'action': 'ir.actions.act_window,%s' % (action.id,)
        })

        board_obj = self.env['board.board']
        board_obj.clear_caches()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }
