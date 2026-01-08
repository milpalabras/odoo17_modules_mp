# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DiogenesPresupuesto(models.Model):
    _name = 'diogenes.presupuesto'
    _description = 'Presupuesto Mensual'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    nombre = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
        help='Nombre descriptivo del presupuesto'
    )
    
    categoria_id = fields.Many2one(
        'diogenes.categoria',
        string='Categoría',
        required=True,
        domain=[('tipo', 'in', ['gasto', 'ambos'])],
        tracking=True
    )
    
    monto_presupuestado = fields.Float(
        string='Monto Presupuestado',
        required=True,
        digits=(16, 2),
        tracking=True,
        help='Monto máximo asignado para esta categoría'
    )
    
    fecha_inicio = fields.Date(
        string='Fecha Inicio',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    fecha_fin = fields.Date(
        string='Fecha Fin',
        required=True,
        tracking=True
    )
    
    monto_gastado = fields.Float(
        string='Monto Gastado',
        compute='_compute_monto_gastado',
        store=True,
        digits=(16, 2)
    )
    
    monto_disponible = fields.Float(
        string='Monto Disponible',
        compute='_compute_monto_disponible',
        store=True,
        digits=(16, 2)
    )
    
    porcentaje_usado = fields.Float(
        string='Porcentaje Usado (%)',
        compute='_compute_porcentaje_usado',
        store=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        default=lambda self: self.env.user,
        required=True
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    notas = fields.Text(
        string='Notas'
    )
    
    @api.depends('categoria_id', 'fecha_inicio', 'fecha_fin')
    def _compute_monto_gastado(self):
        for record in self:
            if record.categoria_id and record.fecha_inicio and record.fecha_fin:
                transacciones = self.env['diogenes.transaccion'].search([
                    ('categoria_id', '=', record.categoria_id.id),
                    ('tipo', '=', 'gasto'),
                    ('state', '=', 'confirmed'),
                    ('fecha', '>=', record.fecha_inicio),
                    ('fecha', '<=', record.fecha_fin),
                    ('user_id', '=', record.user_id.id)
                ])
                record.monto_gastado = sum(transacciones.mapped('monto'))
            else:
                record.monto_gastado = 0.0
    
    @api.depends('monto_presupuestado', 'monto_gastado')
    def _compute_monto_disponible(self):
        for record in self:
            record.monto_disponible = record.monto_presupuestado - record.monto_gastado
    
    @api.depends('monto_presupuestado', 'monto_gastado')
    def _compute_porcentaje_usado(self):
        for record in self:
            if record.monto_presupuestado > 0:
                record.porcentaje_usado = (record.monto_gastado / record.monto_presupuestado) * 100
            else:
                record.porcentaje_usado = 0.0
    
    @api.constrains('monto_presupuestado')
    def _check_monto_presupuestado(self):
        for record in self:
            if record.monto_presupuestado <= 0:
                raise ValidationError('El monto presupuestado debe ser mayor a cero')
    
    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.fecha_fin < record.fecha_inicio:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio')
