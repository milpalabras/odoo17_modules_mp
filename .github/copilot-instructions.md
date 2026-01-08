# Instrucciones para el Agente - Desarrollador de Módulos Odoo 17

## Rol y Contexto

Eres un desarrollador experto de módulos personalizados para **Odoo 17**, trabajando en un entorno de servidor local alojado en otra PC mediante **Portainer** (contenedores Docker).

## Entorno de Desarrollo

- **Versión de Odoo**: 17.0
- **Infraestructura**: Servidor local en PC remota
- **Gestión de contenedores**: Portainer
- **Workspace local**: `c:\Users\Sergio\Documents\odoo17_modules_mp`
- **Directorio de módulos**: `modules/`

## Configuración del Stack Docker (Portainer)

El servidor Odoo corre en contenedores Docker gestionados por Portainer con la siguiente configuración:

### Servicios:

1. **odoo17** (contenedor principal)
   - Imagen: `odoo:17.0`
   - Puerto: `8069:8069`
   - Volúmenes montados:
     - `/docker/odoo/config:/etc/odoo` - Configuración
     - `/docker/odoo/addons:/mnt/extra-addons` - **Módulos personalizados** (aquí se clona el repositorio)
     - `/docker/odoo/backups:/mnt/backups` - Backups
     - `/docker/odoo/logs:/mnt/logs` - Logs
     - `/docker/odoo/geoip:/usr/share/GeoIP/` - GeoIP
   - Variables de entorno:
     - `HOST=postgres`
     - `USER=odoo`
     - `PASSWORD=<tu_password>`

2. **postgres** (base de datos)
   - Imagen: `postgres:15`
   - Puerto: `5432:5432`
   - Max conexiones: 300
   - Shared memory: 4GB

3. **pgweb** (administrador de BD web)
   - Puerto: `8081:8081`
   - Interfaz web para gestionar PostgreSQL

### Stack completo:

```yaml
services:
  odoo:
    container_name: odoo17
    image: odoo:17.0
    labels:
      - "app=odoo"
      - "tier=frontend"
    depends_on:
      - postgres
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - /docker/odoo/config:/etc/odoo
      - /docker/odoo/addons:/mnt/extra-addons
      - /docker/odoo/backups:/mnt/backups
      - /docker/odoo/logs:/mnt/logs
      - /docker/odoo/geoip:/usr/share/GeoIP/
    environment:
      - HOST=postgres
      - USER=odoo
      - PASSWORD=<tu_password>
    restart: unless-stopped     
   
  postgres:
    container_name: postgres
    image: postgres:15
    labels:
      - "app=odoo"
      - "tier=database"
    shm_size: 4gb
    command: postgres -c "max_connections=300"
    ports:
      - 5432:5432
    environment:
      - POSTGRES_DB=postgres      
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
      - POSTGRES_PASSWORD=<tu_password>
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata    
    restart: unless-stopped

  pgweb:
    container_name: pgweb
    restart: always  
    image: sosedoff/pgweb
    labels:
      - "app=odoo"
      - "tier=admin"
    ports: 
      - "8081:8081" 
    environment:
      - DATABASE_URL=postgres://odoo:<tu_password>@postgres:5432/postgres?sslmode=disable
    depends_on:
      - postgres

volumes:
  odoo-web-data:
  odoo-db-data:
```

**Nota importante**: Los módulos personalizados se clonan/actualizan en `/docker/odoo/addons/` en el servidor, que está montado como `/mnt/extra-addons` dentro del contenedor.

## Estructura de Módulos Odoo

Cada módulo debe seguir la estructura estándar de Odoo:

```
nombre_modulo/
├── __init__.py                 # Importaciones de paquetes
├── __manifest__.py             # Descriptor del módulo
├── models/                     # Modelos de datos
│   ├── __init__.py
│   └── modelo.py
├── views/                      # Vistas XML
│   ├── menu.xml
│   └── vistas.xml
├── security/                   # Permisos y grupos
│   └── ir.model.access.csv
├── data/                       # Datos demo y maestros
│   └── demo_data.xml
├── static/                     # Recursos estáticos
│   ├── description/
│   │   ├── index.html
│   │   └── icon.png
│   └── src/
│       ├── css/
│       ├── js/
│       └── xml/
├── controllers/                # Controladores web
│   ├── __init__.py
│   └── main.py
├── wizards/                    # Asistentes
│   ├── __init__.py
│   └── wizard.py
└── reports/                    # Informes
    ├── __init__.py
    └── reporte.xml
```

## Archivo __manifest__.py

Estructura estándar del manifiesto:

```python
{
    'name': 'Nombre del Módulo',
    'version': '17.0.1.0.0',
    'category': 'Categoría',
    'summary': 'Descripción breve',
    'description': """
        Descripción detallada del módulo
    """,
    'author': 'Nombre del autor',
    'website': 'https://www.ejemplo.com',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'stock'],  # Dependencias
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/vistas.xml',
        'data/demo_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Modelos en Odoo 17

### Estructura básica de un modelo:

```python
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class MiModelo(models.Model):
    _name = 'mi.modulo.modelo'
    _description = 'Descripción del Modelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Opcional
    _order = 'name asc'
    _rec_name = 'name'
    
    # Campos
    name = fields.Char(string='Nombre', required=True, tracking=True)
    description = fields.Text(string='Descripción')
    date = fields.Date(string='Fecha', default=fields.Date.today)
    amount = fields.Float(string='Monto', digits=(16, 2))
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Hecho'),
        ('cancel', 'Cancelado'),
    ], string='Estado', default='draft', tracking=True)
    
    # Relaciones
    partner_id = fields.Many2one('res.partner', string='Cliente')
    line_ids = fields.One2many('mi.modulo.linea', 'parent_id', string='Líneas')
    tag_ids = fields.Many2many('mi.modulo.tag', string='Etiquetas')
    
    # Campos computados
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    
    # Constrains SQL
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'El nombre debe ser único'),
    ]
    
    # Métodos computados
    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.line_ids.mapped('amount'))
    
    # Validaciones
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError('El monto no puede ser negativo')
    
    # Onchanges
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.description = self.partner_id.name
    
    # Métodos CRUD
    @api.model
    def create(self, vals):
        # Lógica antes de crear
        record = super(MiModelo, self).create(vals)
        # Lógica después de crear
        return record
    
    def write(self, vals):
        # Lógica antes de escribir
        result = super(MiModelo, self).write(vals)
        # Lógica después de escribir
        return result
    
    def unlink(self):
        # Validaciones antes de eliminar
        if any(rec.state == 'done' for rec in self):
            raise UserError('No se puede eliminar un registro finalizado')
        return super(MiModelo, self).unlink()
    
    # Métodos de acción
    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'confirmed'})
        return True
```

## Vistas XML

### Vista Form:

```xml
<record id="view_mi_modelo_form" model="ir.ui.view">
    <field name="name">mi.modulo.modelo.form</field>
    <field name="model">mi.modulo.modelo</field>
    <field name="arch" type="xml">
        <form string="Mi Modelo">
            <header>
                <button name="action_confirm" string="Confirmar" 
                        type="object" states="draft" 
                        class="oe_highlight"/>
                <field name="state" widget="statusbar" 
                       statusbar_visible="draft,confirmed,done"/>
            </header>
            <sheet>
                <div class="oe_title">
                    <h1>
                        <field name="name" placeholder="Nombre..."/>
                    </h1>
                </div>
                <group>
                    <group>
                        <field name="partner_id"/>
                        <field name="date"/>
                    </group>
                    <group>
                        <field name="amount"/>
                        <field name="active"/>
                    </group>
                </group>
                <notebook>
                    <page string="Líneas">
                        <field name="line_ids">
                            <tree editable="bottom">
                                <field name="name"/>
                                <field name="amount"/>
                            </tree>
                        </field>
                    </page>
                </notebook>
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### Vista Tree:

```xml
<record id="view_mi_modelo_tree" model="ir.ui.view">
    <field name="name">mi.modulo.modelo.tree</field>
    <field name="model">mi.modulo.modelo</field>
    <field name="arch" type="xml">
        <tree string="Mi Modelo">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="amount"/>
            <field name="state" widget="badge" 
                   decoration-success="state=='done'"
                   decoration-info="state=='confirmed'"
                   decoration-muted="state=='cancel'"/>
        </tree>
    </field>
</record>
```

### Vista Search:

```xml
<record id="view_mi_modelo_search" model="ir.ui.view">
    <field name="name">mi.modulo.modelo.search</field>
    <field name="model">mi.modulo.modelo</field>
    <field name="arch" type="xml">
        <search string="Buscar">
            <field name="name"/>
            <field name="partner_id"/>
            <filter string="Activos" name="active" domain="[('active','=',True)]"/>
            <filter string="Borradores" name="draft" domain="[('state','=','draft')]"/>
            <separator/>
            <filter string="Fecha" name="group_date" context="{'group_by':'date'}"/>
            <filter string="Cliente" name="group_partner" context="{'group_by':'partner_id'}"/>
        </search>
    </field>
</record>
```

## Menús

```xml
<menuitem id="menu_mi_modulo_root"
          name="Mi Módulo"
          sequence="10"/>

<menuitem id="menu_mi_modulo_main"
          name="Principal"
          parent="menu_mi_modulo_root"
          sequence="10"/>

<menuitem id="menu_mi_modelo"
          name="Mi Modelo"
          parent="menu_mi_modulo_main"
          action="action_mi_modelo"
          sequence="10"/>
```

## Acciones

```xml
<record id="action_mi_modelo" model="ir.actions.act_window">
    <field name="name">Mi Modelo</field>
    <field name="res_model">mi.modulo.modelo</field>
    <field name="view_mode">tree,form</field>
    <field name="context">{'search_default_active': 1}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Crear el primer registro
        </p>
    </field>
</record>
```

## Seguridad (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_mi_modelo_user,mi.modulo.modelo.user,model_mi_modulo_modelo,base.group_user,1,1,1,1
access_mi_modelo_manager,mi.modulo.modelo.manager,model_mi_modulo_modelo,base.group_system,1,1,1,1
```

## Controladores Web

```python
from odoo import http
from odoo.http import request

class MiControlador(http.Controller):
    
    @http.route('/mi_modulo/endpoint', type='json', auth='user')
    def mi_endpoint(self, **kwargs):
        data = request.env['mi.modulo.modelo'].search_read([], ['name'])
        return {'status': 'success', 'data': data}
    
    @http.route('/mi_modulo/web', type='http', auth='public', website=True)
    def mi_pagina_web(self, **kwargs):
        return request.render('mi_modulo.template_web', {})
```

## Buenas Prácticas

1. **Nomenclatura**:
   - Modelos: snake_case (`mi_modulo.modelo`)
   - Clases Python: PascalCase (`MiModelo`)
   - Variables/métodos: snake_case (`mi_metodo`)
   - IDs XML: snake_case con prefijos (`view_mi_modelo_form`)

2. **Performance**:
   - Usar `search_read()` en lugar de `search()` + `read()`
   - Evitar búsquedas en loops
   - Usar campos computados con `store=True` cuando sea apropiado
   - Utilizar `@api.depends()` correctamente

3. **Seguridad**:
   - Siempre definir reglas de acceso en `ir.model.access.csv`
   - Usar `sudo()` con precaución
   - Validar datos de entrada

4. **Testing**:
   - Probar siempre en modo desarrollador
   - Verificar logs para errores
   - Hacer pruebas de actualización del módulo

## Comandos Útiles (Portainer/Docker)

### Comandos de Docker (en servidor remoto):

```bash
# Ver logs del contenedor (seguimiento en tiempo real)
docker logs -f odoo17

# Ver logs recientes
docker logs --tail 100 odoo17

# Acceder al shell del contenedor
docker exec -it odoo17 bash

# Ver estado de contenedores
docker ps

# Reiniciar contenedor específico
docker restart odoo17

# Reiniciar todo el stack
docker restart odoo17 postgres pgweb
```

### Comandos de Odoo (dentro del contenedor):

```bash
# Actualizar módulo existente
odoo-bin -u nombre_modulo -d nombre_base_datos --stop-after-init

# Instalar módulo nuevo
odoo-bin -i nombre_modulo -d nombre_base_datos --stop-after-init

# Actualizar múltiples módulos
odoo-bin -u modulo1,modulo2,modulo3 -d nombre_base_datos --stop-after-init

# Shell interactivo de Odoo (para debugging)
odoo-bin shell -d nombre_base_datos

# Ver lista de bases de datos
odoo-bin db --list
```

### Comandos de Git (en servidor):

```bash
# Navegar a la carpeta de addons personalizados
cd /docker/odoo/addons

# Clonar repositorio (primera vez) - Comando específico para este proyecto:
git clone https://github.com/milpalabras/odoo17_modules_mp.git

# Actualizar desde GitHub
cd /docker/odoo/addons/odoo17_modules_mp
git pull origin main

# Ver estado del repositorio
git status

# Ver últimos commits
git log --oneline -10

# Cambiar a una rama específica
git checkout nombre_rama
```

## Workflow de Desarrollo

Este es el flujo de trabajo completo para desarrollar y desplegar módulos:

### 1. Desarrollo Local
- **Workspace local**: `c:\Users\Sergio\Documents\odoo17_modules_mp\modules\`
- Crear/modificar módulos en la carpeta `modules/`
- Seguir la estructura estándar de Odoo (ver ejemplo en `modulo_prueba/`)
- Probar localmente si es posible

### 2. Control de Versiones (GitHub)
```bash
# Agregar cambios
git add modules/nombre_modulo/

# Commit con mensaje descriptivo
git commit -m "feat: agregar funcionalidad X al módulo Y"

# Subir a GitHub
git push origin main
```

**Buenas prácticas de commits**:
- `feat:` para nuevas funcionalidades
- `fix:` para correcciones de bugs
- `refactor:` para refactorización de código
- `docs:` para documentación
- Ejemplo: `feat: agregar modelo de inventario en modulo_almacen`

### 3. Despliegue en Servidor
En el servidor remoto (vía SSH o terminal de Portainer):

```bash
# Navegar a la carpeta de addons personalizados de Odoo
cd /docker/odoo/addons

# Si es la primera vez, clonar el repositorio
git clone https://github.com/milpalabras/odoo17_modules_mp.git

# Si ya existe, actualizar
cd odoo17_modules_mp
git pull origin main

# Asegurar permisos correctos
chmod -R 755 modules/
chown -R odoo:odoo modules/  # ajustar según tu configuración
```

### 4. Reiniciar y Actualizar
Desde **Portainer**:
- Ir al contenedor `odoo17`
- Clic en "Restart" para reiniciar el servicio

O desde **línea de comandos**:
```bash
# Reiniciar contenedor de Odoo
docker restart odoo17

# O reiniciar todo el stack
docker restart odoo17 postgres pgweb
```

### 5. Instalar/Actualizar en Odoo
Desde la **interfaz web de Odoo**:
1. Ir a `Settings → Apps`
2. Activar modo desarrollador: `Settings → Developer Mode`
3. Click en "Update Apps List" (actualizar lista de módulos)
4. Buscar tu módulo
5. Hacer click en "Install" o "Upgrade"

O desde **CLI** (dentro del contenedor):
```bash
# Instalar módulo nuevo
odoo-bin -i nombre_modulo -d nombre_base_datos --stop-after-init

# Actualizar módulo existente
odoo-bin -u nombre_modulo -d nombre_base_datos --stop-after-init
```

### 6. Verificación y Testing
- **Ver logs**: En Portainer → Logs del contenedor
- **Probar funcionalidad**: Navegar al módulo en Odoo
- **Revisar errores**: Check logs y modo desarrollador
- **Verificar datos demo**: Si están definidos en `data/demo_data.xml`

### 7. Iterar
Si hay errores o cambios necesarios:
1. Volver a desarrollo local
2. Hacer modificaciones
3. Commit y push a GitHub
4. Pull en servidor
5. Actualizar módulo en Odoo (`-u nombre_modulo`)

## Estructura de Referencia

El módulo `modulo_prueba` en este workspace es un ejemplo de referencia que incluye:

```
modulo_prueba/
├── __init__.py                 # Imports del módulo
├── __manifest__.py             # Metadatos y configuración
├── models/
│   ├── __init__.py
│   └── prueba_model.py        # Modelo con ejemplos de campos
├── views/
│   ├── menu.xml               # Definición de menús
│   └── prueba_views.xml       # Vistas tree, form, search
├── security/
│   └── ir.model.access.csv    # Permisos de acceso
├── data/
│   └── demo_data.xml          # Datos de demostración
└── static/
    ├── description/
    │   └── index.html         # Descripción del módulo
    └── src/
        └── css/
            └── style.css      # Estilos personalizados
```

### Características del módulo de referencia:
- **Campos básicos**: Char, Text, Boolean, Selection, Datetime
- **Relaciones**: Many2one (usuarios), Many2many (tags)
- **Widgets**: priority, progressbar, many2many_tags
- **Métodos**: acción personalizada `action_complete`
- **Assets**: CSS personalizado cargado correctamente
- **Demo data**: Registros de ejemplo para testing

## Acceso al Servidor Odoo

- **URL típica**: `http://IP_SERVIDOR:8069`
- **Modo desarrollador**: Settings → Activate Developer Mode
- **Actualizar lista de apps**: Apps → Update Apps List

## Debugging

- Activar modo desarrollador con assets: `?debug=assets`
- Ver logs de Python en Portainer
- Usar `_logger.info()` para debug:

```python
import logging
_logger = logging.getLogger(__name__)

_logger.info('Debug info: %s', variable)
```

## Recursos Adicionales

- Documentación oficial: https://www.odoo.com/documentation/17.0/
- OCA (Odoo Community Association): https://github.com/OCA
- Odoo Apps Store: https://apps.odoo.com/

---

**Nota**: Siempre seguir las convenciones de Odoo y mantener el código limpio, comentado y bien estructurado.
