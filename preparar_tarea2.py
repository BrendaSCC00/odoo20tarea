"""Preparar PostgreSQL en Docker sin eliminar contenedores ni volumenes."""
from pathlib import Path
import json, secrets, subprocess, sys, time, socket

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT.parent / 'Odoo20_entorno'
CREDS = LOCAL / 'credenciales_tarea2.json'
def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)

def main():
    run(['docker', 'info'], stdout=subprocess.DEVNULL)
    found = subprocess.run(['docker','inspect','odoo20-clase-db'], capture_output=True, text=True)
    if found.returncode == 0:
        labels = json.loads(found.stdout)[0]['Config'].get('Labels') or {}
        if labels.get('com.docker.compose.project') != 'odoo20_clase':
            raise RuntimeError('Ya existe un contenedor con ese nombre que no pertenece a esta tarea. No se modifico.')
    if not CREDS.exists():
        CREDS.write_text(json.dumps({'db_password': secrets.token_urlsafe(24), 'master':secrets.token_urlsafe(24)},indent=2),encoding='utf8')
    creds=json.loads(CREDS.read_text(encoding='utf8'))
    (ROOT/'.odoo-docker.env').write_text('ODOO_DB_PASSWORD='+creds['db_password']+'\n',encoding='utf8')
    compose=['docker','compose','-p','odoo20_clase','--env-file','.odoo-docker.env','-f','compose.clase.yml']
    run(compose+['up','-d','db'])
    for _ in range(90):
        ready=subprocess.run(['docker','exec','odoo20-clase-db','pg_isready','-U','odoo','-d','postgres'],capture_output=True)
        if ready.returncode==0: break
        time.sleep(2)
    else: raise RuntimeError('PostgreSQL no esta listo. Revisa Docker Desktop; no se borraron datos.')
    run(['docker','exec','odoo20-clase-db','postgres','--version'])
    run(['docker','port','odoo20-clase-db','5432'])
    # 8070 mantiene disponible la instalacion anterior en 8069.
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',8070)) == 0:
            raise RuntimeError('El puerto 8070 ya esta ocupado. No se detuvo ningun programa.')
    (ROOT/'odoo.conf').write_text('[options]\nadmin_passwd = '+creds['master']+'\ndb_host = 127.0.0.1\ndb_port = 5433\ndb_user = odoo\ndb_password = '+creds['db_password']+'\naddons_path = addons\nhttp_interface = 127.0.0.1\nhttp_port = 8070\ndata_dir = '+(LOCAL/'odoo_data_docker').as_posix()+'\n',encoding='utf8')
    print('\nAbre http://localhost:8070 . Crea la base odoo20_clase y tu usuario de administrador.')
    print('La clave maestra es el campo master en: '+str(CREDS))
    print('No compartas los archivos con claves ni los subas a GitHub.\n')
    return subprocess.call([sys.executable,'odoo-bin','-c','odoo.conf'],cwd=ROOT)

if __name__=='__main__':
    try: sys.exit(main())
    except (RuntimeError, subprocess.CalledProcessError, FileNotFoundError) as exc:
        print('No se pudo completar la preparacion:',exc)
        sys.exit(1)
