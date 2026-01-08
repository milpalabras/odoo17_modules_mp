# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DiogenesMetaFinanciera(models.Model):
    _name = 'diogenes.meta.financiera'
    _description = 'Meta Financiera'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_limite asc'

    nombre = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
        help='Nombre de la meta financiera'
    )
    
    tipo = fields.Selection([
        ('ahorro', 'Ahorro'),
        ('inversion', 'Inversión'),
        ('jubilacion', 'Jubilación'),
        ('deuda', 'Pago de Deuda'),
        ('otro', 'Otro')
    ], string='Tipo', required=True, default='ahorro', tracking=True)
    
    descripcion = fields.Text(
        string='Descripción',
        help='Descripción detallada de la meta'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    monto_objetivo = fields.Monetary(
        string='Monto Objetivo',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help='Monto que se desea alcanzar'
    )
    
    monto_actual = fields.Monetary(
        string='Monto Actual',
        currency_field='currency_id',
        default=0.0,
        tracking=True,
        help='Monto acumulado hasta el momento'
    )
    
    monto_faltante = fields.Monetary(
        string='Monto Faltante',
        compute='_compute_monto_faltante',
        store=True,
        currency_field='currency_id'
    )
    
    porcentaje_completado = fields.Float(
        string='Progreso (%)',
        compute='_compute_porcentaje_completado',
        store=True
    )
    
    fecha_inicio = fields.Date(
        string='Fecha Inicio',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    fecha_limite = fields.Date(
        string='Fecha Límite',
        tracking=True,
        help='Fecha objetivo para alcanzar la meta'
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('achieved', 'Alcanzada'),
        ('cancelled', 'Cancelada')
    ], string='Estado', default='draft', tracking=True)
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        default=lambda self: self.env.user,
        required=True
    )
    
    notas = fields.Text(
        string='Notas'
    )
    
    priority = fields.Selection([
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente')
    ], string='Prioridad', default='medium')
    
    @api.depends('monto_objetivo', 'monto_actual')
    def _compute_monto_faltante(self):
        for record in self:
            record.monto_faltante = record.monto_objetivo - record.monto_actual
    
    @api.depends('monto_objetivo', 'monto_actual')
    def _compute_porcentaje_completado(self):
        for record in self:
            if record.monto_objetivo > 0:
                porcentaje = (record.monto_actual / record.monto_objetivo) * 100
                record.porcentaje_completado = min(porcentaje, 100)
            else:
                record.porcentaje_completado = 0.0
    
    @api.constrains('monto_objetivo')
    def _check_monto_objetivo(self):
        for record in self:
            if record.monto_objetivo <= 0:
                raise ValidationError('El monto objetivo debe ser mayor a cero')
    
    @api.constrains('monto_actual')
    def _check_monto_actual(self):
        for record in self:
            if record.monto_actual < 0:
                raise ValidationError('El monto actual no puede ser negativo')
    
    def action_start(self):
        """Iniciar la meta"""
        self.ensure_one()
        self.write({'state': 'in_progress'})
        return True
    
    def action_achieve(self):
        """Marcar como alcanzada"""
        self.ensure_one()
        self.write({'state': 'achieved'})
        return True
    
    def action_cancel(self):
        """Cancelar la meta"""
        self.ensure_one()
        self.write({'state': 'cancelled'})
        return True
    
    def action_draft(self):
        """Volver a borrador"""
        self.ensure_one()
        self.write({'state': 'draft'})
        return True
