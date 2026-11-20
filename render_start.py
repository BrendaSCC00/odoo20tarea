"""Configuración y arranque de la tarea de Odoo en Render."""
import configparser
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import unquote, urlparse


def database_settings(database_url):
    url = urlparse(database_url)
    database = unquote(url.path.lstrip('/'))
    if url.scheme not in ('postgres', 'postgresql') or not url.hostname:
        raise ValueError('DATABASE_URL debe ser una conexión PostgreSQL válida.')
    if not database or not url.username or not url.password:
        raise ValueError('La conexión debe incluir base de datos, usuario y contraseña.')
    return {
        'host': url.hostname,
        'port': url.port or 5432,
        'user': unquote(url.username),
        'password': unquote(url.password),
        'dbname': database,
    }


def write_config(settings, path):
    parser = configparser.ConfigParser(interpolation=None)
    parser['options'] = {
        'addons_path': '/opt/odoo-project/addons,/opt/odoo-project/odoo/addons,/mnt/extra-addons',
        'data_dir': '/var/lib/odoo',
        'admin_passwd': os.environ['ODOO_MASTER_PASSWORD'],
        'db_host': settings['host'],
        'db_port': str(settings['port']),
        'db_user': settings['user'],
        'db_password': settings['password'],
        'db_name': settings['dbname'],
        'dbfilter': '^' + re.escape(settings['dbname']) + '$',
        'db_sslmode': 'require',
        'db_maxconn': '8',
        'list_db': 'False',
        'proxy_mode': 'True',
        'http_interface': '0.0.0.0',
        'http_port': os.environ.get('PORT', '10000'),
        'workers': '0',
        'max_cron_threads': '0',
        'limit_time_cpu': '180',
        'limit_time_real': '300',
    }
    with open(path, 'w', encoding='utf-8') as target:
        parser.write(target)
    Path(path).chmod(0o600)


BOOTSTRAP = '''
import os
params = env['ir.config_parameter'].sudo()
params.set_param('ir_attachment.location', 'db')
env['ir.attachment'].sudo().force_storage()
if not params.get_param('tarea_nube.configurada'):
    admin = env.ref('base.user_admin')
    admin.write({
        'name': 'Revisión académica',
        'login': os.environ.get('ODOO_ADMIN_LOGIN', 'revision'),
        'password': os.environ['ODOO_ADMIN_PASSWORD'],
    })
    env.ref('base.main_company').write({'name': 'Odoo_BrendaCuellar'})
    params.set_param('tarea_nube.configurada', '1')
env.cr.commit()
print('Configuración de la tarea verificada.')
'''


def main():
    import psycopg2
    settings = database_settings(os.environ['DATABASE_URL'])
    if len(os.environ['ODOO_ADMIN_PASSWORD']) < 16:
        raise ValueError('La contraseña inicial debe tener al menos 16 caracteres.')
    config_path = '/tmp/odoo-render.conf'
    write_config(settings, config_path)
    connection = None
    for attempt in range(60):
        try:
            connection = psycopg2.connect(**settings, sslmode='require', connect_timeout=5)
            break
        except psycopg2.OperationalError:
            if attempt == 59:
                raise RuntimeError('PostgreSQL no está disponible; revisar la conexión.') from None
            time.sleep(2)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.ir_module_module')")
            initialized = bool(cursor.fetchone()[0])
            modules_ready = False
            if initialized:
                cursor.execute(
                    "SELECT count(*) FROM ir_module_module "
                    "WHERE name IN ('base', 'ventas_unicah') AND state = 'installed'"
                )
                modules_ready = cursor.fetchone()[0] == 2
    connection.close()
    command = [sys.executable, '/opt/odoo-project/odoo-bin']
    if not modules_ready:
        print('Instalando la base y el módulo de la tarea.', flush=True)
        subprocess.run(command + [
            '-c', config_path, '-i', 'base,ventas_unicah',
            '--without-demo=all', '--load-language=es_ES',
            '--stop-after-init', '--no-http',
        ], check=True)
    subprocess.run(
        command + ['shell', '-c', config_path, '--no-http'],
        input=BOOTSTRAP, text=True, check=True,
    )
    print('Odoo disponible para la revisión.', flush=True)
    os.execv(sys.executable, command + ['-c', config_path])


if __name__ == '__main__':
    main()
