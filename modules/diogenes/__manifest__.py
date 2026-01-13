# -*- coding: utf-8 -*-
{
    'name': 'Diógenes - Finanzas Personales',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Gestión de finanzas personales para alcanzar la libertad financiera',
    'description': """
        Diógenes - Finanzas Personales
        ===============================
        
        Aplicación que ayuda a mantener un registro de gastos e ingresos 
        para alcanzar la libertad financiera.
        
        Características principales:
        * Seguimiento de gastos e ingresos: Registra y categoriza fácilmente 
          tus transacciones para tener una visión clara de tus finanzas
        * Presupuesto personalizado: Establece presupuestos basados en tus 
          metas financieras y realiza un seguimiento de tu progreso
        * Planificación financiera: Crea y visualiza planes a largo plazo, 
          incluyendo metas de ahorro, inversión y planificación para la jubilación
        
        Módulos incluidos:
        * Transacciones (ingresos y gastos)
        * Categorías personalizables
        * Presupuestos mensuales
        * Metas financieras a largo plazo
    """,
    'author': 'Sergio Milpalabras',
    'website': 'https://github.com/milpalabras',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/categorias_default.xml',
        'data/cuentas_default.xml',
        'views/cuenta_views.xml',
        'views/transaccion_views.xml',
        'views/categoria_views.xml',
        'views/presupuesto_views.xml',
        'views/meta_financiera_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}
