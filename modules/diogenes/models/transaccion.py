# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DiogenesTransaccion(models.Model):
    _name = 'diogenes.transaccion'
    _description = 'Transacción Financiera'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, id desc'
    _rec_name = 'descripcion'

    descripcion = fields.Char(
        string='Descripción',
        required=True,
        tracking=True,
        help='Descripción de la transacción'
    )
    
    tipo = fields.Selection([
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto')
    ], string='Tipo', required=True, default='gasto', tracking=True)
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    monto = fields.Monetary(
        string='Monto',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help='Monto de la transacción'
    )
    
    fecha = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    categoria_id = fields.Many2one(
        'diogenes.categoria',
        string='Categoría',
        required=True,
        tracking=True
    )
    
    notas = fields.Text(
        string='Notas'
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        default=lambda self: self.env.user,
        required=True
    )
    
    @api.constrains('monto')
    def _check_monto(self):
        for record in self:
            if record.monto <= 0:
                raise ValidationError('El monto debe ser mayor a cero')
    
    def action_confirm(self):
        """Confirmar la transacción"""
        self.ensure_one()
        self.write({'state': 'confirmed'})
        return True
    
    def action_cancel(self):
        """Cancelar la transacción"""
        self.ensure_one()
        self.write({'state': 'cancelled'})
        return True
    
    def action_draft(self):
        """Volver a borrador"""
        self.ensure_one()
        self.write({'state': 'draft'})
        return True
