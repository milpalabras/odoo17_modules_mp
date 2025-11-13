# -*- coding: utf-8 -*-
{
    'name': 'Módulo de Prueba',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Módulo de prueba para testing y desarrollo',
    'description': """
        Módulo de Prueba - Sergio Milpalabras
        ====================================
        
        Este es un módulo de prueba creado para:
        * Verificar que Odoo reconoce módulos personalizados
        * Servir como base para desarrollo
        * Testing de funcionalidades básicas
        
        Características:
        * Modelo simple de demostración
        * Vista de lista y formulario
        * Menú en la aplicación
    """,
    'author': 'Sergio Milpalabras',
    'website': 'https://github.com/milpalabras',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/prueba_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'modulo_prueba/static/src/css/style.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}
