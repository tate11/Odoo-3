# -*-coding:utf-8-*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_correspondente = fields.Boolean(u'Correspondente')
    is_grupo = fields.Boolean(u'Grupo')
    is_advogado = fields.Boolean(u'Advogado')
    is_parte_contraria = fields.Boolean(u'Parte Contrária')
    is_parte_representada = fields.Boolean(u'Parte Representada')
    is_escritorio = fields.Boolean(u'Escritório')
    is_credenciado = fields.Boolean(u'Credenciado')
    is_contumaz = fields.Boolean(u'Contumaz')
    is_agressor = fields.Boolean(u'Agressor')
    is_juiz = fields.Boolean(u'Juiz')
    is_cessionaria = fields.Boolean(u'Cessionária')
    oab = fields.Char(u'OAB')
    estado_ids = fields.Many2many('res.country.state','res_partner_estado_rel','partner_id','state_id' ,string="Estados")
    comarca_ids =  fields.Many2many('res.state.city', 'res_partner_comarca_rel', 'partner_id', 'city_id', string="Comarcas")
    valid_comarca_ids =  fields.Many2many('res.state.city', 'res_partner_valid_comarca_rel', 'partner_id', 'city_id', string="Comarcas")
    historico_ids = fields.Many2many('dossie.dossie','partner_dossie_historico_rel','partner_id','dossie_id',string=u'Histórico',compute='get_dossie_historico')

    @api.one
    def get_dossie_historico(self):
        # get dossie from parte_contraria_ids ==> dossie_parte_contraria_rel
        query = "select dossie_id from dossie_parte_contraria_rel where parte_id = %s"%self.id
        self.env.cr.execute(query)
        contrarias  = self.env.cr.fetchall()

        # get dossie from advogado_adverso_ids ==> dossie_advogado_rel
        query = "select dossie_id from dossie_advogado_rel where advogado_id = %s" % self.id
        self.env.cr.execute(query)
        advogados = self.env.cr.fetchall()
        partners = advogados + contrarias
        partner_list = [part[0] for part in partners]
        #set partners in Historico Tab
        self.historico_ids = partner_list

    @api.multi
    def name_get(self):
        res = []
        for part in self:
            name = part.name
            if part.is_parte_contraria or part.is_parte_representada:
                if part.cnpj_cpf:
                    name = name + ', %s' %part.cnpj_cpf
            if part.is_advogado and part.oab:
                name = name + ', %s' % part.oab
            res.append((part.id, name))
        return res

    # Search partners with Name, CNPJ/CPF and OAB
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search(['|','|',('name', operator, name),('cnpj_cpf', operator, name),('oab',operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.onchange('estado_ids','comarca_ids')
    def onchange_estado_comarca(self):
        result = {'value' : {}}
        all_states = self.estado_ids.ids
        used_states = self.comarca_ids.mapped(lambda p: p.state_id).ids
        non_used_states = list(set(all_states) - set(used_states))
        implicit_cites = self.env['res.state.city'].search([('state_id','in',non_used_states)])
        all_cities = implicit_cites + self.comarca_ids
        result['value']['valid_comarca_ids'] = [(6, 0, all_cities.ids)]
        return result


class ResStateCountry(models.Model):
    _inherit = 'res.state.city'

    is_capital = fields.Boolean('É Capital', default=False)

    @api.multi
    @api.constrains('is_capital', 'state_id')
    def check_state_is_capital(self):
        for city in self:
            city_ids = self.search([
                    ('state_id', '=', city.state_id.id),
                    ('is_capital', '=', True),
                    ])
            if len(city_ids) > 1 :
                raise ValidationError(_(
                    "Só pode existir uma capital por estado!"))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        recs = self.search(args, limit=limit)
        if self._context.has_key('estado_ids'):
            if self._context.get('estado_ids'):
                args.append(['state_id','in', self._context.get('estado_ids')[0][2]])
            else:
                args.append(['state_id','in', []])
            recs = self.search(args, limit=limit)
        return recs.name_get()
