# -*-coding:utf-8-*-
from odoo import fields, models, api, _
import threading
import ast

dossie_honorario_estado_vals = [('n', u'Novo'), ('s', u'Solicitado'),
                                ('a', u'Aprovado'), ('r', u'Rejeitado'), ('e', u'Emitido'),
                                ('r', u'Recebido')]


class DossieDossie(models.Model):
    _inherit = 'dossie.dossie'

    honorario_ids = fields.One2many('dossie.honorario', 'dossie_id', string=u'Honorários')


class DossieHonorario(models.Model):
    _name = 'dossie.honorario'
    _description = u'Honorário'

    name = fields.Char(string=u'Código')
    dossie_id = fields.Many2one('dossie.dossie', string=u'Dossiê')
    tipo_id = fields.Many2one('dossie.honorario.tipo', string=u'Tipo')
    valor = fields.Monetary(string=u'Valor', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    estado = fields.Selection(string=u'Estado', selection=dossie_honorario_estado_vals)
    honorario_lote_id = fields.Many2one('dossie.honorario.lote', string=u'Lote')


    def calcula_honorarios(self,vals):
        if self.dossie_id:
            dossie_id = self.dossie_id
        else:
            dossie_id = self.env['dossie.dossie'].search([('id','=',vals.get('dossie_id'))])

        tipo_id = None
        if dossie_id:
            # Busca todos os tipos de dossiê cadastrados
            # (dossie.honorario.tipo.campo) em um tipo (dossie.honorario.tipo)
            lista_tipos = self.env['dossie.honorario.tipo'].search([])

            # Variavel de controle com as pontuações carregadas para cada lista de campos 
            tipos_validos = []
            
            tipo_score = 0
            cmd_aux = ""
            aux_var = None
            for tipo in lista_tipos:
                tipo_score = 0
                for domain in ast.literal_eval(tipo.domain):
                    # Atribui valor do campo a variavel aux_var
                    cmd_aux = 'dossie_id.' + domain[0]
                    conteudo = domain[2]

                    try:
                        aux_var = eval(cmd_aux)
                    except:
                        print "error on eval function execution %s" %cmd_aux
                    else:
                        # Referencia deixada para a possibilidade de habilitar outros tipos de campo
                        campo_id = self.env['ir.model.fields'].search([('model','=','dossie.dossie'), ('name','=',domain[0])], limit=1)

                        if campo_id.ttype == 'many2one':
                            if aux_var.name.upper() == conteudo.upper():
                                tipo_score += 1
                        elif campo_id.ttype == 'monetary' or campo_id.ttype == 'float' or campo_id.ttype == 'integer':
                            if aux_var == float(conteudo.replace(',','.')):
                                tipo_score += 1
                        elif campo_id.ttype == 'bolean':
                            if conteudo.upper() == 'TRUE' or conteudo.upper() == 'T' or conteudo.upper() == 'VERDADEIRO' or conteudo.upper() == 'V':
                                if aux_var == True:
                                    tipo_score += 1
                            elif conteudo.upper() == 'FALSE' or conteudo.upper() == 'FALSO' or conteudo.upper() == 'F':
                                if aux_var == False:
                                    tipo_score += 1
                        else: #campos armazenam strings
                            if aux_var.upper() == conteudo.upper():
                                tipo_score += 1
                
                if tipo_score > 0:
                    tipos_validos.append((tipo.id,tipo_score))
                    
            # Grava o id do dossie.honorario.tipo que tem o score máximo no campo tipo_id 
            if len(tipos_validos) > 0:
                max_score = sorted(tipos_validos, key=lambda x:(-x[1],x[0]))[0]
                tipo_id = self.env['dossie.honorario.tipo'].search([('id','=',max_score[0])])
                vals['tipo_id'] = max_score[0]
                valor_total = 0.0
                valor_variavel = 0.0
                if tipo_id.codigo_python:
                    try:

                        method_ret = eval(tipo_id.codigo_python)
                        valor_variavel = method_ret
                    except SyntaxError:
                        pass
                if valor_variavel:
                    valor_total = tipo_id.valor_fixo + valor_variavel
                else:
                    valor_total = tipo_id.valor_fixo
                vals['valor'] = valor_total
                vals['name'] = ('%s | %s | %f' % (dossie_id.name,tipo_id.name,round(valor_total,2)))
        return vals



    @api.model
    def create(self, vals):
        vals = self.calcula_honorarios(vals)

        return super(DossieHonorario, self).create(vals)


    @api.multi
    def write(self, vals):
        vals = self.calcula_honorarios(vals)
        return super(DossieHonorario, self).write(vals)



class DossieHonorarioTipo(models.Model):
    _name = 'dossie.honorario.tipo'
    _description = u'Tipo de Honorário'


    name = fields.Char(string=u'Nome')

    currency_id = fields.Many2one('res.currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)

    valor_fixo = fields.Monetary(string=u'Valor Fixo', currency_field='currency_id',required=True)

    # Código usado para ser calculado no dossie.honorario no momento da seleção do dossiê associado e/ou do honorario.tipo
    codigo_python = fields.Text(string=u'Regra do Valor Variável')

    domain  = fields.Text(string='Domain', default='[]')


class DossieHonorarioLote(models.Model):
    _name = 'dossie.honorario.lote'
    _description = u'Lote de Honorários'

    valor = fields.Monetary(string=u'Valor', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    estado = fields.Selection(string=u'Estado', selection=dossie_honorario_estado_vals)
    honorario_ids = fields.One2many('dossie.honorario', 'honorario_lote_id', string=u'Honorários')


class DossieHonorarioTipoCampo(models.Model):
    _name = 'dossie.honorario.tipo.campo'
    _description = u'Campos de Tipo de Honorários'
    _order = 'tipo_id, sequence, id'


    name = fields.Char(string=u'Descrição')

    sequence = fields.Integer(string=u'Sequence', default=10, index=True)

    tipo_id = fields.Many2one('dossie.honorario.tipo', string=u'Meta', required=True, ondelete='cascade', index=True, copy=False)

    campo_id = fields.Many2one('ir.model.fields',string=u'Campo',required=True,domain=[('model','=','dossie.dossie')])
 
    conteudo = fields.Char(string=u'Conteúdo')





