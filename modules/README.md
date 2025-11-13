# Módulos Personalizados de Odoo

Esta carpeta contiene los módulos personalizados desarrollados para Odoo 17.

## Estructura
Cada módulo debe tener la siguiente estructura:
```
mi_modulo/
├── __init__.py
├── __manifest__.py
├── models/
├── views/
├── data/
├── static/
└── security/
```

## Para agregar un nuevo módulo:
1. Crea una carpeta con el nombre de tu módulo
2. Desarrolla tu módulo siguiendo las mejores prácticas de Odoo
3. Haz commit de tus cambios

## Para usar en desarrollo local:
Los módulos en esta carpeta deben copiarse o enlazarse a:
- Docker: `./docker/odoo/addons/`
- Local: ruta de addons de tu instalación Odoo
