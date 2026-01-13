# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DiogenesCuenta(models.Model):
    _name = 'diogenes.cuenta'
    _description = 'Cuenta Financiera'
    _order = 'nombre asc'
    _rec_name = 'nombre'

    nombre = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre de la cuenta'
    )
    
    tipo_cuenta = fields.Selection([
        ('banco', 'Cuenta Bancaria'),
        ('inversion', 'Cuenta de Inversión'),
        ('efectivo', 'Efectivo'),
        ('credito', 'Tarjeta de Crédito'),
        ('digital', 'Billetera Digital'),
        ('ahorro', 'Cuenta de Ahorro'),
        ('otro', 'Otro')
    ], string='Tipo de Cuenta', required=True, default='banco')
    
    numero_cuenta = fields.Char(
        string='Número de Cuenta',
        help='Número o identificador de la cuenta'
    )
    
    institucion = fields.Char(
        string='Institución Financiera',
        help='Banco, cooperativa u otra institución'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    saldo_inicial = fields.Monetary(
        string='Saldo Inicial',
        currency_field='currency_id',
        default=0.0,
        help='Saldo al crear la cuenta'
    )
    
    saldo_actual = fields.Monetary(
        string='Saldo Actual',
        compute='_compute_saldo_actual',
        store=True,
        currency_field='currency_id',
        help='Saldo calculado basado en transacciones'
    )
    
    color = fields.Integer(
        string='Color',
        help='Color para identificar la cuenta'
    )
    
    icono = fields.Char(
        string='Ícono',
        help='Ícono FontAwesome (ej: fa-bank, fa-credit-card)'
    )
    
    descripcion = fields.Text(
        string='Descripción'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        default=lambda self: self.env.user,
        required=True
    )
    
    transaccion_origen_ids = fields.One2many(
        'diogenes.transaccion',
        'cuenta_origen_id',
        string='Transacciones de Origen'
    )
    
    transaccion_destino_ids = fields.One2many(
        'diogenes.transaccion',
        'cuenta_destino_id',
        string='Transacciones de Destino'
    )
    
    transaccion_origen_count = fields.Integer(
        string='Total Salidas',
        compute='_compute_transaccion_count',
        store=False
    )
    
    transaccion_destino_count = fields.Integer(
        string='Total Entradas',
        compute='_compute_transaccion_count',
        store=False
    )
    
    transaccion_count = fields.Integer(
        string='Número de Transacciones',
        compute='_compute_transaccion_count'
    )
    
    _sql_constraints = [
        ('nombre_user_unique', 'unique(nombre, user_id)', 
         'Ya tienes una cuenta con este nombre'),
    ]
    
    @api.depends('transaccion_origen_ids', 'transaccion_destino_ids')
    def _compute_transaccion_count(self):
        for record in self:
            record.transaccion_origen_count = len(record.transaccion_origen_ids)
            record.transaccion_destino_count = len(record.transaccion_destino_ids)
            record.transaccion_count = record.transaccion_origen_count + record.transaccion_destino_count
    
    @api.depends('saldo_inicial', 'transaccion_origen_ids', 'transaccion_destino_ids',
                 'transaccion_origen_ids.monto', 'transaccion_origen_ids.state', 'transaccion_origen_ids.tipo',
                 'transaccion_destino_ids.monto', 'transaccion_destino_ids.state', 'transaccion_destino_ids.tipo')
    def _compute_saldo_actual(self):
        for record in self:
            saldo = record.saldo_inicial
            
            # Transacciones donde esta cuenta es origen (sale dinero)
            salidas = self.env['diogenes.transaccion'].search([
                ('cuenta_origen_id', '=', record.id),
                ('state', '=', 'confirmed'),
                ('tipo', 'in', ['gasto', 'transferencia'])
            ])
            saldo -= sum(salidas.mapped('monto'))
            
            # Transacciones donde esta cuenta es destino (entra dinero)
            entradas = self.env['diogenes.transaccion'].search([
                ('cuenta_destino_id', '=', record.id),
                ('state', '=', 'confirmed'),
                ('tipo', 'in', ['ingreso', 'transferencia'])
            ])
            saldo += sum(entradas.mapped('monto'))
            
            record.saldo_actual = saldo
    
    @api.depends('transaccion_origen_ids', 'transaccion_destino_ids')
    def _compute_transaccion_count(self):
        for record in self:
            record.transaccion_count = len(record.transaccion_origen_ids) + len(record.transaccion_destino_ids)
