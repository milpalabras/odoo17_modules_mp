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
        ('gasto', 'Gasto'),
        ('transferencia', 'Transferencia')
    ], string='Tipo', required=True, default='gasto', tracking=True)
    
    metodo_pago = fields.Selection([
        ('efectivo', 'Efectivo'),
        ('debito', 'Tarjeta de Débito'),
        ('credito', 'Tarjeta de Crédito'),
        ('debito_auto', 'Débito Automático'),
        ('transferencia', 'Transferencia Bancaria'),
        ('digital', 'Billetera Digital'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro')
    ], string='Método de Pago', tracking=True)
    
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
        tracking=True
    )
    
    cuenta_origen_id = fields.Many2one(
        'diogenes.cuenta',
        string='Cuenta Origen',
        tracking=True,
        help='Cuenta desde donde sale el dinero'
    )
    
    cuenta_destino_id = fields.Many2one(
        'diogenes.cuenta',
        string='Cuenta Destino',
        tracking=True,
        help='Cuenta hacia donde va el dinero'
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
    
    @api.constrains('tipo', 'categoria_id', 'cuenta_origen_id', 'cuenta_destino_id')
    def _check_campos_requeridos(self):
        for record in self:
            # Para transferencias se requieren ambas cuentas
            if record.tipo == 'transferencia':
                if not record.cuenta_origen_id or not record.cuenta_destino_id:
                    raise ValidationError('Las transferencias requieren cuenta origen y cuenta destino')
                if record.cuenta_origen_id == record.cuenta_destino_id:
                    raise ValidationError('La cuenta origen y destino deben ser diferentes')
            
            # Para gastos e ingresos se requiere categoría
            if record.tipo in ['gasto', 'ingreso'] and not record.categoria_id:
                raise ValidationError('Los ingresos y gastos requieren una categoría')
            
            # Para gastos se requiere cuenta origen
            if record.tipo == 'gasto' and not record.cuenta_origen_id:
                raise ValidationError('Los gastos requieren una cuenta origen')
            
            # Para ingresos se requiere cuenta destino
            if record.tipo == 'ingreso' and not record.cuenta_destino_id:
                raise ValidationError('Los ingresos requieren una cuenta destino')
    
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
