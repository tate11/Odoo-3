# -*-coding:utf-8-*-
from odoo import models, fields, api, _
import odoo
import time
from xlrd import open_workbook
import xlrd
from datetime import datetime
import threading
from Queue import Queue
import os
import logging
from dossie import dossie_state, tipo_processo_vals, parecer_vals, analise_acordo_vals, responsabilidade_vals, \
    risco_vals, polo_cliente_vals, assuncao_defesa_vals, boolean_selection_vals

_logger = logging.getLogger(__name__)
import base64
import time
global t1
def ncpus():
    # for Linux, Unix and MacOS
    if hasattr(os, "sysconf"):
        if os.sysconf_names.has_key("SC_NPROCESSORS_ONLN"):
            # Linux and Unix
            ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
            if isinstance(ncpus, int) and ncpus > 0:
                return ncpus
        else:
            # MacOS X
            return int(os.popen2("sysctl -n hw.ncpu")[1].read())
    # for Windows
    if os.environ.has_key("NUMBER_OF_PROCESSORS"):
        ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
        if ncpus > 0:
            return ncpus
    # return the default value
    return 1


class import_dossie_excel(models.Model):
    _name = 'import.dossie.excel'
    _inherit = 'mail.thread'
    _description = 'Import Excel'

    name = fields.Char('Nome do Arquivo', size=256,
                       track_visibility='onchange',
                       readonly=True,
                       states={'new': [('readonly', False)]},
                       required=True)
    state = fields.Selection([
        ('new', _('Novo')),
        ('loaded', _('Carregado')),
        ('imported', _('Importado')),
        ('error', _('Erro')), ], 'Estado',
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
                               readonly=True, copy=False)
    imported_lines = fields.Integer(u'Número de Dossiês Importados',
                                    readonly=True, copy=False)
    imported_lines_error = fields.Integer(u'Número de Dossiês Errados',
                                          readonly=True, copy=False)
    # dossie_ids = fields.One2many('project.dossie', 'import_excel_id',
    #                            readonly=True)
    import_line_ids = fields.One2many('import.dossie.excel.line',
                                      'import_excel_id',
                                      'Linhas')
    file = fields.Binary('Arquivo', readonly=True,
                         states={'new': [('readonly', False)]})
    create_escritorio = fields.Boolean(u'Escritorio', default=True)
    create_credenciado = fields.Boolean(u'Credenciado', default=True)
    limit = fields.Integer('Limit')

    def format_boolean(self, value):
        if value.upper() in ['TRUE', 'VERDADEIRO']:
            return True
        return False

    def format_number(self, number):
        try:
            return int(float(number))
        except:
            return number

    def format_date(self, number, wb):
        try:
            date = float(number)
            date = datetime(*xlrd.xldate_as_tuple(date, wb.datemode))
            return date
        except:
            return False

    def get_uf(self, uf, country_code=False):
        if not uf:
            return False
        country = self.env['res.country'].search([('code', '=', 'BR')])
        if not len(country):
            raise Warning(u"Country with code BR not found")
        if len(country) > 1:
            raise Warning(u"Multiple countries found for code BR")
        if len(uf) == 2:
            state = self.env['res.country.state'].search([('code', '=ilike', uf), ('country_id', '=', country.id)])
        else:
            state = self.env['res.country.state'].search([('name', '=ilike', uf), ('country_id', '=', country.id)])
        if not len(state):
            raise Warning(u"State %s not found" % uf)
        if len(state) > 1:
            raise Warning(u"Multiple states found with name %s for country Brasil" % uf)
        return state.id

    def get_comarca_id(self, comarca, state_id):
        if not comarca:
            return False
        if not state_id:
            raise Warning(u"State not set")
        city = self.env['res.state.city'].search([('name', '=ilike', comarca), ('state_id', '=', state_id)])
        if not len(city):
            raise Warning(u"City %s not found for state ID %s" % (comarca, state_id))
        if len(city) > 1:
            raise Warning(u"Multiple cities found with name %s for state ID %s" % (comarca, state_id))
        return city.id

    def format_cnpj_cpf(self, cnpj_cpf):
        is_company = False
        if cnpj_cpf:
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

    def get_advogado(self, line):
        partner = []
        cnpj_cpf = False
        if not len(partner) and line.oab:
            partner = self.env['res.partner'].search([('oab', '=', line.oab)])
        if not len(partner) and line.cnpj_cpf:
            is_company, cnpj_cpf = self.format_cnpj_cpf(line.cnpj_cpf)
            partner = self.env['res.partner'].search([('cnpj_cpf', '=', cnpj_cpf)])
        if not len(partner) and line.name:
            partner = self.env['res.partner'].search([('name', '=', line.name)])
        if not line.name:
            return False
        if not line.name:
            return False
        if not len(partner):
            partner = self.env['res.partner'].create({
                'name': line.name,
                'cnpj_cpf': cnpj_cpf or False,
                'phone': line.phone,
                'oab': line.oab or False,
                'is_advogado': line.is_advogado,
                'is_company': line.is_company,
                'mobile': line.mobile,
                'email': line.email,
            })
        return partner[0].id

    def get_partner(self, line):
        partner = []
        cnpj_cpf = False
        if not len(partner) and line.cnpj_cpf:
            is_company, cnpj_cpf = self.format_cnpj_cpf(line.cnpj_cpf)
            partner = self.env['res.partner'].search([('cnpj_cpf', '=', cnpj_cpf)])
        if not len(partner) and line.name:
            partner = self.env['res.partner'].search([('name', '=', line.name)])
        if not len(partner):
            country_id = False
            state_id = False
            city_id = False

            country = self.env['res.country'].search([('name', '=ilike', line.country)], limit=1)
            if country:
                country_id = country.id

            if country_id:
                country = self.env['res.country'].browse(country_id)
                state_id = self.get_uf(line.state, country.code)
                if state_id:
                    city_id = self.get_comarca_id(line.city, state_id)
            if not line.name:
                return False
            if not line.name:
                return False
            if not len(partner):
                partner = self.env['res.partner'].create({
                    'name': line.name,
                    'cnpj_cpf': cnpj_cpf,
                    'legal_name': line.razao_social,
                    'number': line.number,
                    'district': line.district,
                    'street': line.street,
                    'street2': line.street2,
                    'phone': line.phone,
                    'mobile': line.mobile,
                    'email': line.email,
                    'city_id': city_id,
                    'is_company': line.is_company,
                    'state_id': state_id,
                    'country_id': country_id,
                    'is_parte_contraria': line.is_parte_contraria,
                    'is_parte_representada': line.is_parte_representada,
                })
        return partner[0].id

    def reset_import(self):
        self.write({'state': 'loaded',
                    'imported_lines_error': 0,
                    'imported_lines': 0,
                    })
        self.import_line_ids.write({'state': 'new'})
        return True

    def load_spreadsheet(self):

        # big numbers are read as floating point numbers from excel
        # covert them to float and int

        line_header = {
            0: u'Dossiê',  # A# name
            1: u'Processo Nº',  # B# processo
            2: u'Status',  # C# state
            3: u'Polo Cliente',  # D# polo_cliente
            4: u'Fase Atual',  # E# fase_id
            5: u'Origem',  # F# origem_id
            6: u'Tipo do Processo',  # G# tipo_processo
            7: u'Parte Representada',  # H# parte_representada_ids.name
            8: u'Parte Representada / Razão Social',  # I# parte_representada_ids.razao_social
            9: u'Parte Representada / CPF ou CNPJ',  # J# parte_representada_ids.cnpj_cpf
            10: u'Parte Representada / Telefone',  # K# parte_representada_ids.phone
            11: u'Parte Representada / Mobile',  # L# parte_representada_ids.mobile
            12: u'Parte Representada / Email',  # M# parte_representada_ids.email
            13: u'Parte Representada / É Parte Representada',  # N# parte_representada_ids.name
            14: u'Parte Representada / É Empresa',  # O# parte_representada_ids.is_company
            15: u'Parte Representada / Grupo',  # p# parte_representada_ids.parent_id
            16: u'Parte Representada / Rua',  # Q# parte_representada_ids.street
            17: u'Parte Representada / Nº',  # R# parte_representada_ids.number
            18: u'Parte Representada / Complemento',  # S# parte_representada_ids.street2
            19: u'Parte Representada / Bairro',  # T# parte_representada_ids.district
            20: u'Parte Representada / Cidade',  # U# parte_representada_ids.city_id
            21: u'Parte Representada / UF',  # V# parte_representada_ids.state_id
            22: u'Parte Representada / País',  # W# parte_representada_ids.country_id
            23: u'Parte Contrária',  # X# parte_contraria_ids
            24: u'Parte Contrária / CPF ou CNPJ',  # Y# parte_contraria_ids.cnpj_cpf
            25: u'Parte Contrária / Telefone',  # Z# parte_contraria_ids.phone
            26: u'Parte Contrária / Celular',  # AA# parte_contraria_ids.mobile
            27: u'Parte Contrária / Email',  # AB# parte_contraria_ids.email
            28: u'Parte Contrária / É Parte Contrária',  # AC# parte_contraria_ids.is_parte_contraria
            29: u'Parte Contrária / É Empresa',  # AD# parte_contraria_ids.is_company
            30: u'Parte Contrária / Rua',  # AE# parte_contraria_ids.street
            31: u'Parte Contrária / Nº',  # AF# parte_contraria_ids.number
            32: u'Parte Contrária / Complemento',  # AG# parte_contraria_ids.street2
            33: u'Parte Contrária / Bairro',  # AH# parte_contraria_ids.district
            34: u'Parte Contrária / Cidade',  # AI# parte_contraria_ids.city_id
            35: u'Parte Contrária / UF',  # AJ# parte_contraria_ids.state_id
            36: u'Parte Contrária / País',  # AK# parte_contraria_ids.country_id
            37: u'Advogado Adverso',  # AL# advogado_adverso_ids.name
            38: u'Advogado Adverso / CPF ou CNPJ',  # AM# advogado_adverso_ids.cnpj_cpf
            39: u'Advogado Adverso / OAB',  # AN# advogado_adverso_ids.oab
            40: u'Advogado Adverso / Mobile',  # AO# advogado_adverso_ids.mobile
            41: u'Advogado Adverso / Email',  # AP# advogado_adverso_ids.email
            42: u'Advogado Adverso / É Advogado',  # AQ# advogado_adverso_ids.is_advogado
            43: u'Advogado Adverso / É Empresa',  # AR# advogado_adverso_ids.is_company
            44: u'Advogado Adverso / Escritório',  # AS# advogado_adverso_ids.parent_id
            45: u'Escritório',  # AT# escritorio_id.name
            46: u'Escritório / Razão Social',  # AU# escritorio_id.razao_social
            47: u'Escritório / CPF ou CNPJ',  # AV# escritorio_id.cnpj_cpf
            48: u'Escritório / Telefone',  # AW# escritorio_id.phone
            49: u'Escritório / Email',  # AX# escritorio_id.email
            50: u'Escritório / É Escritório',  # AY# escritorio_id.is_escritorio
            51: u'Escritório / É Empresa',  # AZ# escritorio_id.is_company
            52: u'Escritório / Rua',  # BA# escritorio_id.street
            53: u'Escritório / Nº',  # BB# escritorio_id.number
            54: u'Escritório / Complemento',  # BC# escritorio_id.street2
            55: u'Escritório / Bairro',  # BD# escritorio_id.district
            56: u'Escritório / Cidade',  # BE# escritorio_id.city_id
            57: u'Escritório / UF',  # BF# escritorio_id.state_id
            58: u'Escritório / País',  # BG# escritorio_id.country_id
            59: u'Assunção de Defesa',  # BH# assuncao_defesa
            60: u'Valor da Causa',  # BI# valor_causa
            61: u'Valor do Dano Moral',  # BJ# valor_dano_moral
            62: u'Valor do Dano Material',  # BK# valor_dano_material
            63: u'Data da Distribuição',  # BL# data_distribuicao
            64: u'Rito',  # BM# rito_id
            65: u'Nº Ordinal',  # BN# ordinal
            66: u'Vara',  # BO# vara_id
            67: u'Orgão',  # BP# orgao_id
            68: u'Comarca',  # BQ# comarca_id
            69: u'UF',  # BR# estado_id
            70: u'Natureza',  # BS# natureza_id
            71: u'Tipo da Ação',  # BT# tipo_acao_id
            72: u'Projeto',  # BU# projeto_id
            73: u'Credenciado',  # BV# credenciado_id
            74: u'Credenciado / Razão Social',  # BX# credenciado_id.razao_social
            75: u'Credenciado / CNPJ',  # BX# credenciado_id.cnpj_cpf
            76: u'Credenciado / Telefone',  # BY# credenciado_id.phone
            77: u'Credenciado / Email',  # BZ# credenciado_id.email
            78: u'Credenciado / É Credenciado',  # CA# credenciado_id.is_credenciado
            79: u'Credenciado / É Empresa',  # CB# credenciado_id.is_company
            80: u'Objeto',  # CC# objeto_id
            81: u'Assunto',  # CD# assunto_id
            82: u'Local do Fato',  # CE# local_fato
            83: u'Data do Fato',  # CF# data_fato
            84: u'Parecer',  # CG# parecer
            85: u'Subsidio',  # CH# subsidio
            86: u'Análise Acordo',  # CI# analise_acordo
            87: u'Motivo de Inaptidão',  # CJ# motivo_inaptidao
            88: u'Valor da Alçada',  # CK# valor_alcada
            89: u'Contrato',  # CL# contrato_id
            90: u'Carteira',  # CM# carteira_id
            91: u'Responsabilidade',  # CN# responsabilidade
            92: u'Risco',  # CO# risco
            93: u'Obrigação de Fazer',  # CP# obrigacao
            94: u'Liminar',  # CQ# _liminar
            95: u'Data Audiencia Inicial',  # CR# data_audiencia_inicial
            96: u'Tem Advogado',  # CS
            97: u'Grupo' # CT grupo_id
        }
        excel_line_obj = self.env['import.dossie.excel.line']
        advogado_adverso_obj = self.env['excel.advogado.adverso']
        parte_contraria_obj = self.env['excel.parte.contraria']
        parte_representada_obj = self.env['excel.parte.representada']

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
                if row == 0:
                    continue
                is_autor_contato = False
                line = {}
                num_lines = self.num_lines
                for col in range(s.ncols):
                    line[col] = unicode(s.cell(row, col).value).strip(' \t\n\r')
                # if row == 0:
                #     # last column is optional
                #     if len(line.values()) == 14:
                #         print line_header.values()
                #         print "=================="
                #         print line.values()
                #         if line_header.values() != line.values():
                #             raise Warning(u"Arquivo com formato errado")
                #     else:
                #         if line_header.values() != line.values():
                #             raise Warning(u"Arquivo com formato errado")
                else:
                    # 0 to 15
                    if line[1]:
                        num_lines += 1
                        # File Format
                        row_line = {
                            'dossie': line[0],
                            'processo': line[1],
                            'dossie_state': line[2],
                            'polo_cliente': line[3],
                            'fase': line[4],
                            'origem': line[5],
                            'tipo_processo': line[6],
                            'groupo': line[22],
                            'escritorio': line[45],
                            'escritorio_razao_social': line[46],
                            'escritorio_cnpj_cpf': self.format_number(line[47]),
                            'escritorio_phone': self.format_number(line[48]),
                            'escritorio_email': line[49],
                            'escritorio_is_escritorio': self.format_boolean(line[50]),
                            'escritorio_is_company': self.format_boolean(line[51]),
                            'escritorio_street': line[52],
                            'escritorio_number': line[53],
                            'escritorio_street2': line[54],
                            'escritorio_district': line[55],
                            'escritorio_city': line[56],
                            'escritorio_state': line[57],
                            'escritorio_country': line[58],
                            'assuncao_defesa': line[59],
                            'valor_causa': line[60],
                            'valor_dano_moral': line[61],
                            'valor_dano_material': line[62],
                            'data_distribuicao': self.format_date(line[63], wb),
                            'rito': line[64],
                            'ordinal': line[65],
                            'vara': line[66],
                            'orgao': line[67],
                            'comarca': line[68],
                            'estado': line[69],
                            'natureza': line[70],
                            'tipo_acao': line[71],
                            'projeto': line[72],
                            'credenciado': line[73],
                            'credenciado_razao_social': line[74],
                            'credenciado_cnpj_cpf': self.format_number(line[75]),
                            'credenciado_phone': self.format_number(line[76]),
                            'credenciado_email': line[77],
                            'credenciado_is_credenciado': self.format_boolean(line[78]),
                            'credenciado_is_company': self.format_boolean(line[79]),
                            'objeto': line[80],
                            'assunto': line[81],
                            'local_fato': line[82],
                            'data_fato': self.format_date(line[83], wb),
                            'parecer': line[84],
                            'subsidio': line[85],
                            'analise_acordo': line[86],
                            'motivo_inaptidao': line[87],
                            'valor_alcada': self.format_number(line[88]),
                            'contrato': line[89],
                            'carteira_id': line[90],
                            'responsabilidade': line[91],
                            'risco': line[92],
                            'obrigacao': line[93],
                            'liminar': line[94],
                            'data_audiencia_inicial': self.format_date(line[95], wb),
                            'tem_advogado': line[96],
                            'import_excel_id': imp.id,
                            'grupo': line[97]
                        }
                        excel_line = excel_line_obj.create(row_line)
                    # Parte Representada cols 07 to 21

                    if line[7]:
                        parte_representada_vals = {
                            'excel_line_id': excel_line.id,
                            'name': line[7],
                            'legal_name': line[8],
                            'cnpj_cpf': self.format_number(line[9]),
                            'phone': self.format_number(line[10]),
                            'mobile': self.format_number(line[11]),
                            'email': line[12],
                            'is_parte_representada': self.format_boolean(line[13]),
                            'is_company': self.format_boolean(line[14]),
                            'street': line[16],
                            'number': line[17],
                            'street2': line[18],
                            'district': line[19],
                            'city': line[20],
                            'state': line[21],
                            'country': line[22],
                        }
                        parte_representada_obj.create(parte_representada_vals)

                    # Parte Contraria cols 23 to 35
                    if line[23]:
                        parte_contraria_vals = {
                            'excel_line_id': excel_line.id,
                            'name': line[23],
                            'cnpj_cpf': self.format_number(line[24]),
                            'phone': self.format_number(line[25]),
                            'mobile': self.format_number(line[26]),
                            'email': self.format_number(line[27]),
                            'is_parte_contraria': self.format_boolean(line[28]),
                            'company_type': 'company' if self.format_boolean(line[29]) else 'person',
                            'is_company': self.format_boolean(line[29]),
                            'street': line[30],
                            'number': line[31],
                            'street2': line[32],
                            'district': line[33],
                            'city': line[34],
                            'state': line[35],
                            'country': line[36],
                        }
                        parte_contraria_obj.create(parte_contraria_vals)

                    # Advogado Adverso cols 37 to 44

                    if line[37]:
                        advogado_adverso_vals = {
                            'excel_line_id': excel_line.id,
                            'name': line[37],
                            'cnpj_cpf': self.format_number(line[38]),
                            'oab': line[39],
                            'mobile': self.format_number(line[40]),
                            'email': line[41],
                            'is_advogado': self.format_boolean(line[42]),
                            'is_company': self.format_boolean(line[43]),
                            'parent_id': line[44]
                        }

                        advogado_adverso_obj.create(advogado_adverso_vals)

                imp.write({'state': 'loaded',
                           'num_lines': num_lines,
                           'limit': num_lines})
        return True

    def import_spreadsheet_line_thread(self, semaphores, queue):
        #  Methods to get values
        def validate_dossie(dossie, processo):
            if not dossie or not dossie.strip():
                return True
            if dossie or processo:
                dossie = self.env['dossie.dossie'].search([('name', '=', dossie)])
                if not len(dossie) and processo:
                    dossie = self.env['dossie.dossie'].search([('processo', '=', processo)])
                if len(dossie):
                    return False
            return True

        # Get key from selection fields
        # eg: state, Tipo Processo
        def get_selection_key(selection_vals, key, warn_label):
            """
            selection_vals : domain for slection field
            key : Selection Label
            warn_label : warning word if key not found
            """
            if not key:
                return False
            vals = dict(selection_vals)
            if not key in vals.values():
                raise Warning(u"%s not found for %s" % (warn_label, key))
            return vals.keys()[vals.values().index(key)]

        # Dossie Fase
        def get_fase(name):
            if not name:
                return False
            fase = self.env['dossie.fase'].search([('name', '=', name)])
            if not len(fase):
                raise Warning(u"Fase %s not found" % name)
            if len(fase) > 1:
                raise Warning(u"Multiple fase found with name %s" % name)
            return fase.id

        # Dossie Origem
        def get_origem(name):
            if not name:
                return False
            origem = self.env['dossie.origem'].search([('name', '=', name)])
            if not len(origem):
                raise Warning(u"Origem %s not found" % name)
            if len(origem) > 1:
                raise Warning(u"Multiple origem found with name %s" % name)
            return origem.id

        # Grupo
        def get_grupo(name):
            if not name:
                return False
            grupo = self.env['res.partner'].search([('name', '=', name),('is_grupo','=',True)])
            if not len(grupo):
                raise Warning(u"Grupo %s not found" % name)
            if len(grupo) > 1:
                raise Warning(u"Multiple grupo found with name %s" % name)
            return grupo.id

        # Get recor id with model and name
        def get_record_id(model, name):
            if not name:
                return False
            records = self.env[model].search([('name', '=ilike', name)])
            if not len(records):
                raise Warning(u"Record : %s not found" % name)
            if len(records) > 1:
                raise Warning(u"Duplicate record found for model %s with name %s" % (model, name))
            return records.id

        def get_escritorio(cnpj_cpf, name, line):
            if not name:
                return False
            escritorio = []
            if cnpj_cpf:
                is_company, cnpj_cpf = self.format_cnpj_cpf(cnpj_cpf)
                escritorio = self.env['res.partner'].search([('cnpj_cpf', '=', cnpj_cpf)])
            if not len(escritorio):
                escritorio = self.env['res.partner'].search([('name', '=', name)])
                if not len(escritorio):
                    if self.create_escritorio:
                        country_id = get_record_id('res.country', line.escritorio_country)
                        state_id = False
                        city_id = False
                        if country_id:
                            country = self.env['res.country'].browse(country_id)
                            state_id = self.get_uf(line.escritorio_state, country.code)
                            if state_id:
                                city_id = self.get_comarca_id(line.escritorio_city, state_id)
                        escritorio = self.env['res.partner'].create({
                            'name': name,
                            'legal_name': line.escritorio_razao_social,
                            'cnpj_cpf': cnpj_cpf,
                            'customer': False,
                            'is_company': True,
                            'phone': line.escritorio_phone,
                            'email': line.escritorio_email,
                            'street': line.escritorio_street,
                            'number': line.escritorio_number,
                            'street2': line.escritorio_street2,
                            'district': line.escritorio_district,
                            'city_id': city_id,
                            'state_id': state_id,
                            'country_id': country_id,
                            'is_escritorio': True,
                        })
                    else:
                        raise Warning(u"Escritorio %s not found" % name)
            return escritorio[0].id

        def get_credenciado(cnpj_cpf, name, line):
            credenciado = []
            if cnpj_cpf:
                is_company, cnpj_cpf = self.format_cnpj_cpf(cnpj_cpf)
                credenciado = self.env['res.partner'].search([('cnpj_cpf', '=', cnpj_cpf)])
            if not len(credenciado) and name:
                credenciado = self.env['res.partner'].search([('name', '=', name)])
                if not len(credenciado):
                    if self.create_credenciado:
                        escritorio = self.env['res.partner'].create({
                            'name': line.credenciado,
                            'legal_name': line.credenciado_razao_social,
                            'cnpj_cpf': cnpj_cpf or False,
                            'phone': line.credenciado_phone,
                            'email': line.credenciado_email,
                            'is_credenciado': True,
                            'is_company': line.credenciado_is_company,
                        })
                    else:
                        raise Warning(u"Credenciado %s not found" % name)
            if len(credenciado):
                return credenciado[0].id
            return False

        def get_projeto(name):
            projeto = self.env['project.project'].search([('name', '=ilike', name)])
            if not len(projeto):
                raise Warning(u"Projeto %s not found" % name)
            if len(projeto) > 1:
                raise Warning(u"Multiple projects found for %s" % name)
            return projeto[0].id

        global num_errors
        global imported_lines
        global imported_lines_error
        update_import = {}
        while not queue.empty():
            with semaphores:
                with threading.Lock():
                    with api.Environment.manage():
                        with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                            self = self.with_env(self.env(cr=new_cr))
                            line = self.env['import.dossie.excel.line'].browse(queue.get())
                            line_objs = self.env['import.dossie.excel.line']
                            dossie_obj = self.env['dossie.dossie']
                            # line = queue.get()
                            # do the import line stuff process
                            err = ''
                            try:
                                for record in line.parte_representada_ids:
                                    try:
                                        partner_id = self.get_partner(record)
                                        record.partner_id = partner_id
                                    except Exception, err:
                                        raise Warning(u"ERRO Parte Representada :\n%s" % err[0])

                                for record in line.parte_contraria_ids:
                                    try:
                                        partner_id = self.get_partner(record)
                                        record.partner_id = partner_id
                                    except Exception, err:
                                        raise Warning(u"ERRO Parte Contraria :\n%s" % err[0])

                                for record in line.advogado_adverso_ids:
                                    try:
                                        partner_id = self.get_advogado(record)
                                        record.partner_id = partner_id
                                    except Exception, err:
                                        raise Warning(u"ERRO Advogado Adverso :\n%s" % err[0])
                                try:
                                    if line.dossie or line.processo:
                                        # import only non-existing dossie
                                        # idenfity for dossie and processo
                                        dossie = validate_dossie(line.dossie, line.processo)

                                        if not dossie:
                                            line.write({
                                                'state': 'imported',
                                                'importation_error': u'Dossie ja existe!',
                                            })
                                            continue


                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Dossie:\n%s" % err[0])
                                try:
                                    estado_id = self.get_uf(line.estado)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO UF:\n%s" % err[0])
                                try:
                                    comarca_id = self.get_comarca_id(line.comarca, estado_id)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Comarca:\n%s" % err[0])
                                try:
                                    natureza_id = get_record_id('dossie.natureza', line.natureza)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Natureza:\n%s" % err[0])
                                try:
                                    rito_id = get_record_id('dossie.rito', line.rito)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Rito:\n%s" % err[0])
                                try:
                                    ordinal = line.ordinal and int(float(line.ordinal))
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Ordinal:\n%s" % u'Ordinal must be an integer')
                                try:
                                    vara_id = get_record_id('dossie.vara', line.vara)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Vara:\n%s" % err[0])
                                try:
                                    tipo_acao_id = get_record_id('dossie.tipo.acao', line.tipo_acao)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Tipo de Ação:\n%s" % err[0])
                                try:
                                    projeto_id = get_record_id('project.project', line.projeto)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Projeto:\n%s" % err[0])
                                try:
                                    objeto_id = get_record_id('dossie.objeto', line.objeto)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Objeto:\n%s" % err[0])
                                try:
                                    assunto_id = get_record_id('dossie.assunto', line.assunto)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Assunto:\n%s" % err[0])
                                try:
                                    motivo_inaptidao = get_record_id('motivo.inaptidao', line.motivo_inaptidao)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Motivo da Inaptidao:\n%s" % err[0])
                                try:
                                    orgao_id = get_record_id('dossie.orgao', line.orgao)
                                except Exception, err:
                                    raise Warning(u"ERRO INSERINDO Orgão:\n%s" % err[0])

                                try:
                                    dossie = dossie_obj.create({'name': line.dossie,
                                                                'processo': line.processo,
                                                                'state': get_selection_key(dossie_state,
                                                                                           line.dossie_state,
                                                                                           u'State'),
                                                                'polo_cliente': get_selection_key(polo_cliente_vals,
                                                                                                  line.polo_cliente,
                                                                                                  u'Polo Cliente'),
                                                                'fase_id': get_fase(line.fase),
                                                                'origem_id': get_origem(line.origem),
                                                                'tipo_processo': get_selection_key(tipo_processo_vals,
                                                                                                   line.tipo_processo,
                                                                                                   u'Tipo do Processo'),
                                                                'assuncao_defesa': get_selection_key(
                                                                    assuncao_defesa_vals,
                                                                    line.assuncao_defesa,
                                                                    u' Assunção de Defesa'),
                                                                'valor_causa': line.valor_causa,
                                                                'valor_dano_moral': line.valor_dano_moral,
                                                                'valor_dano_material': line.valor_dano_material,
                                                                'data_distribuicao': line.data_distribuicao,
                                                                'rito_id': rito_id,
                                                                'ordinal': ordinal,
                                                                'vara_id': vara_id,
                                                                'orgao_id': orgao_id,
                                                                'comarca_id': comarca_id,
                                                                'estado_id': estado_id,
                                                                'natureza_id': natureza_id,
                                                                'tipo_acao_id': tipo_acao_id,
                                                                'projeto_id': projeto_id,
                                                                'credenciado_id': get_credenciado(
                                                                    line.credenciado_cnpj_cpf,
                                                                    line.credenciado, line),
                                                                'objeto_id': objeto_id,
                                                                'assunto_id': assunto_id,
                                                                'local_fato': line.local_fato,
                                                                'data_fato': line.data_fato,
                                                                'parecer': get_selection_key(parecer_vals, line.parecer,
                                                                                             u'Parecer'),
                                                                'subsidio': line.subsidio,
                                                                'analise_acordo': get_selection_key(analise_acordo_vals,
                                                                                                    line.analise_acordo,
                                                                                                    u'Analise de Acordo'),
                                                                'motivo_inaptidao': motivo_inaptidao,
                                                                'valor_alcada': line.valor_alcada,
                                                                'responsabilidade': get_selection_key(
                                                                    responsabilidade_vals,
                                                                    line.responsabilidade,
                                                                    u'Responsabilidade'),
                                                                'risco': get_selection_key(risco_vals, line.risco,
                                                                                           u'Risco'),
                                                                'obrigacao': line.obrigacao,
                                                                'liminar': line.liminar,
                                                                'data_audiencia_inicial': line.data_audiencia_inicial,

                                                                'escritorio_id': get_escritorio(cnpj_cpf=False,
                                                                                                name=False,
                                                                                                line=line),
                                                                'parte_representada_ids': [
                                                                    (6, 0,
                                                                     line.parte_representada_ids.mapped(
                                                                         'partner_id').ids)],
                                                                'parte_contraria_ids': [
                                                                    (6, 0, line.parte_contraria_ids.mapped(
                                                                        'partner_id').ids)],
                                                                'advogado_adverso_ids': [
                                                                    (6, 0, line.advogado_adverso_ids.mapped(
                                                                        'partner_id').ids)],
                                                                'tem_advogado': get_selection_key(
                                                                    boolean_selection_vals,
                                                                    line.tem_advogado,
                                                                    u'Tem Advogado'),
                                                                'grupo_id':get_grupo(line.grupo)
                                                                # 'import_excel_id': import_obj.id
                                                                })
                                    _logger.info("Imported Dossie %s" % dossie)

                                except Exception, err:
                                    _logger.info("EXCEPTION on import %s" % err[0])
                                    raise Warning(u"ERRO INSERINDO DOSSIÊ:\n%s" % err[0])
                            except Exception, err:
                                if line.state == 'new':
                                    imported_lines_error += 1
                                try:
                                    error_msg = err[0]
                                    _logger.info("EXCEPTION on import %s" % err[0])
                                except:
                                    error_msg = err
                                    _logger.info("EXCEPTION on import %s" % err)
                                line.write(
                                    {'state': 'error',
                                     'importation_error': error_msg,
                                     'importation_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                     })
                                num_errors += 1
                            if err == '':
                                #TODO unable to write dossie_id here
                                # probably because of new cursor
                                line.write(
                                    {'state': 'imported',
                                     #'dossie_id': dossie.id,
                                     'importation_error': '',
                                     'importation_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                     })
                            new_cr.commit()
                    queue.task_done()
        return True

    def import_spreadsheet(self):
        # if IMPORT_SPREADSHEET_N_THREADS system parameter is defined
        # use it
        # else use ncpus()
        nthreads = ncpus() * 5
        semaphore_pool = threading.BoundedSemaphore(nthreads)
        import_queue = Queue(maxsize=0)

        line_objs = self.env['import.dossie.excel.line']
        dossie_obj = self.env['dossie.dossie']
        for import_obj in self:
            global update_import
            global num_errors  # global might be syntax optional
            global imported_lines
            global imported_lines_error
            t1 = time.time()
            num_errors = 0
            imported_lines = import_obj.imported_lines
            imported_lines_error = import_obj.imported_lines_error
            line_obj_ids = line_objs.search(
                [('import_excel_id', '=', import_obj.id), ('state', 'in', ('new', 'error'))],
                limit=import_obj.limit
            )

            for line in line_obj_ids:
                import_queue.put(line.id)

            # if IMPORT_SPREADSHEET_N_THREADS system parameter is defined
            # use it
            # else use ncpu()
            for i in range(nthreads):
                t = threading.Thread( \
                    target=self.import_spreadsheet_line_thread,
                    name=u'spreadsheet_line_import_' + str(
                        i),
                    args=(semaphore_pool, import_queue))
                # setting threads as "daemon" allows main program to
                # exit eventually even if these dont finish
                # correctly.
                t.setDaemon(True)
                t.start()

            import_queue.join()

            noOfErrors = len(self.import_line_ids.filtered(lambda t: t.state == 'error'))
            noOfImported = len(self.import_line_ids.filtered(lambda t: t.state == 'imported'))
            self.write({'imported_lines_error':noOfErrors,
                        'imported_lines': noOfImported,
                        })
            msg = "It took %s Sec in process %s records " % (time.time() - t1, self.limit)
            self.message_post(body=msg)
        return True


class ExcelAdvogadoAdverso(models.Model):
    _name = 'excel.advogado.adverso'

    name = fields.Char(u'Name')
    cnpj_cpf = fields.Char(u'CNPJ')
    oab = fields.Char(u'OAB')
    empresa = fields.Char(u'Empresa')
    email = fields.Char(u'Email')
    phone = fields.Char(u'Telefone')
    mobile = fields.Char(u'Mobile')
    is_advogado = fields.Boolean(u'É Advogado', default=True)
    is_company = fields.Boolean(u'É Empresa', default=True)
    company_type = fields.Selection([('company', 'Company'), ('person', u'Person')], default='person',
                                    string=u'Física ou Jurídica')
    partner_id = fields.Many2one('res.partner', u'Advogado Adverso')
    excel_line_id = fields.Many2one('import.dossie.excel.line', 'Excel Line')


class ParteRepresentada(models.Model):
    _name = 'excel.parte.representada'

    name = fields.Char(u'Name')
    razao_social = fields.Char(u'Razão Social')
    cnpj_cpf = fields.Char(u'CNPJ')
    empresa = fields.Char(u'Empresa')
    email = fields.Char(u'Email')
    phone = fields.Char(u'Telefone')
    mobile = fields.Char(u'Mobile')
    street = fields.Char(u'Rua')
    street2 = fields.Char(u'Complemento')
    district = fields.Char(u'Bairro')
    city = fields.Char(u'Cidade')
    state = fields.Char(u'UF')
    country = fields.Char(u'País')
    number = fields.Char(u'Nº')
    is_company = fields.Boolean(u'É Empresa')
    is_parte_representada = fields.Boolean(u'É Parte Representada')
    is_parte_contraria = fields.Boolean(u'É Parte Contrária')
    company_type = fields.Selection([('company', 'Company'), ('person', u'Person')], default='person',
                                    string=u'Física ou Jurídica')
    partner_id = fields.Many2one('res.partner', u'Parte Representada')
    excel_line_id = fields.Many2one('import.dossie.excel.line', 'Excel Line')


class ParteContraria(models.Model):
    _name = 'excel.parte.contraria'

    name = fields.Char(u'Name')
    razao_social = fields.Char(u'Razão Social')
    cnpj_cpf = fields.Char(u'CNPJ')
    empresa = fields.Char(u'Empresa')
    email = fields.Char(u'Email')
    phone = fields.Char(u'Telefone')
    mobile = fields.Char(u'Mobile')
    street = fields.Char(u'Rua')
    street2 = fields.Char(u'Complemento')
    district = fields.Char(u'Bairro')
    city = fields.Char(u'Cidade')
    is_parte_contraria = fields.Boolean(u'É Parte Contrária')
    is_parte_representada = fields.Boolean(u'É Parte Representada')
    is_company = fields.Boolean(u'É Empresa')
    state = fields.Char(u'UF')
    country = fields.Char(u'País')
    number = fields.Char(u'Nº')
    partner_id = fields.Many2one('res.partner', u'Parte Contraria')
    company_type = fields.Selection([('company', 'Company'), ('person', u'Person')], default='person',
                                    string=u'Física ou Jurídica')
    excel_line_id = fields.Many2one('import.dossie.excel.line', 'Excel Line')

class import_dossie_excel_line(models.Model):
    _name = 'import.dossie.excel.line'
    _description = 'Import dossie Excel Line'

    import_excel_id = fields.Many2one(
        'import.dossie.excel', 'Import Excel ID',
        ondelete='cascade',
        readonly=True)
    state = fields.Selection([
        ('new', _('Novo')),
        ('imported', _('Importado')),
        ('error', _('Erro')), ], 'Estado',
        default='new',
        readonly=True,
        required=True)
    num_line = fields.Integer(u'Número de Linha',
                              readonly=True)
    importation_date = fields.Datetime(u'Data Importação',
                                       default=lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
                                       readonly=True,
                                       required=True)
    importation_error = fields.Text(u'Erro Importação',
                                    readonly=True)
    dossie_id = fields.Many2one('dossie.dossie', u'Dossie')
    dossie = fields.Char(u'Dossie')
    processo = fields.Char(u'Processo')
    dossie_state = fields.Char(u'State')
    polo_cliente = fields.Char(u'Polo Cliente')
    fase = fields.Char(u'Fase Atual')
    origem = fields.Char(u'Origem')
    tipo_processo = fields.Char(u'Tipo do Processo')
    groupo = fields.Char(u'Projeto')
    escritorio = fields.Char(u'Escritório')
    escritorio_razao_social = fields.Char(u'Escritório / Razão Social')
    escritorio_cnpj_cpf = fields.Char(u'Escritório / CNPJ')
    escritorio_phone = fields.Char(u'Escritório / Phone')
    escritorio_email = fields.Char(u'Escritório / Email')
    escritorio_is_escritorio = fields.Boolean(u'Escritório / É Escritório')
    escritorio_is_company = fields.Boolean(u'Escritório / É Empresa')
    escritorio_street = fields.Char(u'Escritório / Rua')
    escritorio_number = fields.Char(u'Escritório / Nº')
    escritorio_street2 = fields.Char(u'Escritório / Complemento')
    escritorio_district = fields.Char(u'Escritório / Bairro')
    escritorio_city = fields.Char(u'Escritório / Cidade')
    escritorio_state = fields.Char(u'Escritório / UF')
    escritorio_country = fields.Char(u'Escritório / País')
    credenciado = fields.Char(u'Credenciado')
    credenciado_razao_social = fields.Char(u'Credenciado / Razão Social')
    credenciado_cnpj_cpf = fields.Char(u'Credenciado / CNPJ')
    credenciado_phone = fields.Char(u'Credenciado / Telefone')
    credenciado_email = fields.Char(u'Credenciado / Email')
    credenciado_is_credenciado = fields.Boolean(u'Credenciado / É Credenciado')
    credenciado_is_company = fields.Boolean(u'Credenciado / É Empresa')
    assuncao_defesa = fields.Char(u'Assunção de Defesa')
    valor_causa = fields.Char(u'Valor da Causa')
    valor_dano_moral = fields.Char(u'Valor do Dano Moral')
    valor_dano_material = fields.Char(u'Valor do Dano Material')
    data_distribuicao = fields.Date(u'Data da Distribuição')
    data_audiencia_inicial = fields.Datetime(u'Data Audiencia Inicial')
    rito = fields.Char(u'Rito')
    ordinal = fields.Char(u'Nº Ordinal')
    vara = fields.Char(u'Vara')
    orgao = fields.Char(u'Orgão')
    comarca = fields.Char(u'Comarca')
    estado = fields.Char(u'UF')
    natureza = fields.Char(u'Natureza')
    tipo_acao = fields.Char(u'Tipo da Ação')
    projeto = fields.Char(u'Projeto')
    objeto = fields.Char(u'Objeto')
    assunto = fields.Char(u'Assunto')
    local_fato = fields.Char(u'Local do Fato')
    data_fato = fields.Date(u'Data do Fato')
    parecer = fields.Char(u'Parecer')
    subsidio = fields.Char(u'Subsidio')
    analise_acordo = fields.Char(u'Análise Acordo')
    motivo_inaptidao = fields.Char(u'Motivo de Inaptidão')
    valor_alcada = fields.Char(u'Valor da Alçada')
    contrato = fields.Char(u'Contrato')
    carteira = fields.Char(u'Carteira')
    responsabilidade = fields.Char(u'Responsabilidade')
    risco = fields.Char(u'Risco')
    obrigacao = fields.Char(u'Obrigação de Fazer')
    liminar = fields.Char(u'Liminar')
    tem_advogado = fields.Char(string=u'Tem Advogado')
    grupo = fields.Char(string=u'Grupo')
    parte_representada_ids = fields.One2many('excel.parte.representada', 'excel_line_id', u'Parte Representada')
    parte_contraria_ids = fields.One2many('excel.parte.contraria', 'excel_line_id', u'Parte Contrária')
    advogado_adverso_ids = fields.One2many('excel.advogado.adverso', 'excel_line_id', u'Advogado Adverso')
