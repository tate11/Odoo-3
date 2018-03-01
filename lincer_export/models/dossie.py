# -*-coding:utf-8-*-
from odoo import models, fields, api, _

class DossieMovimentacao(models.Model):
    _inherit = 'dossie.movimentacao'

    @api.multi
    def process_movimentacao_task(self):
    	action_id = self.env['project.task.action'].search([('name','=', u'Ler Movimentação')], limit = 1)        
    	for record in self:
			tipo_name = record.tipo_movimentacao_id.name
			task_type_id =  self.env['task.type'].search([('name','=', tipo_name)], limit = 1)
			task = False
			for t in record.dossie_id.task_ids:
				if t.task_type_id.name == tipo_name:
					task = t
					break

			if task:
				if tipo_name == 'Prazo':
					if task.tipo_prazo_id and record.tipo_prazo_id and task.tipo_prazo_id.id == record.tipo_prazo_id.id:
						if task.stage_id.closed is False:
							action_line  = self.env['project.task.action.line'].create({
				                                    'movimentacao_id' : record.id,
				                                    'action_id' : action_id and action_id.id or False,
				                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
				                                    'task_id' : task.id,
				                                    })
							record.action_line_id = action_line.id
							record.task_id = action_line.task_id.id
						else:
							new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id':  task_type_id and task_type_id.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        'tipo_prazo_id': record.tipo_prazo_id and record.tipo_prazo_id.id or False,
					        })
							record.task_id = new_task.id
					else:
						new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id':  task_type_id and task_type_id.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        'tipo_prazo_id': record.tipo_prazo_id and record.tipo_prazo_id.id or False,
					        })
						record.task_id = new_task.id
				elif tipo_name == 'Recurso':
					if task.tipo_recurso_id and record.tipo_recurso_id and task.tipo_recurso_id.id == record.tipo_recurso_id.id:
						if task.stage_id.closed is False:
							action_line  = self.env['project.task.action.line'].create({
				                                    'movimentacao_id' : record.id,
				                                    'action_id' : action_id and action_id.id or False,
				                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
				                                    'task_id' : task.id,
				                                    })
							record.action_line_id = action_line.id
							record.task_id = action_line.task_id.id
							
						else:
							new_task = self.env['project.task'].create({
						        'movimentacao_id' : record.id,
						        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
						        'task_type_id':  task_type_id and task_type_id.id or False,
						        'dossie_id': record.dossie_id and record.dossie_id.id or False,
						        'tipo_recurso_id': record.tipo_recurso_id and record.tipo_recurso_id.id or False,
						        })
							record.task_id = new_task.id
					else:
						new_task = self.env['project.task'].create({
						        'movimentacao_id' : record.id,
						        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
						        'task_type_id':  task_type_id and task_type_id.id or False,
						        'dossie_id': record.dossie_id and record.dossie_id.id or False,
						        'tipo_recurso_id': record.tipo_recurso_id and record.tipo_recurso_id.id or False,
						        })
						record.task_id = new_task.id

				elif tipo_name not in ('Prazo','Recurso'):
					if task.stage_id.closed is False:
						action_line  = self.env['project.task.action.line'].create({
			                                    'movimentacao_id' : record.id,
			                                    'action_id' : action_id and action_id.id or False,
			                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
			                                    'task_id' : task.id,
			                                    })
						record.action_line_id = action_line.id
						record.task_id = action_line.task_id.id
						
					else:
						new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id':  task_type_id and task_type_id.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        })
						record.task_id = new_task.id
			elif task_type_id:
				new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id': task_type_id and task_type_id.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        'tipo_prazo_id': record.tipo_prazo_id and record.tipo_prazo_id.id or False,
					        })
				record.task_id = new_task.id


			if record.tem_pagamento == 's':
				for t in record.dossie_id.task_ids:
					if t.task_type_id.name == 'Pagamento':
						if t.stage_id.closed is False:
							#create acton line
							action_line  = self.env['project.task.action.line'].create({
				                                    'movimentacao_id' : record.id,
				                                    'action_id' : action_id and action_id.id or False,
				                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
				                                    'task_id' : task.id,
				                                    })
							record.action_line_id = action_line.id
							record.task_id = action_line.task_id.id
							break
						else:
							new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id':  t.task_type_id.id,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        })
							record.task_id = new_task.id
							break
					else:
						task_type = self.env['project.task.type'].search([('name','=','Pagamento')], limit=1)
						new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id':  task_type and task_type.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        })
						record.task_id = new_task.id
						break

			if record.tem_audiencia == 's':
				for t in record.dossie_id.task_ids:
					if t.task_type_id.name == 'Audiência':
						if t.stage_id.closed is False:
							#create acton line
							action_line  = self.env['project.task.action.line'].create({
				                                    'movimentacao_id' : record.id,
				                                    'action_id' : action_id and action_id.id or False,
				                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
				                                    'task_id' : task.id,
				                                    })
							# write action id back in movimentacao
							record.action_line_id = action_line.id
							record.task_id = action_line.task_id.id
							break
						else:
							new_task = self.env['project.task'].create({
						        'movimentacao_id' : record.id,
						        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
						        'task_type_id':  t.task_type_id.id,
						        'dossie_id': record.dossie_id and record.dossie_id.id or False,
						        })
							record.task_id = new_task.id
							break	
					else:
						task_type = self.env['project.task.type'].search([('name','=','Audiência')], limit=1)
						new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id': task_type and task_type.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        })
						record.task_id = new_task.id
						break

			if record.tem_levantamento == 's':
				for t in record.dossie_id.task_ids:
					if t.task_type_id.name == 'Levantamento':
						if t.stage_id.closed is False:
							#create acton line
							action_line  = self.env['project.task.action.line'].create({
				                                    'movimentacao_id' : record.id,
				                                    'action_id' : action_id and action_id.id or False,
				                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
				                                    'task_id' : task.id,
				                                    })
							# write action id back in movimentacao
							record.action_line_id = action_line.id
							record.task_id = action_line.task_id.id
							break
						else:
							new_task = self.env['project.task'].create({
						        'movimentacao_id' : record.id,
						        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
						        'task_type_id':  t.task_type_id.id,
						        'dossie_id': record.dossie_id and record.dossie_id.id or False,
						        })
							record.task_id = new_task.id
							break
					else:
						task_type = self.env['project.task.type'].search([('name','=','Levantamento')], limit=1)
						new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id':  task_type and task_type.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        })
						record.task_id = new_task.id
						break

			if record.tem_encerramento == 's':
				for t in record.dossie_id.task_ids:
					if t.task_type_id.name == 'Encerramento':
						if t.stage_id.closed is False:
							#create acton line
							action_line  = self.env['project.task.action.line'].create({
				                                    'movimentacao_id' : record.id,
				                                    'action_id' : action_id and action_id.id or False,
				                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
				                                    'task_id' : task.id,
				                                    })
							# write action id back in movimentacao
							record.action_line_id = action_line.id
							record.task_id = action_line.task_id.id
							break
						else:
							new_task = self.env['project.task'].create({
						        'movimentacao_id' : record.id,
						        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
						        'task_type_id':  t.task_type_id.id,
						        'dossie_id': record.dossie_id and record.dossie_id.id or False,
						        })
							record.task_id = new_task.id
							break
					else:
						task_type = self.env['project.task.type'].search([('name','=','Encerramento')], limit=1)
						new_task = self.env['project.task'].create({
					        'movimentacao_id' : record.id,
					        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
					        'task_type_id':  task_type and task_type.id or False,
					        'dossie_id': record.dossie_id and record.dossie_id.id or False,
					        })
						record.task_id = new_task.id
						break



      			
      			"""

			action_id = env['project.task.action'].search([('name','=', u'Ler Movimentação')], limit = 1)        

			if found:
			    action_line  = env['project.task.action.line'].create({
			                                    'movimentacao_id' : record.id,
			                                    'action_id' : action_id and action_id.id or False,
			                                    'dossie_id': record.dossie_id and record.dossie_id.id or False,
			                                    'task_id' : task_id,
			                                    })
			    # write action id back in movimentacao
			    record['action_line_id'] = action_line.id
			    record['task_id'] = action_line.task_id.id
			else:
			    task_type_id =  env['task.type'].search([('name','=', tipo_name)], limit = 1)        
			    task = env['project.task'].create({
			        'movimentacao_id' : record.id,
			        'name' : record.dossie_id and record.dossie_id.name or 'ERRO',
			        'task_type_id':  task_type_id and task_type_id.id or False,
			        'dossie_id': record.dossie_id and record.dossie_id.id or False,
			        'tipo_prazo_id': record.tipo_prazo_id and record.tipo_prazo_id.id or False,
			        'tipo_recurso_id': record.tipo_recurso_id and record.tipo_recurso_id.id or False
			        })
			    record['task_id'] = task.id"""
