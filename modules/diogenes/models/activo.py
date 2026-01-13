# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DiogenesActivo(models.Model):
    _name = 'diogenes.activo'
    _description = 'Activos y Bienes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_adquisicion desc, nombre'
    _rec_name = 'nombre'
    
    nombre = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
        help='Nombre del activo o bien'
    )
    
    tipo = fields.Selection([
        ('inmueble', 'Inmueble (Casa, Terreno)'),
        ('vehiculo', 'Vehículo'),
        ('electronico', 'Electrónico'),
        ('mobiliario', 'Mobiliario'),
        ('joyeria', 'Joyería'),
        ('arte', 'Arte y Coleccionables'),
        ('inversion', 'Inversión'),
        ('otro', 'Otro')
    ], string='Tipo', required=True, default='otro', tracking=True)
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    
    valor_compra = fields.Monetary(
        string='Valor de Compra',
        currency_field='currency_id',
        tracking=True,
        help='Valor al momento de la compra'
    )
    
    valor_estimado = fields.Monetary(
        string='Valor Estimado Actual',
        currency_field='currency_id',
        tracking=True,
        help='Valor estimado actual del bien'
    )
    
    depreciacion = fields.Monetary(
        string='Depreciación',
        compute='_compute_depreciacion',
        store=True,
        currency_field='currency_id',
        help='Diferencia entre valor de compra y valor estimado actual'
    )
    
    porcentaje_depreciacion = fields.Float(
        string='% Depreciación',
        compute='_compute_depreciacion',
        store=True,
        help='Porcentaje de depreciación del activo'
    )
    
    fecha_adquisicion = fields.Date(
        string='Fecha de Adquisición',
        default=fields.Date.today,
        tracking=True
    )
    
    estado_conservacion = fields.Selection([
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo')
    ], string='Estado de Conservación', default='bueno', tracking=True)
    
    puede_venderse = fields.Boolean(
        string='Disponible para Venta',
        default=True,
        tracking=True,
        help='Indica si este activo está disponible para ser vendido'
    )
    
    meta_financiera_id = fields.Many2one(
        'diogenes.meta.financiera',
        string='Meta Financiera Asociada',
        tracking=True,
        help='Meta financiera para la cual se podría vender este activo'
    )
    
    ubicacion = fields.Char(
        string='Ubicación',
        help='Dónde se encuentra el activo'
    )
    
    numero_serie = fields.Char(
        string='Número de Serie / Identificador',
        help='Número de serie, placas, escrituras, etc.'
    )
    
    descripcion = fields.Text(
        string='Descripción'
    )
    
    notas = fields.Text(
        string='Notas'
    )
    
    imagen = fields.Binary(
        string='Imagen',
        attachment=True
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
    
    color = fields.Integer(
        string='Color',
        help='Color para identificar el activo'
    )
    
    @api.depends('valor_compra', 'valor_estimado')
    def _compute_depreciacion(self):
        for record in self:
            if record.valor_compra and record.valor_estimado:
                record.depreciacion = record.valor_compra - record.valor_estimado
                if record.valor_compra > 0:
                    record.porcentaje_depreciacion = (record.depreciacion / record.valor_compra) * 100
                else:
                    record.porcentaje_depreciacion = 0.0
            else:
                record.depreciacion = 0.0
                record.porcentaje_depreciacion = 0.0
    
    @api.constrains('valor_compra', 'valor_estimado')
    def _check_valores(self):
        for record in self:
            if record.valor_compra and record.valor_compra < 0:
                raise ValidationError('El valor de compra no puede ser negativo')
            if record.valor_estimado and record.valor_estimado < 0:
                raise ValidationError('El valor estimado no puede ser negativo')
    
    def action_marcar_vendido(self):
        """Marca el activo como vendido (inactivo)"""
        self.ensure_one()
        self.write({
            'active': False,
            'puede_venderse': False
        })
        return True
    
    def action_actualizar_valor(self):
        """Abre el formulario para actualizar el valor estimado"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Actualizar Valor',
            'res_model': 'diogenes.activo',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
