# CHRONO-MATE

> Herramienta para cargar horas en jira de forma automagica

![alt text](img/chronomate.png)

## REQUERIMIENTOS

* **Docker**
* **Python 3.8+**

## EJECUCION

### DOCKER

* Pararse en la ruta raiz del proyecto con docker instalado y ejecutar:
```bash
chmod +x run_dockerized.sh
./run_dockerized.sh files/config.yml #En caso de no tener el parametro lo busca por default en ese mismo path
```
o tambien se puede ejecutar directamente con docker: 
```bash
docker run --network=host -it -v $(pwd)/files:/usr/src/files \
chrono-mate /usr/src/files/config.yml
```
### NATIVO

* Pararse en la ruta raiz del proyecto con Python instalado y ejecutar:
```
pip install -r requirements.txt
python app.py files/config.yml
```

## CONFIGURACION

### AUTH
La clave "auth" contiene las credenciales necesarias para conectarse a Jira. Esta clave contiene dos subclaves:

* **username**: El nombre de usuario utilizado para conectarse a Jira.
* **password**: La contraseña utilizada para conectarse a Jira.

Ejemplo:

```yaml
auth:
  username: miUsuario
  password: miContraseña
```

### SPECIAL_TASKS
La clave "special_tasks" es un mapa clave-valor que relaciona una etiqueta con un issue de Jira. Cada etiqueta está representada por una clave, mientras que su valor corresponde a un issue de Jira.

Ejemplo:

```yaml
special_tasks:
  soporte_development: SP18-291
  soporte_qa: SP18-292
  soporte_prod: SP18-285
  implementaciones: SP18-286
  vacaciones: SP18-287
  tramite_personal: SP18-288
  examenes: SP18-289
  enfermedad: SP18-290
  reuniones: SP18-294
```

### CALENDAR
La clave "calendar" contiene información sobre la fecha actual y los días de inicio y fin de la semana. Esta clave contiene tres subclaves:

* **today**: La fecha actual en formato "YYYY-MM-DD" (Opcional).
* **first_day**: El primer día de la semana (ejemplo: "lunes").
* **last_day**: El último día de la semana (ejemplo: "viernes").

Ejemplo:

```yaml
calendar:
  today: "2023-03-30"
  first_day: lunes 
  last_day:  viernes
```

### HOURS
La clave "hours" contiene información sobre cómo se distribuyen las horas de trabajo en la semana. Esta clave contiene subclaves que indican la cantidad de horas de trabajo para cada tarea. Las horas pueden ser especificadas como un monto fijo o un porcentaje de la jornada laboral.

Ejemplo:

```yaml
hours:
  soporte_development: 20%
  soporte_qa: 0%
  soporte_prod: 0%
  reuniones: 10hs
  vacaciones: 0%
  enfermedad: 0%
  tareas: 60%
```

### TASKS
Incluye información sobre los valores mínimos, medios y altos de las horas de trabajo diarias y el nombre del tablero Kanban utilizado por la aplicación.

* **issues_key**: Esta es la key dentro de ***hours*** de la cual se usara como *"palabra reservada"* para referirse a las tareas de los kanban que no sean ***special_tasks***.
* **daily_hours**: El número de horas de trabajo diarias.
* **lower_hours**: El número mínimo de horas de trabajo semanales para tareas.
* **medium_hours**: El número medio de horas de trabajo semanales para tareas.
* **high_hours**: El número maximo de horas de trabajo semanales para tareas.
* **kanban_boards**: Una lista que contiene el nombre del tablero Kanban utilizado por la aplicación.

Ejemplo:

```yaml
tasks:
  issues_key: tareas
  daily_hours: 8hs
  lower_hours: 1hs
  medium_hours: 8hs
  high_hours: 16hs
  kanban_boards:
    - SP18
```

### DRY_RUN
La clave "dry_run" indica si la aplicación se ejecuta en modo de prueba o no. Si esta clave está presente y su valor es "true", la aplicación se ejecutará en modo de prueba (no se cargaran las horas en jira).

Ejemplo:

```yaml
dry_run: true
```
