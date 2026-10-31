# Odoo 20 - tarea de clase

Proyecto basado en la rama 20.0 del repositorio oficial https://github.com/odoo/odoo . Se conservan su licencia y los avisos originales.

## Preparacion de esta computadora

Python 3.12 y las dependencias estan instalados en `.venv`. PostgreSQL 17 se ejecuta en Docker mediante `compose.clase.yml`.

Desde la carpeta del proyecto en la terminal de VS Code:

```powershell
.\Iniciar_Tarea2.cmd
```

El script crea o inicia el servicio de PostgreSQL de esta tarea, espera a que este listo y arranca Odoo en http://localhost:8070 . PostgreSQL se publica solo en 127.0.0.1:5433.

La primera vez, crear la base de pruebas `odoo20_clase` desde el navegador y elegir los datos del administrador. La clave maestra generada se encuentra en el campo `master` del archivo local `../Odoo20_entorno/credenciales_tarea2.json`.

## Al descargarlo en otra computadora

Instalar Python 3.12 y Docker Desktop, crear `.venv` con `python -m venv .venv`, activarlo e instalar `requirements.txt`. Luego ejecutar `Iniciar_Tarea2.cmd`. El entorno virtual y las contrasenas son locales; no se incluyen en GitHub. Las dependencias que no tengan binarios disponibles pueden requerir herramientas de compilacion de C++.

No se deben subir `odoo.conf`, `.odoo-docker.env`, `.env`, `.venv` ni archivos de credenciales. Los datos de PostgreSQL se conservan en un volumen Docker; el script no elimina contenedores ni volumenes.
