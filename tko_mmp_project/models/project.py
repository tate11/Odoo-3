# -*-coding:utf-8-*-
from odoo import models, fields, api
from dossie import tipo_processo_vals, parecer_vals, responsabilidade_vals, dossie_state, multa_selection_vals
from dossie import assuncao_defesa_vals, risco_vals, polo_cliente_vals, analise_acordo_vals, boolean_selection_vals
from lxml import etree
from odoo.osv.orm import setup_modifiers

class task_type(models.Model):
    _inherit = 'task.type'

    field_ids = fields.Many2many(
        comodel_name='ir.model.fields', 
        relation='task_type_fields_rel', 
        column1='fields_id', 
        column2='type_id', 
        string=u'Fields',
        domain=[('dynamic_view_field', '=', True), ('model', 'in', ['project.task', 'project.task.default.line'])])


class MotivoCancelamento(models.Model):
    _name = 'motivo.cancelamento'
    _description = u'Motivo de Cancelamento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoOficio(models.Model):
    _name = 'tipo.oficio'
    _description = u'Tipo de Ofício'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class AreaOficio(models.Model):
    _name = 'area.oficio'
    _description = u'Área do Oficio'

    name = fields.Char(
        string=u'Nome', 
        required=True)

class FormaPagamento(models.Model):
    _name = 'forma.pagamento'
    _description = u'Forma de Pagamento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossie', 
        ondelete='cascade')
    fase_tarefa_id = fields.Many2one(
        comodel_name='dossie.fase', 
        string=u'Fase Tarefa')
    movimentacao_id = fields.Many2one(
        comodel_name='dossie.movimentacao',
        readonly=True,
        string=u'Movimentação')
    movimentacao = fields.Text(
        string=u'Conteúdo da Movimentação', 
        store=True, 
        readonly=True, 
        related='movimentacao_id.movimentacao')
    currency_id = fields.Many2one(
        store=True,
        related='dossie_id.currency_id')
    


    ########## DYNAMIC FIELDS ##########



    guia = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Guia', 
        dynamic_view_field=True)
    guia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Guia')

    guia_paga = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Guia Paga', 
        dynamic_view_field=True)
    guia_paga_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Guia Paga')
    
    comprovante_protocolo = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Comprovante do Protocolo',
        dynamic_view_field=True)
    comprovante_protocolo_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Comprovante do Protocolo')

    comprovante_pagamento = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Comprovante do Pagamento',
        dynamic_view_field=True)
    comprovante_pagamento_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Comprovante do Pagamento')
    
    documento_juntada = fields.Many2many(
        comodel_name='ir.attachment', 
        relation='task_attachment_doc_rel', 
        column1='task_id', 
        column2='attachment_id',
        string=u'Documentos para Juntada', 
        dynamic_view_field=True)
    documento_juntada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Documentos para Juntada')

    guias_preparo = fields.Many2many(
        comodel_name='ir.attachment', 
        relation='task_attachment_guias_rel', 
        column1='task_id', 
        column2='attachment_id',
        string=u'Guias das Custas', 
        dynamic_view_field=True)
    guias_preparo_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Guias das Custas')

    tem_preparo = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Custas?', 
        dynamic_view_field=True)
    tem_preparo_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Custas')

    lote = fields.Char(
        string=u'Nº Lote', 
        dynamic_view_field=True)
    lote_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Lote')

    data_audiencia = fields.Datetime(
        string=u'Data da Audiência', 
        dynamic_view_field=True)
    data_audiencia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data da Audiência')

    presentes_audiencia = fields.Selection(
        string=u'Quem deverá comparecer?',
        selection=[
            ('a', u'Advogado'), 
            ('p', u'Preposto'), 
            ('ap', u'Advogado e Preposto')], 
        dynamic_view_field=True)
    presentes_audiencia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Quem deverá comparecer?')

    correspondente_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Correspondente', 
        dynamic_view_field=True)
    correspondente_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Correspondente')
    valid_correspondente_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='valid_correspondente_rel', 
        column1='task_id', 
        column2='partner_id',
        string=u'Valid Correspondente for domain', 
        compute='get_valid_correspondente')

    valor_correspondente = fields.Monetary(
        string=u'Valor do Correspondente',
        currency_field='currency_id',
        dynamic_view_field=True)
    valor_correspondente_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Valor do Correspondente')
    valor_correspondente_media = fields.Monetary(
        string=u'Média Valor do Correspondente',
        related='valor_correspondente', 
        group_operator='avg', 
        readonly=True, 
        store=True)

    advogado_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Advogado', 
        dynamic_view_field=True)
    advogado_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Advogado')

    preposto_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Preposto', 
        dynamic_view_field=True)
    preposto_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Preposto')

    ata = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Ata da Audiência',
        dynamic_view_field=True)
    ata_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Ata')

    motivo_infrutividade = fields.Selection(
        string=u'Motivo da Infrutividade',
        selection=[
            ('c', u'Contraproposta'), 
            ('si', u'Sem Interesse')],
        dynamic_view_field=True)
    motivo_infrutividade_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Motivo da Infrutividade')
    
    tipo_pagamento = fields.Many2one(
        comodel_name='tipo.pagamento', 
        string=u'Tipo de Pagamento',
        dynamic_view_field=True)
    tipo_pagamento_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tipo de Pagamento')

    tipo_acordo = fields.Selection(
        string=u'Tipo de Acordo',
        selection=[
            ('p', u'Pagamento'),
            ('o', u'Obrigação'),
            ('po', u'Pagamento e Obrigação')],
        dynamic_view_field=True)
    tipo_acordo_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tipo de Acordo')

    obrigacao = fields.Text(
        string=u'Obrigação', 
        dynamic_view_field=True)
    obrigacao_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Obrigação')

    estado_sentenca = fields.Selection(
        selection=[
            ('s', u'Proferida'), 
            ('as', u'Aguardando Leitura'), 
            ('np', u'Não Proferida')],
        string=u'Estado da Sentença',
        dynamic_view_field=True)
    estado_sentenca_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Estado da Sentença')

    forma_pagamento_id = fields.Many2one(
        comodel_name='forma.pagamento',
        string=u'Forma do Pagamento', 
        dynamic_view_field=True)
    forma_pagamento_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Forma do Pagamento')

    relatorio_pagamento = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Relatório de Pagamento', 
        dynamic_view_field=True)
    relatorio_pagamento_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Relatório de Pagamento')

    peticao = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Petição', 
        dynamic_view_field=True)
    peticao_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Petição')

    tipo_transito_id = fields.Many2one(
        comodel_name='tipo.transito', 
        string=u'Tipo de Transito', 
        dynamic_view_field=True)
    tipo_transito_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tipo de Transito')

    tipo_prazo_id = fields.Many2one(
        comodel_name='tipo.prazo', 
        string=u'Tipo de Prazo', 
        dynamic_view_field=True)
    tipo_prazo_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tipo de Prazo')

    copias = fields.Many2many(
        comodel_name='ir.attachment', 
        relation='task_copias_rel', 
        column1='task_id', 
        column2='attachment_id',
        string=u'Cópias', 
        dynamic_view_field=True)
    copias_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Cópias')

    tipo_recurso_id = fields.Many2one(
        comodel_name='tipo.recurso', 
        string=u'Tipo de Recurso', 
        dynamic_view_field=True)
    tipo_recurso_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tipo de Recurso')

    tipo_dispensa = fields.Selection(
        selection=[
            ('d', u'Dispensado'), 
            ('nd', u'Não Dispensado')], 
        string=u'Tipo de Dispensa',
        dynamic_view_field=True)
    tipo_dispensa_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tipo de Dispensa')

    relatorio_dispensa = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Relatório de Dispensa', 
        dynamic_view_field=True)
    relatorio_dispensa_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Relatório de Dispensa')
    
    tem_multa_obrigacao = fields.Selection(
        selection=multa_selection_vals,
        string=u'Obrigação Tem Multa?', 
        dynamic_view_field=True)
    tem_multa_obrigacao_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Obrigação Tem Multa?')

    comprovante_obrigacao = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Comprovante da Obrigação',
        dynamic_view_field=True)
    comprovante_obrigacao_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Comprovante da Obrigação')

    motivo_nao_cumprimento = fields.Selection(
        selection=[
            ('i', u'Impossível'), 
            ('a', u'Alternativa'), 
            ('is', u'Inconsistência na Solicitação')],
        string=u'Motivo do Não Cumprimento', 
        dynamic_view_field=True)
    motivo_nao_cumprimento_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Motivo do Não Cumprimento')

    valor_protocolo = fields.Monetary(
        string=u'Valor Protocolo',
        currency_field='currency_id',
        dynamic_view_field=True)
    valor_protocolo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Valor Protocolo')
    valor_protocolo_media = fields.Monetary(
        string=u'Média Valor Protocolo',
        related='valor_protocolo', 
        group_operator='avg', 
        readonly=True, 
        store=True)

    motivo_cancelamento_id = fields.Many2one(
        comodel_name='motivo.cancelamento', 
        string=u'Motivo de Cancelamento',
        dynamic_view_field=True)
    motivo_cancelamento_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Motivo de Cancelamento')

    transitou = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Transitou?', 
        dynamic_view_field=True)
    transitou_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Transitou')

    tipo_audiencia = fields.Selection(
        selection=[
            ('c', u'Conciliação'), 
            ('ij', u'Instrução e Julgamento')],
        string=u'Tipo de Audiência', 
        dynamic_view_field=True)
    tipo_audiencia_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tipo de Audiência')

    local_audiencia = fields.Char(
        string=u'Local da Audiência', 
        dynamic_view_field=True)
    local_audiencia_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Local da Audiência')
    
    comprovante_repasse = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Comprovante de Repasse', 
        dynamic_view_field=True)
    comprovante_repasse_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Comprovante de Repasse')

    pedido_obrigacao = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Comprovante de Pedido de Obrigação',
        dynamic_view_field=True)
    pedido_obrigacao_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Comprovante de pedido de obrigação')
    
    tipo_conclusao_documentos = fields.Selection(
        selection=[
            ('l', u'Localizado'), 
            ('pl', u'Parcialmente Localizado'), 
            ('nl', u'Não Localizado'), 
            ('i', u'Inexistente'), 
            ('sr', u'Sem Resposta')],
        string=u'Tipo de Conclusão de Documentos', 
        dynamic_view_field=True)
    tipo_conclusao_documentos_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tipo Conclusao Documentos')

    conta_pagamento_id = fields.Many2one(
        comodel_name='res.partner.bank', 
        string='Conta para Pagamento', 
        dynamic_view_field=True)
    conta_pagamento_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Conta Pagamento')
    
    tem_juntada = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Juntada?', 
        dynamic_view_field=True)
    tem_juntada_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tem Juntada')

    tem_citese = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem CITE-SE?', 
        dynamic_view_field=True)
    tem_citese_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show CITE-SE')

    tem_parecer = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Parecer?', 
        dynamic_view_field=True)
    tem_parecer_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Parecer')

    tem_emenda = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Emenda Pendente?', 
        dynamic_view_field=True)
    tem_emenda_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tem Emenda Pendente?')
    
    tem_levantamento = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Precisa Criar Levantamento?',
        dynamic_view_field=True)
    tem_levantamento_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Precisa Criar Levantamento?')

    tem_obrigacao = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Precisa criar Obrigação?',
        dynamic_view_field=True)
    tem_obrigacao_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Precisa criar Obrigação?')

    tem_pagamento = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Precisa Criar Pagamento?',
        dynamic_view_field=True)
    tem_pagamento_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Precisa Criar Pagamento?')

    tem_levantamento_cliente = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Levantamento Pendente no Cliente?',
        dynamic_view_field=True)
    tem_levantamento_cliente_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tem levantamento pendente no cliente?')

    tem_obrigacao_cliente = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Obrigação Pendente no Cliente?',
        dynamic_view_field=True)
    tem_obrigacao_cliente_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tem obrigação pendente no cliente?')

    tem_pagamento_cliente = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Pagamento Pendente no Cliente?',
        dynamic_view_field=True)
    tem_pagamento_cliente_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tem pagamento pendente no cliente?')

    tem_dispensa = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Resposta à Dispensa?',
        dynamic_view_field=True)
    tem_dispensa_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tem Dispensa?')

    precisa_copias = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Precisa de Cópias?',
        dynamic_view_field=True)
    precisa_copias_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Precisa Cópias?')

    tem_baixa_restritivo = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Pedido de Baixa de Restritivo?',
        dynamic_view_field=True)
    tem_baixa_restritivo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Tem pedido de baixa de restritivo?')
    
    valor_contraproposta = fields.Monetary(
        string=u'Valor Contraproposta',
        currency_field='currency_id',
        dynamic_view_field=True)
    valor_contraproposta_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Valor Contraproposta')
    valor_contraproposta_media = fields.Monetary(
        string=u'Média Valor Contraproposta',
        related='valor_contraproposta', 
        group_operator='avg', 
        readonly=True, 
        store=True)

    valor_preparo = fields.Monetary(
        string=u'Valor Custas',
        currency_field='currency_id',
        dynamic_view_field=True)
    valor_preparo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Valor Custas')
    valor_preparo_media = fields.Monetary(
        string=u'Média Valor Custas',
        related='valor_preparo', 
        group_operator='avg', 
        readonly=True, 
        store=True)

    numero_recibo = fields.Char(
        string=u'Nº do Recibo', 
        dynamic_view_field=True)
    numero_recibo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Nº do Recibo')

    data_prevista_sentenca = fields.Date(
        string=u'Data Prevista para Leitura da Sentença', 
        dynamic_view_field=True)
    data_prevista_sentenca_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Data Prevista para Leitura da Sentença')

    area_oficio_id = fields.Many2one(
        comodel_name='area.oficio', 
        string=u'Área do Oficio', 
        dynamic_view_field=True)
    area_oficio_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Área do Oficio')

    tem_audiencia = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Audiência?', 
        dynamic_view_field=True)
    tem_audiencia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Audiência?')

    tem_cedula = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Cédula?', 
        dynamic_view_field=True)
    tem_cedula_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Cédula?')

    tem_prescricao = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Prescrição?',
        dynamic_view_field=True)
    tem_prescricao_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Prescrição?')

    tem_extrato = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Extrato?', 
        dynamic_view_field=True)
    tem_extrato_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Extrato?')
    
    tem_veiculo = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Veículo?', 
        dynamic_view_field=True)
    tem_veiculo_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Veículo?')

    tem_endereco = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Endereço?', 
        dynamic_view_field=True)
    tem_endereco_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Endereço?')

    tem_telefone = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Telefone?', 
        dynamic_view_field=True)
    tem_telefone_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Telefone?')

    citacao_deferida = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Citação Deferida?',
        dynamic_view_field=True)
    citacao_deferida_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Citação Deferida?')
    
    data_citacao_deferida = fields.Date(
        string=u'Data Citação Deferida', 
        dynamic_view_field=True)
    data_citacao_deferida_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data Citacao Deferida')

    citacao_expedida = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Citação Expedida?',
        dynamic_view_field=True)  
    citacao_expedida_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Citação Expedida?')
    
    data_citacao_expedida = fields.Date(
        string=u'Data Citação Expedida', 
        dynamic_view_field=True)
    data_citacao_expedida_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data Citacao Expedida')

    citacao_efetivada = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Citação Efetivada?',
        dynamic_view_field=True)
    citacao_efetivada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Citação Efetivada?')

    data_citacao_efetivada = fields.Date(
        string=u'Data Citação Efetivada', 
        dynamic_view_field=True)
    data_citacao_efetivada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data Citacao Efetiva')

    tem_bens = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Bens?', 
        dynamic_view_field=True)
    tem_bens_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Bens?')

    penhora_deferida = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Penhora Deferida?',
        dynamic_view_field=True)
    penhora_deferida_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Penhora Deferida?')

    data_penhora_deferida = fields.Date(
        string=u'Data Penhora Deferida', 
        dynamic_view_field=True)
    data_penhora_deferida_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data Penhora Deferida')

    penhora_efetivada = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Penhora Efetivada?',
        dynamic_view_field=True)
    penhora_efetivada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Penhora Deferida?')

    data_penhora_efetivada = fields.Date(
        string=u'Data Penhora Efetivada', 
        dynamic_view_field=True)
    data_penhora_efetivada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data Penhora Efetivada')

    recibo_anexo = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Anexo Recibo', 
        dynamic_view_field=True)
    recibo_anexo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Recibo Anexo')

    dossie_citacao_id = fields.Many2one(
        comodel_name='dossie.citacao', 
        string=u'Citação', 
        dynamic_view_field=True)
    dossie_citacao_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Citação')

    dossie_citacao_parte_contraria_ids = fields.Many2many(
        related='dossie_citacao_id.parte_contraria_ids',
        dynamic_view_field=True)
    dossie_citacao_parte_contraria_ids_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Partes a Citar?')

    dossie_resultado_parte_ids = fields.One2many(
        related='dossie_citacao_id.resultado_parte_ids',
        dynamic_view_field=True)
    dossie_resultado_parte_ids_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Partes Citadas?')

    dossie_penhora_id = fields.Many2one(
        comodel_name='dossie.penhora', 
        string=u'Penhora', 
        dynamic_view_field=True)
    dossie_penhora_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Penhora')

    dossie_penhora_tipo_ids = fields.Many2many(
        comodel_name='dossie.penhora.tipo', 
        relation='task_tipo_rel', 
        column1='task_id', 
        column2='tipo_id',
        string=u'Tipos de Penhora',
        dynamic_view_field=True)
    dossie_penhora_tipo_ids_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tipos de Penhora')

    dossie_penhora_bem_ids = fields.Many2many( 
        related='dossie_penhora_id.bem_ids',
        dynamic_view_field=True)
    dossie_penhora_bem_ids_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Bens')

    tipos_obrigacoes_ids = fields.Many2many(
        comodel_name='tipo.obrigacao',
        relation='task_tipo_obrigacao_rel',
        column1='task_id',
        column2='tipo_id',
        string=u'Tipos das Obrigações',
        dynamic_view_field=True)
    tipos_obrigacoes_ids_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tipos das Obrigações')

    tem_contestacao = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Leva Contestação?',
        dynamic_view_field=True)
    tem_contestacao_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Leva Contestação')

    precisa_documento = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Precisa de Documentos?',
        dynamic_view_field=True)
    precisa_documento_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Precisa de Documentos?')

    tipos_documentos_ids = fields.Many2many(
        comodel_name='tipo.documento',
        relation='task_tipos_documentos_rel',
        column1='task_id',
        column2='tipo_id',
        string=u'Tipos dos Documentos',
        dynamic_view_field=True)
    tipos_documentos_ids_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tipos dos Documentos')

    observacoes_documentos = fields.Text(
        string=u'Observações dos Documentos',
        dynamic_view_field=True)
    observacoes_documentos_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Observações dos Documentos')

    documentos_solicitado_ids = fields.Many2many(
        comodel_name='ir.attachment', 
        relation='task_documentos_solicitados_rel', 
        column1='task_id', 
        column2='attachment_id',
        string=u'Documentos Solicitados', 
        dynamic_view_field=True)
    documentos_solicitado_ids_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Documentos Solicitados')

    observacoes_copias = fields.Text(
        string=u'Observações das Cópias',
        dynamic_view_field=True)
    observacoes_copias_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Observações das Cópias')

    valor_pagamento = fields.Monetary(
        string=u'Valor do Pagamento',
        currency_field='currency_id',
        dynamic_view_field=True)
    valor_pagamento_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Valor do Pagamento')
    valor_pagamento_media = fields.Monetary(
        string=u'Média Valor do Pagamento',
        related='valor_pagamento', 
        group_operator='avg', 
        readonly=True, 
        store=True)

    resultado_negociacao = fields.Selection(
        selection=[
        ('f', u'Frutífero'),
        ('i', u'Infrutífero')], 
        string=u'Resultado da Negociação?',
        dynamic_view_field=True)
    resultado_negociacao_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Resultado da Negociação?')

    tem_multa_pagamento = fields.Selection(
        selection=multa_selection_vals,
        string=u'Pagamento Tem Multa?', 
        dynamic_view_field=True)
    tem_multa_pagamento_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Pagamento Tem Multa?')

    guias_pagas_custas = fields.Many2many(
        comodel_name='ir.attachment',
        relation='guias_pagas_attachment_rel',
        column1='task_id', 
        column2='attachment_id',
        string=u'Guias Pagas Custas',
        dynamic_view_field=True)
    guias_pagas_custas_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Guias Pagas Custas')

    precisa_prazo = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Precisa de Prazo?',
        dynamic_view_field=True)
    precisa_prazo_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Precisa de Prazo?')

    precisa_recurso = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Precisa de Recurso?',
        dynamic_view_field=True)
    precisa_recurso_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Precisa de Recurso?')

    related_tipo_sentenca_id = fields.Many2one(
        string=u'Related Tipo de Sentença',
        related='tipo_sentenca_id',
        dynamic_view_field=True)
    related_tipo_sentenca_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Penhora')

    tipo_encerramento_id = fields.Many2one(
        comodel_name='tipo.encerramento',
        string=u'Tipo do Encerramento',
        dynamic_view_field=True)
    tipo_encerramento_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tipo do Encerramento')

    encerrado_cliente = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Encerrado no Cliente?',
        dynamic_view_field=True)
    encerrado_cliente_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Encerrado no Cliente?')

    related_tipo_sentenca_id = fields.Many2one(
        related='tipo_sentenca_id',
        dynamic_view_field=True)
    related_tipo_sentenca_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tipo de Sentença')

    related_analise_acordo = fields.Selection(
        related='analise_acordo',
        dynamic_view_field=True)
    related_analise_acordo_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Análise de Acordo')

    related_obrigacao_alcada = fields.Text(
        related='obrigacao_alcada',
        dynamic_view_field=True)
    related_obrigacao_alcada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Alçada de Obrigação')

    related_valor_alcada = fields.Monetary(
        related='valor_alcada',
        dynamic_view_field=True)
    related_valor_alcada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Valor de Alçada')

    related_motivo_inaptidao = fields.Many2one(
        related='motivo_inaptidao',
        dynamic_view_field=True)
    related_motivo_inaptidao_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Motivo da Inaptidão')

    related_tipo_prazo_id = fields.Many2one(
        related='tipo_prazo_id')
    related_tipo_prazo_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Related Tipo de Prazo')

    related_tipo_recurso_id = fields.Many2one(
        related='tipo_recurso_id')
    related_tipo_recurso_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Related Tipo de Recurso')

    copias_aprovado = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Cópias Aprovadas',
        dynamic_view_field=True)
    copias_aprovado_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Cópias Aprovadas')

    cancelamento_aprovado = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Cancelamento Aprovado',
        dynamic_view_field=True)
    cancelamento_aprovado_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Cancelamento Aprovado')

    tem_audiencia_redesignada = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Audiência Redesignada?',
        dynamic_view_field=True)
    tem_audiencia_redesignada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Audiência Redesignada?')

    data_audiencia_redesignada = fields.Datetime(
        string=u'Data da Audiência Redesignada',
        dynamic_view_field=True)
    data_audiencia_redesignada_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data da Audiência Redesignada')

    tem_proxima_audiencia = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Próxima Audiência?',
        dynamic_view_field=True)
    tem_proxima_audiencia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Próxima Audiência?')

    data_proxima_audiencia = fields.Datetime(
        string=u'Data da Próxima Audiência',
        dynamic_view_field=True)
    data_proxima_audiencia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Data da Próxima Audiência')

    tem_sucumbencia = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Sucumbência?',
        dynamic_view_field=True)
    tem_sucumbencia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Sucumbência?')
    
    valor_sucumbencia = fields.Monetary(
        string=u'Valor Sucumbência',
        currency_field='currency_id',
        dynamic_view_field=True)
    valor_sucumbencia_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Valor Sucumbência')

    cedula_anexo = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Cédula Anexo', 
        dynamic_view_field=True)
    cedula_anexo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Cédula Anexo')

    extrato_anexo = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Extrato Anexo', 
        dynamic_view_field=True)
    extrato_anexo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Extrato Anexo')

    tem_planilha_debito = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Planilha de Débito?',
        dynamic_view_field=True)
    tem_planilha_debito_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Tem Planilha de Débito?')

    planilha_debito_anexo = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Planilha Débito Anexo', 
        dynamic_view_field=True)
    planilha_debito_anexo_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Planilha Débito Anexo')

    related_contrato_id = fields.Many2one(
        related='contrato_id',
        dynamic_view_field=True)
    related_contrato_id_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Contrato')

    related_parecer = fields.Selection(
        related='parecer',
        dynamic_view_field=True)
    related_parecer_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Parecer')

    related_relatorio_parecer = fields.Many2one(
        related='relatorio_parecer',
        dynamic_view_field=True)
    related_relatorio_parecer_show = fields.Boolean(
        compute='_get_field_show', 
        string=u'Show Relatório Parecer')

    analise_parecer = fields.Selection(
        selection=[
        ('r', u'Ratificar'), 
        ('c', u'Complementar'), 
        ('a', u'Alterar')],
        string=u'Análise do Parecer',
        dynamic_view_field=True)
    analise_parecer_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Análise do Parecer')

    analise_parecer_observacoes = fields.Text(
        string=u'Observações para Análise do Parecer',
        dynamic_view_field=True)
    analise_parecer_observacoes_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Observações para Análise do Parecer')

    related_citacao_id = fields.Many2one(
        related='citacao_id',
        dynamic_view_field=True)
    related_citacao_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Related Citação')

    related_liminar_id = fields.Many2one(
        related='liminar_id',
        dynamic_view_field=True)
    related_liminar_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Related Liminar')

    related_sentenca_id = fields.Many2one(
        related='sentenca_id',
        dynamic_view_field=True)
    related_sentenca_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Related Sentença')

    related_acordao_id = fields.Many2one(
        related='acordao_id',
        dynamic_view_field=True)
    related_acordao_id_show = fields.Boolean(
        compute='_get_field_show',
        string=u'Show Related Acordão')


    @api.model_cr_context
    def _field_create(self):
        result = super(ProjectTask, self)._field_create()
        model_fields = sorted(self._fields.itervalues(),
                              key=lambda field: field.type == 'sparse')
        for field in model_fields:
            if field._attrs.get('dynamic_view_field'):
                field_id = self.env['ir.model.fields'].search(
                    [('name', '=', field.name), ('model', '=', 'project.task')], limit=1)
                # can't use write becuase manual fields are not allowed to
                # write
                if field_id:
                    self._cr.execute(
                        "update ir_model_fields set dynamic_view_field='t' where id='%s'" % field_id.id)
        return result

    @api.depends('task_type_id', 'task_type_id.field_ids')
    @api.one
    def _get_field_show(self):
        # write name of dynamic field
        dynamic_fields_list = [
                                'stage_id', 
                                'numero_recibo', 
                                'guia', 
                                'guia_paga',
                                'documento_juntada', 
                                'lote', 
                                'data_audiencia',
                                'presentes_audiencia', 
                                'correspondente_id', 
                                'valor_correspondente',
                                'advogado_id', 
                                'preposto_id', 
                                'ata', 
                                'motivo_infrutividade',
                                'tipo_pagamento', 
                                'tipo_acordo', 
                                'obrigacao',
                                'estado_sentenca',
                                'data_prevista_sentenca',
                                'forma_pagamento_id', 
                                'relatorio_pagamento', 
                                'peticao',
                                'tem_juntada', 
                                'tipo_prazo_id',
                                'tipo_transito_id', 
                                'copias', 
                                'tipo_recurso_id',
                                'tipo_dispensa', 
                                'relatorio_dispensa', 
                                'tem_multa_obrigacao', 
                                'tipos_obrigacoes_ids',
                                'comprovante_obrigacao', 
                                'motivo_nao_cumprimento', 
                                'valor_protocolo',
                                'motivo_cancelamento_id',
                                'comprovante_repasse', 
                                'tipo_conclusao_documentos', 
                                'transitou', 
                                'tipo_audiencia',
                                'local_audiencia', 
                                'conta_pagamento_id', 
                                'valor_contraproposta',
                                'tem_citese', 
                                'tem_parecer', 
                                'tem_emenda', 
                                'tem_dispensa', 
                                'precisa_copias',
                                'valor_preparo', 
                                'tem_levantamento', 
                                'tem_obrigacao',
                                'tem_pagamento', 
                                'tem_levantamento_cliente', 
                                'tem_obrigacao_cliente',
                                'tem_pagamento_cliente', 
                                'tem_baixa_restritivo', 
                                'pedido_obrigacao',
                                'area_oficio_id', 
                                'comprovante_protocolo', 
                                'comprovante_pagamento', 
                                'guias_preparo',
                                'tem_preparo', 
                                'tem_audiencia', 
                                'tem_cedula',
                                'tem_prescricao', 
                                'tem_extrato', 
                                'tem_veiculo', 
                                'tem_endereco', 
                                'tem_telefone',
                                'citacao_deferida', 
                                'citacao_expedida', 
                                'citacao_efetivada', 
                                'tem_bens',
                                'penhora_deferida', 
                                'penhora_efetivada',
                                'dossie_citacao_id', 
                                'dossie_citacao_parte_contraria_ids', 
                                'dossie_resultado_parte_ids',
                                'dossie_penhora_id',
                                'data_citacao_deferida', 
                                'data_citacao_expedida', 
                                'data_citacao_efetivada',
                                'data_penhora_deferida', 
                                'data_penhora_efetivada',
                                'recibo_anexo', 
                                'dossie_penhora_tipo_ids', 
                                'dossie_penhora_bem_ids',
                                'tipo_obrigacao_id', 
                                'tem_contestacao',
                                'precisa_documento',
                                'tipos_documentos_ids',
                                'observacoes_documentos',
                                'documentos_solicitado_ids',
                                'observacoes_copias',
                                'valor_pagamento',
                                'resultado_negociacao',
                                'tem_multa_pagamento',
                                'guias_pagas_custas',
                                'precisa_prazo',
                                'precisa_recurso',
                                'tipo_encerramento_id',
                                'encerrado_cliente',
                                'related_tipo_sentenca_id',
                                'related_analise_acordo',
                                'related_valor_alcada',
                                'related_motivo_inaptidao',
                                'related_tipo_prazo_id',
                                'related_tipo_recurso_id',
                                'related_obrigacao_alcada',
                                'copias_aprovado',
                                'tem_audiencia_redesignada',
                                'data_audiencia_redesignada',
                                'tem_sucumbencia',
                                'valor_sucumbencia',
                                'cedula_anexo',
                                'extrato_anexo',
                                'tem_planilha_debito',
                                'planilha_debito_anexo',
                                'related_contrato_id',
                                'related_parecer',
                                'related_relatorio_parecer',
                                'analise_parecer',
                                'analise_parecer_observacoes',
                                'related_citacao_id',
                                'related_liminar_id',
                                'related_sentenca_id',
                                'related_acordao_id',
                                ]

        field_names = []
        for field in self.task_type_id.field_ids:
            field_names.append(field.name)
        for field_name in dynamic_fields_list:
            # show the field
            if field_name in field_names:
                field_name += '_show'
                setattr(self, field_name, True)
        return True

    

    ########## DOSSIÊ RELATED FIELDS ##########

    dossie_state = fields.Selection(
        store=True, 
        related='dossie_id.state')
    fase_id = fields.Many2one(
        store=True,
        related='dossie_id.fase_id')
    polo_cliente = fields.Selection(
        store=True, 
        related='dossie_id.polo_cliente')

    numero_pendencias = fields.Integer(
        string=u'Nº Pendencias', 
        compute='get_numero_pendencias', 
        store=False,
        search='search_numero_pendencias')

    dossie_name = fields.Char(
        store=True, 
        related='dossie_id.name')
    origem_id = fields.Many2one(
        store=True, 
        related='dossie_id.origem_id')
    processo = fields.Char(
        store=True, 
        related='dossie_id.processo')
    tipo_processo = fields.Selection(
        store=True, 
        related='dossie_id.tipo_processo')

    parte_representada_ids = fields.Many2many(
        related='dossie_id.parte_representada_ids')
    parte_contraria_ids = fields.Many2many(
        related='dossie_id.parte_contraria_ids')
    parte_contraria_contumaz_ids = fields.Many2many(
        related='dossie_id.parte_contraria_contumaz_ids')
    tem_advogado = fields.Selection(
        store=True, 
        related='dossie_id.tem_advogado')
    escritorio_id = fields.Many2one(
        store=True, 
        related='dossie_id.escritorio_id')
    advogado_adverso_ids = fields.Many2many(
        related='dossie_id.advogado_adverso_ids')
    advogado_adverso_agressor_ids = fields.Many2many(
        related='dossie_id.advogado_adverso_agressor_ids')
    assuncao_defesa = fields.Selection(
        store=True,
        related='dossie_id.assuncao_defesa')

    valor_causa = fields.Monetary(
        store=True, 
        related='dossie_id.valor_causa')
    valor_dano_moral = fields.Monetary(
        store=True,
        related='dossie_id.valor_dano_moral')
    valor_dano_material = fields.Monetary(
        store=True,
        related='dossie_id.valor_dano_moral')

    rito_id = fields.Many2one(
        store=True, 
        related='dossie_id.rito_id')
    natureza_id = fields.Many2one(
        store=True, 
        related='dossie_id.natureza_id')
    tipo_acao_id = fields.Many2one(
        store=True, 
        related='dossie_id.tipo_acao_id')

    ordinal = fields.Integer(
        store=True,
        related='dossie_id.ordinal')
    vara_id = fields.Many2one(
        store=True, 
        related='dossie_id.vara_id')
    orgao_id = fields.Many2one(
        store=True, 
        related='dossie_id.orgao_id')
    comarca_id = fields.Many2one(
        store=True, 
        related='dossie_id.comarca_id')
    estado_id = fields.Many2one(
        store=True, 
        related='dossie_id.estado_id')
    
    objeto_id = fields.Many2one(
        store=True, 
        related='dossie_id.objeto_id')
    assunto_id = fields.Many2one(
        store=True, 
        related='dossie_id.assunto_id')
    local_fato = fields.Char(
        store=True,
        related='dossie_id.local_fato')
    data_fato = fields.Date(
        store=True,
        related='dossie_id.data_fato')

    parecer = fields.Selection(
        store=True, 
        related='dossie_id.parecer')
    relatorio_parecer = fields.Many2one(
        store=True,
        related='dossie_id.relatorio_parecer')
    
    analise_acordo = fields.Selection(
        store=True,
        related='dossie_id.analise_acordo')
    motivo_inaptidao = fields.Many2one(
        store=True, 
        related='dossie_id.motivo_inaptidao')
    valor_alcada = fields.Monetary(
        store=True, 
        related='dossie_id.valor_alcada')
    obrigacao_alcada = fields.Text(
        store=True, 
        related='dossie_id.obrigacao_alcada')

    grupo_id = fields.Many2one(
        store=True, 
        related='dossie_id.grupo_id')
    projeto_id = fields.Many2one(
        store=True, 
        related='dossie_id.projeto_id')
    credenciado_id = fields.Many2one(
        store=True, 
        related='dossie_id.credenciado_id')
    
    contrato_id = fields.Many2one(
        store=True, 
        related='dossie_id.contrato_id')
    contrato_tipo_id = fields.Many2one(
        store=True,
        related='dossie_id.contrato_tipo_id')
    contrato = fields.Char(
        store=True,
        related='dossie_id.contrato')
    carteira_id = fields.Many2one(
        store=True, 
        related='dossie_id.carteira_id')
    risco = fields.Selection(
        store=True, 
        related='dossie_id.risco')
    responsabilidade = fields.Selection(
        store=True, 
        related='dossie_id.responsabilidade')
    cessionaria_id = fields.Many2one(
        store=True, 
        related='dossie_id.cessionaria_id')
    task_ids = fields.One2many(
        comodel_name='project.task', 
        inverse_name='dossie_id',
        compute='_compute_task_ids',
        string=u'Tarefas')
    inicial = fields.Text(
        store=True, 
        related='dossie_id.inicial')
    inicial_id = fields.Many2one(
        store=True, 
        related='dossie_id.inicial_id', 
        readonly=True)
    data_distribuicao = fields.Date(
        store=True, 
        related='dossie_id.data_distribuicao')

    citacao = fields.Text(
        store=True, 
        related='dossie_id.citacao')
    citacao_id = fields.Many2one(
        store=True, 
        related='dossie_id.citacao_id')
    data_citacao = fields.Date(
        store=True,
        related='dossie_id.data_citacao')

    liminar_id = fields.Many2one(
        store=True,
        related='dossie_id.liminar_id')
    liminar = fields.Text(
        store=True,
        related='liminar_id.liminar')
    liminar_anexo_id = fields.Many2one(
        store=True,
        related='liminar_id.anexo_id')
    data_liminar = fields.Date(
        store=True,
        related='liminar_id.data')
    tipo_liminar_id = fields.Many2one(
        store=True,
        related='liminar_id.tipo_liminar_id')

    sentenca_id = fields.Many2one(
        store=True,
        related='dossie_id.sentenca_id')
    sentenca = fields.Text(
        store=True, 
        related='sentenca_id.sentenca')
    sentenca_anexo_id = fields.Many2one(
        store=True,
        related='sentenca_id.anexo_id',
        readonly=True)
    data_sentenca = fields.Date(
        store=True,
        related='sentenca_id.data')
    tipo_sentenca_id = fields.Many2one(
        store=True,
        related='sentenca_id.tipo_sentenca_id')

    acordao_id = fields.Many2one(
        store=True, 
        related='dossie_id.acordao_id')
    acordao_anexo_id = fields.Many2one(
        store=True,
        related='acordao_id.anexo_id')
    acordao = fields.Text(
        store=True, 
        related='acordao_id.acordao')
    data_acordao = fields.Date(
        store=True, 
        related='acordao_id.data')
    tipo_acordao_id = fields.Many2one(
        store=True,
        related='acordao_id.tipo_acordao_id')

    acordao_superior_id = fields.Many2one(
        store=True,
        related='dossie_id.acordao_superior_id', 
        readonly=True)
    acordao_superior = fields.Text( 
        store=True,
        related='dossie_id.acordao_superior')
    data_acordao_superior = fields.Date(
        store=True,
        related='dossie_id.data_acordao_superior')
    tipo_acordao_superior_id = fields.Many2one(
        store=True,
        related='dossie_id.tipo_acordao_superior_id')

    acordao_supremo_id = fields.Many2one(
        store=True,
        related='dossie_id.acordao_supremo_id', 
        readonly=True)
    acordao_supremo = fields.Text(
        store=True,
        related='dossie_id.acordao_supremo')
    data_acordao_supremo = fields.Date(
        store=True, 
        related='dossie_id.data_acordao_supremo')
    tipo_acordao_supremo_id = fields.Many2one(
        store=True,
        related='dossie_id.tipo_acordao_supremo_id')

    movimentacao_historico_ids = fields.One2many(
        inverse_name='dossie_id',
        store=True,
        related='dossie_id.movimentacao_historico_ids')

    fase_cliente =  fields.Char(
        related='dossie_id.fase_cliente')
   

    @api.onchange('estado_id', 'comarca_id')
    def onchange_estado(self):
        partners = []
        result = {'domain': {},
                  'value': {}, }
        comarca_id = self.comarca_id.id
        if self.comarca_id.state_id != self.estado_id:
            comarca_id = False
        domain = [('is_correspondente', '=', True)]
        partner_ids = self.env['res.partner'].search(domain).ids
        if len(partner_ids):
            partner_ids.append(0)
            if self.comarca_id:
                # get all partners with type 'correspondente' with selected
                # city
                self.env.cr.execute(
                    "select partner_id from res_partner_valid_comarca_rel where city_id='%s' and partner_id in %s" % (
                        self.comarca_id.id, tuple(partner_ids)))
                partners = self.env.cr.fetchall()
            result['domain'].update(
                {'correspondente_id': [('id', 'in', partners)]})
        result['value'].update({'comarca_id': comarca_id})
        return result

    @api.one
    @api.depends('comarca_id')
    def get_valid_correspondente(self):
        if self.comarca_id:
            query = "select partner_id from res_partner_valid_comarca_rel where city_id='%s'" % self.comarca_id.id
            self.env.cr.execute(query)
            result = self.env.cr.fetchall()
            self.valid_correspondente_ids = [row[0] for row in result]
        else:
            self.valid_correspondente_ids = [(6, 0, [])]

    @api.one
    def get_numero_pendencias(self):
        types = self.env['task.type'].search(
            [('name', 'in', [u'Pagamento', u'Obrigação', u'Levantamento'])])
        stages = self.env['project.task.type'].search(
            [('name', 'in', [u'Concluído', u'Cancelado'])])
        tasks = self.env['project.task'].search(
            [('task_type_id', 'in', types.ids), ('dossie_id', '=', self.dossie_id.id), ('stage_id', 'not in', stages.ids)])
        self.numero_pendencias = len(tasks)

    def search_numero_pendencias(self, operator, operand):
        result = []
        for task in self.search([]):
            # append 0 in case a single element found
            types = tuple(
                self.env['task.type'].search([('name', 'in', [u'Pagamento', u'Obrigação', u'Levantamento'])]).ids + [0])
            stages = tuple(
                self.env['project.task.type'].search([('name', 'in', [u'Concluído', u'Cancelado'])]).ids + [0])
            query = "select id from project_task where task_type_id in %s and stage_id not in %s and dossie_id = %s" % (
                types, stages, task.dossie_id.id)
            self.env.cr.execute(query)
            tasks = self.env.cr.fetchall()
            if operator == '=':
                if len(tasks) == operand:
                    result.append(task.id)
            if operator == '>':
                if len(tasks) > operand:
                    result.append(task.id)
            if operator == '<':
                if len(tasks) < operand:
                    result.append(task.id)
            if operator == '>=':
                if len(tasks) >= operand:
                    result.append(task.id)
            if operator == '<=':
                if len(tasks) <= operand:
                    result.append(task.id)
            if operator == '!=':
                if len(tasks) != operand:
                    result.append(task.id)
        return [('id', 'in', result)]

    """
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ProjectTask, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        
        if view_type == 'form':
            print 'FORM VIEW FORM VIEW FORM VIEW FORM VIEW'
            view_obj = etree.XML(res['arch'])
            
            elements = []
            update_fields = {}
            params = self._context.get('params', False)
            if 'id' in params:
                tasks = self.env['project.task'].search([])
                for task in tasks:
                    field_names = []
                    print 'task_type_id', task.task_type_id
                    for field in task.task_type_id.field_ids:
                        field_names.append(field.name)

                    print 'Field names: ', field_names
                    for node in view_obj.xpath("//field[@name='task_type_id']"):
                        if 'tipo_prazo_id' in field_names:
                            elements.append(etree.Element('field', {'name': 'tipo_prazo_id'}))
                            update_fields['tipo_prazo_id'] = {'type': 'many2one'}

                        for elem in elements:
                            setup_modifiers(elem)
                            node.addnext(elem)
            
            res['fields'].update(update_fields)

            res['arch'] = etree.tostring(view_obj)

        return res"""

    # set dynamic_view_field True in fields
    # dynamic_view_field is custom property
    
    
    
    @api.one
    def _get_dossie_tasks(self):
        self.dossie_task_ids = [
            (6, 0, [task.id for task in self.dossie_id.task_ids])]

    @api.onchange('dossie_id')
    def change_dossie_id(self):
        self.name = self.dossie_id.name or False
        self.project_id = self.dossie_id.projeto_id.id or False

    def _compute_task_ids(self):
        self.task_ids = [(6, 0, [task.id for task in self.dossie_id.task_ids])]
