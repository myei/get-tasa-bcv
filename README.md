# get-tasa-bcv.py

Script para consultar las tasas de cambio oficiales del Banco Central de Venezuela (BCV) con soporte para notificaciones del sistema y almacenamiento local.

## 📋 Características

- ✅ Consulta automática de tasas USD y EUR del BCV
- ✅ Soporte para Chrome y Firefox
- ✅ Notificaciones del sistema (Linux)
- ✅ Base de datos local SQLite para caché
- ✅ Múltiples formatos de salida
- ✅ Ejecutable standalone (sin dependencias)
- ✅ Compatible con crontab para automatización

## 🔧 Requisitos

### Opción 1: Ejecutar desde código fuente
- Python 3.9+ (compatible con 3.12)
- Chrome o Firefox instalado
- ChromeDriver o GeckoDriver en el PATH del sistema

### Opción 2: Usar ejecutable standalone
- Solo Chrome o Firefox instalado
- No requiere Python ni dependencias adicionales

## 📦 Instalación

### Método 1: Desde código fuente

```bash
# Clonar el repositorio
git clone https://github.com/myei/get-tasa-bcv.git
cd get-tasa-bcv

# Crear entorno virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Método 2: Generar ejecutable standalone

```bash
# Desde el directorio del proyecto con entorno virtual activado
pip install pyinstaller

# Generar ejecutable con soporte completo para notificaciones
pyinstaller --onefile \
    --name=get-tasa-bcv \
    --hidden-import=plyer.platforms.linux.notification \
    --hidden-import=plyer.platforms.linux \
    --hidden-import=plyer.platforms \
    --hidden-import=plyer.facades.notification \
    get-tasa-bcv.py

# El ejecutable se genera en: ./dist/get-tasa-bcv
```

## 🚀 Uso

### Opciones disponibles

```bash
python get-tasa-bcv.py [opciones]

# O usando el ejecutable:
./dist/get-tasa-bcv [opciones]
```

**Opciones:**
- `-c` : Usar Google Chrome (por defecto)
- `-f` : Usar Mozilla Firefox  
- `-s` : Formato de salida corto
- `-u` : Solo mostrar tasa del Dólar (USD)
- `-e` : Solo mostrar tasa del Euro (EUR)
- `-n` : Generar notificación en pantalla
- `--nc` : Generar notificación solo cuando las tasas cambian
- `--force` : Forzar nueva consulta (ignorar caché)
- `-h` : Mostrar ayuda

### Ejemplos de uso

```bash
# Consulta básica
python get-tasa-bcv.py

# Con notificación
python get-tasa-bcv.py -n

# En formato corto
python get-tasa-bcv.py -s

# Usando Firefox
python get-tasa-bcv.py -f

# Forzar nueva consulta con notificación
python get-tasa-bcv.py -n --force

# Usando el ejecutable con notificación
./dist/get-tasa-bcv -n
```

## 🗄️ Almacenamiento de datos

La base de datos SQLite se almacena en:
```
~/.get-tasa-bcv/bcv_rates.db
```

Esto permite:
- Caché de consultas por fecha
- Evitar consultas repetidas el mismo día
- Historial de tasas consultadas

## ⏰ Automatización con Crontab

### Para el script Python:
```bash
# Editar crontab
crontab -e

# Consultar cada 30 minutos con notificación (requiere entorno virtual)
30 * * * * DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus cd /ruta/al/proyecto && .venv/bin/python get-tasa-bcv.py --nc --force
```

### Para el ejecutable standalone:
```bash
# Editar crontab  
crontab -e

# Consultar cada 30 minutos con notificación (sin dependencias)
30 * * * * DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus /ruta/al/proyecto/dist/get-tasa-bcv --nc --force
```

**Nota:** Las variables `DISPLAY` y `DBUS_SESSION_BUS_ADDRESS` son necesarias para que las notificaciones funcionen correctamente en crontab.

## 🛠️ Solución de problemas

### Error: "externally-managed-environment"
Usa el ejecutable standalone o crea un entorno virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: "ChromeDriver version mismatch"
Actualiza ChromeDriver o usa Firefox:
```bash
python get-tasa-bcv.py -f
```

### Error: "No module named 'plyer.platforms'"
Regenera el ejecutable con los hidden-imports correctos (ver sección de instalación).

### Las notificaciones no aparecen en crontab
Asegúrate de incluir las variables de entorno `DISPLAY` y `DBUS_SESSION_BUS_ADDRESS` en tu configuración de crontab (ver ejemplos de automatización).

## 📸 Ejemplos de ejecución

![Ejemplo de ayuda y usos](https://github.com/myei/get-tasa-bcv/blob/master/examples/usage.png?raw=true)

![Ejemplo de notificación](https://github.com/myei/get-tasa-bcv/blob/master/examples/popup.png?raw=true)

## 📄 Dependencias

- `selenium==4.19.0` - Web scraping del sitio del BCV
- `plyer` - Notificaciones del sistema

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
