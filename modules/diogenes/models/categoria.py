# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DiogenesCategoria(models.Model):
    _name = 'diogenes.categoria'
    _description = 'Categoría de Transacción'
    _order = 'nombre asc'
    _rec_name = 'nombre'

    nombre = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre de la categoría'
    )
    
    codigo = fields.Char(
        string='Código',
        required=True,
        help='Código único de la categoría'
    )
    
    tipo = fields.Selection([
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
        ('ambos', 'Ambos')
    ], string='Tipo', default='ambos', required=True)
    
    color = fields.Integer(
        string='Color',
        help='Color para identificar la categoría en gráficos'
    )
    
    descripcion = fields.Text(
        string='Descripción'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    transaccion_ids = fields.One2many(
        'diogenes.transaccion',
        'categoria_id',
        string='Transacciones'
    )
    
    transaccion_count = fields.Integer(
        string='Número de Transacciones',
        compute='_compute_transaccion_count'
    )
    
    _sql_constraints = [
        ('codigo_unique', 'unique(codigo)', 'El código de la categoría debe ser único'),
    ]
    
    @api.depends('transaccion_ids')
    def _compute_transaccion_count(self):
        for record in self:
            record.transaccion_count = len(record.transaccion_ids)
