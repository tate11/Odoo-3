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

import base64
import datetime
import logging
import re
import time
from string import capwords
from xlrd import open_workbook
from openerp.exceptions import Warning
from openerp import fields, models, api, _

_logger = logging.getLogger(__name__)


class import_excel(models.Model):
    _name = 'import.excel'
    _inherit = 'mail.thread'
    _description = 'Import Excel'

    def _get_campanha(self, name):
        return self.env['mmp.pre.campanha'].search([('name', '=', name)])

    def _get_state(self):
        return [
            ('new', _('Novo')),
            ('loaded', _('Carregado')),
            ('send_minutas', _('Enviar Minutas')),
            ('imported', _('Importado')),
            ('error', _('Erro')), ]

    name = fields.Char('Nome do Arquivo', size=256,
                       track_visibility='onchange',
                       readonly=True,
                       states={'new': [('readonly', False)]},
                       required=True)
    campanha_id = fields.Many2one('mmp.pre.campanha', 'Campanha',
                                  track_visibility='onchange',
                                  readonly=True,
                                  states={'new': [('readonly', False)]},
                                  required=True)
    state = fields.Selection(_get_state, 'Estado',
                             track_visibility='onchange',
                             default='new',
                             readonly=True,
                             required=True)
    date = fields.Date('Data',
                       track_visibility='onchange',
                       # default=lambda *a: time.strftime("%Y-%m-%d"),
                       readonly=True,
                       states={'new': [('readonly', False)]},
                       required=True)
    num_lines = fields.Integer(u'Número de Linhas',
                               readonly=True)
    imported_lines = fields.Integer(u'Número de Dossiês Importados',
                                    readonly=True)
    imported_lines_error = fields.Integer(u'Número de Dossiês Errados',
                                          readonly=True)
    import_line_ids = fields.One2many('import.excel.line',
                                      'import_excel_id',
                                      'Linhas')
    dossie_ids = fields.One2many('mmp.pre.dossie',
                                 'import_excel_id',
                                 readonly=True)
    file = fields.Binary('Arquivo', readonly=True,
                         states={'new': [('readonly', False)]})
    category_id = fields.Many2many('res.partner.category', id1='dossie_id', id2='category_id',
                                   string=u'Marcadores')
    move_doessie = fields.Boolean(u'Move Dossiês',
                                  help=u"If selected, it will reset workflow for existing dossiês")

    _sql_constraints = [
        ('import_excel_file_unique', 'unique(name)', u'Arquivo com o mesmo nome já existe.'),
    ]

    _order = 'date desc'

    def convert_date_from_excel(self, date_number, date_ref, row):
        try:
            date = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=int(date_number.split('.')[0]))
            if date_ref and date < datetime.datetime.strptime(date_ref, "%Y-%m-%d"):
                raise Warning(u'ERRO', u'A data %s é inferior à data do dia %s, linha %s' % (
                    date.strftime("%Y-%m-%d"), date_ref, row))
        except Exception, err:
            raise Warning(u'ERRO', u'Erro no campo data, linha %s:\n%s' % (row, err[0]))
        return date.strftime("%Y-%m-%d")

    def format_name(self, nome):
        if len(nome) > 3:
            nome = capwords(nome)
            termos = {' Da ': ' da ', ' De ': ' de ', ' Do ': ' do ', ' Das ': ' das ', ' Dos ': ' dos '}
            for termo in termos.keys():
                nome = nome.replace(termo, termos[termo])
        return nome

    def format_cnpj_cpf(self, cnpj_cpf):
        if cnpj_cpf.find('/') == -1:
            is_company = False
            cnpj_cpf = filter(lambda x: x.isdigit(), cnpj_cpf)
            cnpj_cpf = cnpj_cpf[0:3] + '.' + cnpj_cpf[3:6] + '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:]
        else:
            # is a CNPJ
            is_company = True
            cnpj_cpf = filter(lambda x: x.isdigit(), cnpj_cpf)
            cnpj_cpf = cnpj_cpf[-14:-12] + '.' + cnpj_cpf[-12:-9] + '.' + cnpj_cpf[-9:-6] + '/' + cnpj_cpf[
                                                                                                  -6:-2] + '-' + cnpj_cpf[
                                                                                                                 -2:]
        return is_company, cnpj_cpf

    def format_oab(self, oab):
        oab = oab.upper().replace('.', '')
        oab = oab[:-3] + '.' + oab[-3:]
        return oab

    @api.model
    def insere_autor(self, is_autor, is_contato, nome, cnpj_cpf, email):
        # is a CPF
        is_company = False
        autor_ids = {}
        autor_obj = self.env['res.partner']
        if cnpj_cpf and cnpj_cpf != '':
            is_company, cnpj_cpf = self.format_cnpj_cpf(cnpj_cpf)
            autor_ids = autor_obj.search([('cnpj_cpf', '=', cnpj_cpf)])
        if not len(autor_ids):
            autor_ids = autor_obj.search([('name', '=', nome)])
        if len(autor_ids) == 0:
            new_autor = {
                'is_autor': is_autor,
                'is_contato': is_contato,
                'name': nome,
            }
            if email:
                new_autor.update({'email': email})
            if is_company:
                new_autor.update({'is_company': True})
            if cnpj_cpf != '':
                new_autor.update({'cnpj_cpf': cnpj_cpf})
            autor_ids = autor_obj.create(new_autor)
        autor_id = autor_ids[0]
        return autor_id.id

    @api.model
    def insere_credenciado(self, name):
        partner = self.env['res.partner'].search([('name', '=ilike', name)], limit=1)
        if not len(partner):
            partner = self.env['res.partner'].create({'name': name})
        return partner.id

    @api.model
    def insere_fase(self, name):
        fase = self.env['mmp.pre.dossie.fase'].search([('name', '=ilike', name)], limit=1)
        if not len(fase):
            fase = self.env['mmp.pre.dossie.fase'].create({'name': name})
        return fase.id

    @api.model
    def insere_cliente(self, name):
        client = self.env['mmp.pre.client'].search([('name', '=ilike', name)])
        if not len(client):
            raise Warning(u"Cliente '%s' não existe" % name)
        return client.id

    @api.model
    def insere_contato(self, is_autor, is_contato, nome, oab, email=None):
        contato_obj = self.env['res.partner']
        oab_num = ''
        cnpj_cpf_num = ''
        contato_ids = []
        is_company = False
        if oab and oab != '':
            if oab[0:3].lower() == 'oab':
                oab_num = self.format_oab(oab)
                contato_ids = contato_obj.search([('oab', '=', oab_num)])
            else:
                is_company, cnpj_cpf_num = self.format_cnpj_cpf(oab)
                contato_ids = contato_obj.search([('cnpj_cpf', '=', cnpj_cpf_num)])
        if not len(contato_ids):
            contato_ids = contato_obj.search([('name', '=', nome)])
        if len(contato_ids) == 0:
            new_contato = {
                'is_company': is_company,
                'is_autor': is_autor,
                'is_contato': is_contato,
                'name': nome,
            }
            if email != None:
                new_contato.update({'email': email})
            if cnpj_cpf_num != '':
                new_contato.update({'cnpj_cpf': cnpj_cpf_num})
            if oab_num != '':
                new_contato.update({'oab': oab_num})
            contato_ids = contato_obj.create(new_contato)
        contato_id = contato_ids[0]
        return contato_id.id

    @api.model
    def insere_telefones(self, contato_id, tel1, tel2, tel3, tel4, tel5):
        phone_obj = self.env['mmp.pre.phone.number']
        type_obj = self.env['mmp.pre.phone.type']
        cel_id = type_obj.search([('code', '=', 'cel')])[0].id
        com_id = type_obj.search([('code', '=', 'com')])[0].id
        phones = (tel1, tel2, tel3, tel4, tel5)
        principal_tel = None
        for phone in phones:
            if phone != '':
                phone = filter(lambda x: x.isdigit(), phone)
                phone_id = phone_obj.search([('name', '=', phone)])
                if len(phone_id) == 0:
                    if phone[-9:-8] in ('8', '9'):
                        type_id = cel_id
                    else:
                        type_id = com_id
                    phone_status = self.env['mmp.pre.phone.status'].search([('name', '=ilike', 'Aguardando Discagem')])
                    if not len(phone_status):
                        raise Warning(u"Phone status Aguardando Discagem not found")
                    phone_id = phone_obj.create({
                        'name': phone,
                        'partner_id': contato_id,
                        'type_id': type_id,
                        'status_id': phone_status and phone_status.id,
                    })
                    principal_tel = phone_id.id
                else:
                    principal_tel = phone_id[0].id
        return principal_tel

    @api.model
    def insere_dossie(self, category, campanha, file_id, autor_id, nome_autor, contato_id, nome_contato,
                      principal_tel, nome, data_dia, data_audiencia, observacao, object, subject, processo, type, vara,
                      comarca, uf, oferta, acordo, clausula, obrigacoes, multa, tipo_pagamento, titular_conta, cnpj_cpf,
                      oab, banco, agencia, conta, faixa1, faixa2, campanha_line, credenciado_id, fase_id,
                      client_id, obrigacao_editable):
        new_id = 0
        my_city_id = 0
        dossie_obj = self.env['mmp.pre.dossie']
        dossie = dossie_obj.search([('name', '=', nome)])
        if len(dossie) == 0:
            country = self.env['res.country'].search([('code', '=', 'BR')], limit=1)
            if not country:
                raise Warning(u"País '%s' não existe" % 'Brasil')
            uf_id = self.env['res.country.state'].search([('code', '=', uf), ('country_id', '=', country.id)]).ids
            if not uf_id:
                raise Warning(u"Estado '%s' não existe" % uf)
            city_ids = self.env['l10n_br_base.city'].search([('name', 'ilike', comarca)])
            if not city_ids:
                raise Warning(u"Cidade '%s' não existe" % comarca)
            else:
                for city in city_ids:
                    if len(city.name) == len(comarca):
                        if my_city_id == 0:
                            my_city_id = city.id
                        elif city.name == comarca:
                            my_city_id = city.id
                if my_city_id == 0:  # just in case
                    raise Warning(u"Cidade '%s' não existe" % comarca)
            partner_obj = self.env['res.partner']
            autor_cpf = partner_obj.browse(autor_id).read(['cnpj_cpf'])
            if not autor_cpf:
                raise Warning(u"Author '%s' não existe" % nome_autor)
            contato_oab_email = partner_obj.browse(contato_id).read(['oab', 'email'])
            if not contato_oab_email:
                raise Warning(u"Contato '%s' não existe" % nome_contato)

            campanha_id = campanha.id
            if campanha_line:
                campanha_id = self._get_campanha(campanha_line).id
                if not campanha_id:
                    raise Warning(u"campanha '%s' não existe" % campanha_line)

            def error_msg(name, number):
                raise Warning(u'ERRO',
                              u'Valor %s não é um número válido [%s], precisa de casas decimais. Exemplo: 1500,00' % (
                                  name, number))
                return true

            def convert_currency(name, number):
                if number != '':
                    m = re.search('((\d*[.]?)*\d{3})([,]\d{1,})?$', number)
                    if m:
                        n = unicode(m.group().replace('.', '').replace(',', '.'))
                    else:
                        m = re.search('((\d+)|(\d{1,3})([,]\d{3})*)([.]\d{1,})?$', number)
                        if m:
                            n = unicode(m.group().replace(',', '.'))
                        else:
                            error_msg(name, number)
                    try:
                        if float(n) < 0:
                            error_msg(name, number)
                    except ValueError:
                        error_msg(name, number)
                    return n
                else:
                    return '0.0'

            if not type in ('JEC', 'VC'):
                raise Warning(u"Tipo de processo %s desconhecido" % type)

            new_dossie = {
                'campanha_id': campanha_id,
                'autor_id': autor_id,
                'contato_id': contato_id,
                'name': nome,
                'dt_envio_banco': data_dia,
                'dt_audiencia': data_audiencia,
                'processo': processo,
                'type': type,
                'vara': vara,
                'state_id': uf_id[0],
                'l10n_br_city_id': my_city_id,
                'vl_acordo': convert_currency(u'acordo', acordo),
                'import_excel_id': file_id,
                'faixa1': faixa1,
                'faixa2': faixa2,
                'category_id': [(6, 0, [cat.id for cat in category])],
                'credenciado_id': credenciado_id,
                'fase_id': fase_id,
                'client_id': client_id,
            }
            if autor_cpf[0]['cnpj_cpf']:
                new_dossie.update({'cpf': autor_cpf[0]['cnpj_cpf']})
            if contato_oab_email[0]['oab'] != '':
                new_dossie.update({'oab': contato_oab_email[0]['oab']})
            if contato_oab_email[0]['email'] != '':
                new_dossie.update({'email': contato_oab_email[0]['email']})
            if tipo_pagamento != '' and tipo_pagamento:
                try:
                    tp_num = filter(lambda x: x.isdigit(), tipo_pagamento)
                    #                     tp_num = int(tipo_pagamento[:tipo_pagamento.find(' ')])
                    tppgto_id = self.env['mmp.pre.tppagamento'].search(
                        [('number', '=', tp_num)]).ids
                    if tppgto_id:
                        new_dossie.update({'tp_pagamento_id': tppgto_id[0]})
                    else:
                        raise Warning(u"Tipo pagamento '%s' não existe" % tipo_pagamento)
                except Exception, err:
                    raise Warning(u"Tipo pagamento '%s' não existe" % tipo_pagamento)
            if multa != '' and multa:
                try:
                    multa_id = self.env['mmp.pre.multa'].search(
                        [('name', '=', float(multa))]).ids
                    if multa_id:
                        new_dossie.update({'multa_id': multa_id[0]})
                    else:
                        raise Warning(u"Multa '%s' não existe" % multa)
                except Exception, err:
                    raise Warning(u"Multa '%s' não existe" % multa)
            if principal_tel != None:
                new_dossie.update({'main_phone_number_id': principal_tel})
            if observacao != '' and observacao:
                new_dossie.update({'observacoes': observacao})
            if object != '' and object:
                new_dossie.update({'object': object})
            if subject != '' and subject:
                new_dossie.update({'subject': subject})
            if clausula != '' and clausula:
                new_dossie.update({'clausula': clausula, })
            if obrigacoes != '' and obrigacoes:
                new_dossie.update({'obrigacao_editable': True,
                                   'obrigacao': obrigacoes, })

            if banco and conta and agencia:
                new_account = {}
                ben_ids = []
                ben_id = 0
                res_partner = self.env['res.partner']
                if cnpj_cpf != '':
                    is_company, cnpj_cpf = self.format_cnpj_cpf(cnpj_cpf)
                    ben_ids = res_partner.search(
                        [('cnpj_cpf', '=', cnpj_cpf)],
                    ).ids
                    if len(ben_ids) > 0:
                        ben_id = ben_ids[0]
                else:
                    raise Warning(u'ERRO',
                                  u"Tem de indicar um CNPJ/CPF do beneficiário para criar conta do bancário")
                if ben_id == 0:
                    if titular_conta.lower() == nome_autor.lower():
                        ben_id = autor_id
                    elif titular_conta.lower() == nome_contato.lower():
                        ben_id = contato_id
                        is_company, cnpj_cpf = self.format_cnpj_cpf(cnpj_cpf)
                        res_partner.browse(ben_id).write(ben_id,
                                                         {'is_company': is_company,
                                                          'cnpj_cpf': cnpj_cpf})
                if ben_id == 0:
                    if titular_conta and cnpj_cpf:
                        ben_id = self.insere_contato(False, False, titular_conta, cnpj_cpf)
                    else:
                        raise Warning(u"Conta sem indicação de CPF/CNPJ ou nome de titular")
                bank_obj = self.env['res.bank']
                try:
                    bank_n = format(int(filter(lambda x: x.isdigit(), banco)), '03d')
                except Exception, err:
                    raise Warning(u"Banco '%s' sem código numérico" % banco)
                bank = bank_obj.search([('bic', '=', bank_n)], limit=1)
                if bank:
                    def get_num_dig(num):
                        # num = num.replace('.', '')
                        sep = num.find('-')
                        if sep > 0:
                            n = num[:sep]
                            d = num[sep + 1:]
                        else:
                            n = int(float(num))
                            d = ' '
                        return unicode(n), unicode(d)

                    cnt, cnt_dig = get_num_dig(conta)
                    ag, ag_dig = get_num_dig(agencia)
                    new_account.update({
                        'state': 'bank',
                        'acc_number': cnt,
                        'acc_number_dig': cnt_dig,
                        'bra_number': ag,
                        'bra_number_dig': ag_dig,
                        'partner_id': ben_id,
                        'bank': bank.id,
                        'bank_name': bank.name,
                    })
                    new_account_id = self.env['res.partner.bank'].create(new_account)
                    if new_account_id:
                        new_dossie.update({'banco_id': new_account_id.id})
                    else:
                        raise Warning(u"Erro ao criar conta")
                else:
                    raise Warning(u"Banco '%s' não existe" % banco)
            new_id = dossie_obj.create(new_dossie)
            #update obrigacao_editable
            if object != '' and object:
                new_id.get_obrigacao_editable(excel_import=True)
            else:
            # if dossie already exists
            # move to Aguardando Contato
                if self.move_doessie:
                    dossie.set_aguarda_contato()
                else:
                    raise Warning(u"Dossiê %s já existe.\nCampanha: %s\nEstado: %s" % (nome,
                        dossie.campanha_id.name, dossie.state))
        return new_id

    @api.model
    def update_dossie(self, line, autor_id, contato_id, principal_tel,campanha,campanha_line, credenciado_id, fase_id,
                      client_id,category):

        dossie = self.env['mmp.pre.dossie'].search([('name', '=', line.dossie)])
        
        country = self.env['res.country'].search([('code', '=', 'BR')], limit=1)
        if not country:
            raise Warning(u"País '%s' não existe" % 'Brasil')
        uf_id = self.env['res.country.state'].search([('code', '=', line.uf), ('country_id', '=', country.id)]).ids
        if not uf_id:
            raise Warning(u"Estado '%s' não existe" % line.uf)
        city_ids = self.env['l10n_br_base.city'].search([('name', 'ilike', line.comarca)])
        my_city_id = 0
        if not city_ids:
            raise Warning(u"Cidade '%s' não existe" % line.comarca)
        else:
            for city in city_ids:
                if len(city.name) == len(line.comarca):
                    if my_city_id == 0:
                        my_city_id = city.id
                    elif city.name == line.comarca:
                        my_city_id = city.id
            if my_city_id == 0:  # just in case
                raise Warning(u"Cidade '%s' não existe" % line.comarca)
        
        partner_obj = self.env['res.partner']
        autor_cpf = partner_obj.browse(autor_id).read(['cnpj_cpf'])
        if not autor_cpf:
            raise Warning(u"Author '%s' não existe" % line.autor)
        cpf = False
        if autor_cpf[0]['cnpj_cpf']:
            cpf = autor_cpf[0]['cnpj_cpf']

        campanha_id = campanha.id
        if campanha_line:
            campanha_id = self._get_campanha(campanha_line).id
            if not campanha_id:
                raise Warning(u"campanha '%s' não existe" % campanha_line)
        
        tp_pagamento_id = False
        if line.tipo_pagamento != '' and line.tipo_pagamento:
            try:
                tp_num = filter(lambda x: x.isdigit(), line.tipo_pagamento)
                tppgto_id = self.env['mmp.pre.tppagamento'].search(
                    [('number', '=', tp_num)]).ids
                if tppgto_id:
                    tp_pagamento_id = tppgto_id[0]
                else:
                    raise Warning(u"Tipo pagamento '%s' não existe" % line.tipo_pagamento)
            except Exception, err:
                raise Warning(u"Tipo pagamento '%s' não existe" % line.tipo_pagamento)
        
        multa = False
        if line.multa != '' and line.multa:
            try:
                multa_id = self.env['mmp.pre.multa'].search(
                    [('name', '=', float(line.multa))]).ids
                if multa_id:
                    multa = multa_id[0]
                else:
                    raise Warning(u"Multa '%s' não existe" % line.multa)
            except Exception, err:
                raise Warning(u"Multa '%s' não existe" % line.multa)

        def convert_currency(name, number):
            if number != '':
                m = re.search('((\d*[.]?)*\d{3})([,]\d{1,})?$', number)
                if m:
                    n = unicode(m.group().replace('.', '').replace(',', '.'))
                else:
                    m = re.search('((\d+)|(\d{1,3})([,]\d{3})*)([.]\d{1,})?$', number)
                    if m:
                        n = unicode(m.group().replace(',', '.'))
                    else:
                        error_msg(name, number)
                try:
                    if float(n) < 0:
                        error_msg(name, number)
                except ValueError:
                    error_msg(name, number)
                return n
            else:
                return '0.0'
        
        obj = False
        sub = False
        clausula = False
        if line.object != '' and line.object:
            obj = line.object
        if line.subject != '' and line.subject:
            sub = line.subject
        if line.clausula != '' and line.clausula:
            clausula = line.clausula
            
        if dossie:
            dossie[0].write({
                'dt_envio_banco': line.data_dia,
                'dt_audiencia': line.audiencia,
                'name': line.dossie,
                'autor_id': autor_id,
                'cpf': cpf,
                'observacoes': line.observacao,
                'faixa1': line.faixa1,
                'faixa2': line.faixa2,
                'processo': line.processo,
                'type': line.type,
                'vara': line.vara,
                'state_id': uf_id[0],
                'l10n_br_city_id': my_city_id,
                'obrigacao_editable': '',
                'contato_id': contato_id,
                'oab': line.oab,
                'email': line.email,
                'campanha_id': campanha_id,
                'credenciado_id': credenciado_id,
                'fase_id': fase_id,
                'client_id': client_id,
                'import_excel_id': self.id,
                'obrigacao': line.obrigacao_editable,
                'vl_acordo': convert_currency(u'acordo', line.valor_acordo),
                'category_id': [(6, 0, [cat.id for cat in category])],
                'tp_pagamento_id': tp_pagamento_id,
                'multa_id': multa,
                'main_phone_number_id': principal_tel,
                'object': obj,
                'subject': sub,
                'clausula': clausula,
#                 'banco_id': '',
                        })
        return True
                      
    def import_envia_minutas(self):
        #         threaded_send_email = threading.Thread(target=self.import_envia_minutas_backgroud, args=(cr, uid, ids, context))
        #         threaded_send_email.start()
        dossie_obj = self.env['mmp.pre.dossie']
        for import_obj in self:
            dossie_ids = dossie_obj.search([('import_excel_id', '=', import_obj.id),
                                            ('state', '=', 'ac')],
                                           )
            for dossie in dossie_ids:
                dossie.set_minuta_enviada()
            self.write([import_obj.id], {'state': 'imported'})
        return True

    def import_spreadsheet(self):
        line_objs = self.env['import.excel.line']
        for import_obj in self:
            update_import = {}
            num_errors = 0
            imported_lines = import_obj.imported_lines
            imported_lines_error = import_obj.imported_lines_error
            line_obj_ids = line_objs.search(
                [('import_excel_id', '=', import_obj.id), ('state', 'in', ('new', 'error'))],
            )
            for line in line_obj_ids:
                err = ''
                is_autor_contato = False
                is_update = False
                try:
                    email = ''
                    if line.contato.lower() == 'advogado':
                        email = line.email
                        is_autor_contato = True
                    try:
                        autor_id = self.insere_autor(True, is_autor_contato, self.format_name(line.autor),
                                                     line.cpf, email)
                    except Exception, err:
                        raise Warning(u"ERRO INSERINDO AUTOR:\n%s" % err[0])
                    try:
                        contato_id = self.insere_contato(is_autor_contato, True,
                                                         self.format_name(line.advogado), line.oab, email,
                                                         )
                    except Exception, err:
                        raise Warning(u"ERRO INSERINDO CONTATO:\n%s" % err[0])
                    try:
                        credenciado_id = self.insere_credenciado(
                            self.format_name(line.credenciado),
                        )
                    except Exception, err:
                        raise Warning(u"ERRO INSERINDO CREDENCIADO:\n%s" % err[0])
                    try:
                        fase_id = self.insere_fase(line.fase)
                    except Exception, err:
                        raise Warning(u"ERRO INSERINDO FASE:\n%s" % err[0])
                    try:
                        ciente_id = self.insere_cliente(line.cliente)
                    except Exception, err:
                        raise Warning(u"ERRO INSERINDO Cliente: \n%s" % err[0])
                    try:
                        principal_tel = self.insere_telefones(contato_id, line.tel1, line.tel2, line.tel3,
                                                              line.tel4, line.tel5)
                    except Exception, err:
                        raise Warning(u"ERRO INSERINDO TELEFONES:\n%s" % err[0])
                    try:
                        new_id = self.insere_dossie(import_obj.category_id, import_obj.campanha_id,
                                                    import_obj.id, autor_id, line.autor, contato_id, line.advogado,
                                                    principal_tel, line.dossie, line.data_dia, line.audiencia,
                                                    line.observacao, line.object, line.subject, line.processo,
                                                    line.type, line.vara, line.comarca, line.uf, line.valor_oferta,
                                                    line.valor_acordo, line.clausula, line.obrigacoes, line.multa,
                                                    line.tipo_pagamento, line.titular_conta, line.cpf_beneficiario,
                                                    line.oab, line.banco, line.agencia, line.conta, line.faixa1,
                                                    line.faixa2, line.campanha, credenciado_id, fase_id, ciente_id,
                                                    line.obrigacao_editable
                                                    )
                        if new_id == 0:
                            self.update_dossie(line,autor_id,contato_id,principal_tel,import_obj.campanha_id,line.campanha, credenciado_id, fase_id, ciente_id,import_obj.category_id)
                            is_update = True
                    except Exception, err:
                        raise Warning(u"ERRO INSERINDO DOSSIÊ:\n%s" % err[0])
                except Exception, err:
                    if line.state == 'new':
                        imported_lines_error += 1
                    try:
                        error_msg = err[0]
                    except:
                        error_msg = err
                    line.write(
                        {'state': 'error',
                         'importation_error': error_msg,
                         'importation_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                         })
                    num_errors += 1
                if err == '':
                    if line.state == 'new':
                        imported_lines += 1
                    elif line.state == 'error':
                        imported_lines += 1
                        imported_lines_error -= 1
                    if is_update:
                        dossie = self.env['mmp.pre.dossie'].search([('name', '=', line.dossie)])
                        msg = u"Dossiê %s já existe.\nCampanha: %s\nEstado: %s" % (line.dossie,
                            dossie.campanha_id.name, dossie.state)
                        line.write(
                            {'state': 'imported',
                             'importation_error': msg,
                             'importation_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                             })
                    else:
                        line.write(
                            {'state': 'imported',
                             'importation_error': '',
                             'importation_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                             })
            if num_errors < 1:
                update_import.update({'state': 'imported'})
            update_import.update({'imported_lines': imported_lines,
                                  'imported_lines_error': imported_lines_error})
            self.write(update_import)
        return True

    def load_spreadsheet(self):
        line_header = {
            0: 'Data do Dia',
            1: u'Audiência',
            2: u'Audiência',
            3: u'Dossiê',
            4: 'Autor',
            5: 'CPF',
            6: u'OBSERVAÇÃO',
            7: 'FAIXA1',
            8: 'FAIXA2',
            9: 'OBJETO',
            10: 'ASSUNTO',
            11: 'PROCESSO',
            12: 'TIPO',
            13: 'VARA',
            14: 'COMARCA',
            15: 'UF',
            16: 'VALOR DA OFERTA',
            17: 'VALOR DO ACORDO',
            18: u'CLÁUSULA',
            19: u'OBRIGAÇÕES',
            20: 'MULTA',
            21: 'TIPO DE PAGAMENTO',
            22: 'TITULAR DA CONTA',
            23: u'CPF DO BENEFICIÁRIO',
            24: 'BANCO',
            25: u'AGÊNCIA',
            26: 'CONTA',
            27: 'CONTATO',
            28: u'ADVOGADO DA PARTE CONTRÁRIA',
            29: 'OAB',
            30: 'E-MAIL',
            31: 'TEL1',
            32: 'TEL2',
            33: 'TEL3',
            34: 'TEL4',
            35: 'TEL5',
            36: 'CAMPANHA',
            37: 'CREDENCIADO',
            38: 'FASE',
            39: 'CLIENTE',
            40: 'OBRIGACAO_EDITABLE',
        }
        import_line_obj = self.env['import.excel.line']
        is_company = False

        def get_integer_part(number):
            if number != '':
                try:
                    # number = unicode(int(float(number)))
                    dot = number.find('.')
                    if dot > 0:
                        number = filter(lambda x: x.isdigit(), number[:dot])
                    else:
                        number = filter(lambda x: x.isdigit(), number)
                except:
                    raise Warning(u"Número de telefone %s incorreto" % number)
            return number

        for imp in self:
            try:
                wb = open_workbook(file_contents=base64.decodestring(imp.file))
            except:
                raise Warning(
                    u"Formato de arquivo não suportado (use apenas XLS).\nPor favor, abra este arquivo e salve-o como um arquivo XLS.")
            s = wb.sheets()[0]
            new_id = 0
            num = 0
            imported = 0
            if s.nrows == 0:
                raise Warning(
                    u"Formato de arquivo não suportado (use apenas XLS).\nPor favor, abra este arquivo e salve-o como um arquivo XLS.")
            for row in range(s.nrows):
                is_autor_contato = False
                line = {}
                for col in range(s.ncols):
                    line[col] = unicode(s.cell(row, col).value).strip(' \t\n\r')
                    #what does below condition do??
                    # if line[col] == '0.0':
                    #     # raise Warning(u"Arquivo com fórmulas na posição [%s,%s]'" % (
                    #     #     unicode(row + 1), unicode(col + 1)))
                if row == 0:
                    # last column is optional
                    if len(line.values()) == 36:
                        if line_header.values()[:-1] != line.values():
                            raise Warning(u"Arquivo com formato errado")
                    else:
                        if line_header.values() != line.values():
                            raise Warning(u"Arquivo com formato errado")
                else:
                    if line[3] != '' and line[3]:
                        data_dia = self.convert_date_from_excel(line[0], 0, row + 1)
                        audiencia = self.convert_date_from_excel(line[1], data_dia, row + 1)
                        audiencia2 = self.convert_date_from_excel(line[2], data_dia, row + 1)
                        if len(line.values()) == 36:
                            line[36] = dict(self._get_campanha())[self[0].campanha]

                        row_line = {
                            'import_excel_id': self[0].id,
                            'num_line': row + 1,
                            'data_dia': data_dia,
                            'audiencia': audiencia,
                            'audiencia2': audiencia2,
                            'dossie': line[3],
                            'autor': self.format_name(line[4]),
                            'cpf': line[5],
                            'observacao': line[6],
                            'faixa1': line[7],
                            'faixa2': line[8],
                            'object': line[9],
                            'subject': line[10],
                            'processo': line[11],
                            'type': line[12],
                            'vara': line[13],
                            'comarca': line[14],
                            'uf': line[15],
                            'valor_oferta': line[16],
                            'valor_acordo': line[17],
                            'clausula': line[18],
                            'obrigacoes': line[19],
                            'multa': line[20],
                            'tipo_pagamento': line[21],
                            'titular_conta': line[22],
                            'cpf_beneficiario': line[23],
                            'banco': line[24],
                            'agencia': line[25],
                            'conta': line[26],
                            'contato': line[27],
                            'advogado': self.format_name(line[28]),
                            'oab': line[29],
                            'email': line[30],
                            'tel1': get_integer_part(line[31]),
                            'tel2': get_integer_part(line[32]),
                            'tel3': get_integer_part(line[33]),
                            'tel4': get_integer_part(line[34]),
                            'tel5': get_integer_part(line[35]),
                            'campanha': line[36],
                            'credenciado': line[37],
                            'fase': line[38],
                            'cliente': line[39],
                            'obrigacao_editable' : line[40],
                        }
                        if row_line['cpf'] != '':
                            is_company, row_line['cpf'] = self.format_cnpj_cpf(row_line['cpf'])
                        if row_line['oab'] != '':
                            if row_line['oab'][0:3].lower() == 'oab':
                                row_line['oab'] = self.format_oab(row_line['oab'])
                            else:
                                is_company, row_line['oab'] = self.format_cnpj_cpf(row_line['oab'])
                        import_line_obj.create(row_line)
            imp.write({'state': 'loaded',
                       'num_lines': row})
        return True


class import_excel_line(models.Model):
    _name = 'import.excel.line'
    _description = 'Import Excel Line'

    @api.model
    def _get_state(self):
        return [
            ('new', _('Novo')),
            ('imported', _('Importado')),
            ('error', _('Erro')), ]

    import_excel_id = fields.Many2one(
        'import.excel', 'Import Excel ID',
        ondelete='cascade',
        readonly=True)
    num_line = fields.Integer(u'Número de Linha',
                              readonly=True)
    state = fields.Selection(_get_state, 'Estado',
                             default='new',
                             readonly=True,
                             required=True)
    importation_date = fields.Datetime(u'Data Importação',
                                       default=lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
                                       readonly=True,
                                       required=True)
    importation_error = fields.Text(u'Erro Importação',
                                    readonly=True)
    data_dia = fields.Char('Data do Dia', size=256,
                           readonly=False,
                           states={'imported': [('readonly', True)]})
    audiencia = fields.Char(u'Audiência', size=256,
                            readonly=False,
                            states={'imported': [('readonly', True)]})
    audiencia2 = fields.Char(u'Audiência2', size=256,
                             readonly=False,
                             states={'imported': [('readonly', True)]})
    dossie = fields.Char(u'Dossiê', size=256,
                         readonly=False,
                         states={'imported': [('readonly', True)]})
    autor = fields.Char('Autor', size=256,
                        readonly=False,
                        states={'imported': [('readonly', True)]})
    cpf = fields.Char('CPF', size=256,
                      readonly=False,
                      states={'imported': [('readonly', True)]})
    observacao = fields.Text(u'Observação',
                             readonly=False,
                             states={'imported': [('readonly', True)]})
    object = fields.Char('Objeto', size=256,
                         readonly=False,
                         states={'imported': [('readonly', True)]})
    subject = fields.Char('Assunto', size=256,
                          readonly=False,
                          states={'imported': [('readonly', True)]})
    processo = fields.Char(u'Processo', size=256,
                           readonly=False,
                           states={'imported': [('readonly', True)]})
    type = fields.Char('Tipo', size=3,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    vara = fields.Char('Vara', size=256,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    comarca = fields.Char('Comarca', size=256,
                          readonly=False,
                          states={'imported': [('readonly', True)]})
    uf = fields.Char('UF', size=256,
                     readonly=False,
                     states={'imported': [('readonly', True)]})
    valor_oferta = fields.Char('Valor da Oferta', size=256,
                               readonly=False,
                               states={'imported': [('readonly', True)]})
    valor_acordo = fields.Char('Valor do Acordo', size=256,
                               readonly=False,
                               states={'imported': [('readonly', True)]})
    clausula = fields.Text(u'Cláusula',
                           readonly=False,
                           states={'imported': [('readonly', True)]})
    obrigacoes = fields.Text(u'Obrigações',
                             readonly=False,
                             states={'imported': [('readonly', True)]})
    multa = fields.Char('Multa', size=256,
                        readonly=False,
                        states={'imported': [('readonly', True)]})
    tipo_pagamento = fields.Char('Tipo de Pagamento', size=256,
                                 readonly=False,
                                 states={'imported': [('readonly', True)]})
    titular_conta = fields.Char('Titular da Conta', size=256,
                                readonly=False,
                                states={'imported': [('readonly', True)]})
    cpf_beneficiario = fields.Char(u'CPF Beneficiário', size=256,
                                   readonly=False,
                                   states={'imported': [('readonly', True)]})
    banco = fields.Char('Banco', size=256,
                        readonly=False,
                        states={'imported': [('readonly', True)]})
    agencia = fields.Char(u'Agência', size=256,
                          readonly=False,
                          states={'imported': [('readonly', True)]})
    conta = fields.Char('Conta', size=256,
                        readonly=False,
                        states={'imported': [('readonly', True)]})
    contato = fields.Char('Contato', size=256,
                          readonly=False,
                          states={'imported': [('readonly', True)]})
    advogado = fields.Char(u'Advogado da Parte Contrária', size=256,
                           readonly=False,
                           states={'imported': [('readonly', True)]})
    oab = fields.Char('OAB', size=256,
                      readonly=False,
                      states={'imported': [('readonly', True)]})
    email = fields.Char('Email', size=256,
                        readonly=False,
                        states={'imported': [('readonly', True)]})
    tel1 = fields.Char('Tel1', size=256,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    tel2 = fields.Char('Tel2', size=256,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    tel3 = fields.Char('Tel3', size=256,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    tel4 = fields.Char('Tel4', size=256,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    tel5 = fields.Char('Tel5', size=256,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    faixa1 = fields.Char('Faixa1', size=256,
                         readonly=False,
                         states={'imported': [('readonly', True)]})
    faixa2 = fields.Char('Faixa2', size=256,
                         readonly=False,
                         states={'imported': [('readonly', True)]})
    campanha = fields.Char('Campanha', size=32, readonly=False,
                           states={'imported': [('readonly', True)]})
    credenciado = fields.Char('Credenciado', size=256,
                              readonly=False,
                              states={'imported': [('readonly', True)]})
    fase = fields.Char('Fase', size=256,
                       readonly=False,
                       states={'imported': [('readonly', True)]})
    cliente = fields.Char('Cliente', size=256,
                          readonly=False,
                          states={'imported': [('readonly', True)]})
    obrigacao_editable = fields.Char('Tem Obrigação', size=256,
                          readonly=False,
                          states={'imported': [('readonly', True)]})


    _order = 'num_line, importation_date desc'
