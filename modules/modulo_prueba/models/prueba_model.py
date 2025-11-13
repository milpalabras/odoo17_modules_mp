# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PruebaModel(models.Model):
    _name = 'modulo.prueba'
    _description = 'Modelo de Prueba'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre del registro de prueba'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada del registro'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Indica si el registro está activo'
    )
    
    priority = fields.Selection([
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente')
    ], string='Prioridad', default='normal')
    
    date_created = fields.Datetime(
        string='Fecha de Creación',
        default=fields.Datetime.now,
        readonly=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario Responsable',
        default=lambda self: self.env.user
    )
    
    tag_ids = fields.Many2many(
        'modulo.prueba.tag',
        string='Etiquetas'
    )
    
    progress = fields.Float(
        string='Progreso (%)',
        default=0.0,
        help='Porcentaje de progreso (0-100)'
    )

    @api.constrains('progress')
    def _check_progress(self):
        for record in self:
            if record.progress < 0 or record.progress > 100:
                raise ValueError("El progreso debe estar entre 0 y 100%")

    def action_complete(self):
        """Marcar como completado"""
        self.write({
            'progress': 100.0,
            'priority': 'low'
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Completado',
                'message': f'{self.name} ha sido marcado como completado.',
                'type': 'success',
            }
        }


class PruebaTag(models.Model):
    _name = 'modulo.prueba.tag'
    _description = 'Etiquetas de Prueba'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    
    color = fields.Integer(
        string='Color'
    )
