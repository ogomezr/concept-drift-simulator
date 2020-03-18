# Adaptative Algorithm Simulator (Concept Drift)

Es una aplicación que utiliza los algoritmos implementados en las librerías [Algoritmo Adaptativo](https://github.com/ogomezr/concept-drift-library) con una finalidad de ofrecer una herramienta educativa y de exploración con los diferentes parámetros disponibles y la creación de diferentes sets de datos de manera sencilla.


<p>&nbsp;</p>
<p align="center">
  <img src="img/mainApp.jpeg">
</p>
<p>&nbsp;</p>

##  Instrucciones de uso con Docker

La manera más sencilla de utilizar la aplicación es con el uso de Docker.
* [Instalación Docker](https://docs.docker.com/install/)

Una vez disponemos de docker, ejecutamos el contenedor con el comando:

```
sudo docker run -it --rm  -p 8050:8050 ogomezr/concept-drift-simulator
```

De esta manera, no es necesario descargar el repositorio ni la instalación de librerías adicionales.

Para acceder a la aplicación acceder desde tu navegador a la url:

```
http://0.0.0.0:8050/
```
Para cambiar de puerto se debe cambiar el puerto en la comando de ejecución del contenedor.

## Instrucciones de uso para ejecutar la aplicación localmente.

### Pre-requisitos 📋
Para utilizar esta librerías es necesario disponer de Python instalado en tu equipo. 
* [Python](https://www.python.org/downloads/)

Una vez disponemos de Python, descargar el repositorio desde GitHub o usando desde la consola el comando:

```
git clone https://github.com/ogomezr/concept-drift-simulator
```


### Instalación 🔧

#### Paso 1
Acceso a la carpeta del repositorio.
```
cd concept-drift-simulator
```
#### Paso 2 ( Opcional ) 
Uso de entorno virtual para la instalación del proyecto y librerías necesarias

Creación entorno virtual desde la línea de comandos:
```
python -m venv conceptdrift
```
Activación entorno virtual (Linux/Mac):

```
source ./conceptdrift/bin/activate
```
Activación entorno virtual (Win):

```
./conceptdrift/Scripts/activate
```

#### Paso 3
Instalación de las librerías necesarias:
```
pip install -r requirements.txt
```

#### Paso 4

Ejecución en modo Producción:

```
gunicorn -b 0.0.0.0.8050 app:server
```

Ejecución en modo desarrollo (NO RECOMENDADA : la aplicación funciona de manera menos eficiente.)

```
python app.py
```

#### Paso 5
Abrimos la siguiente url en el navegador:
```
http://0.0.0.0:8050/
```

## Autor ✒️

* *Óscar Gómez* - [ogomezr](https://github.com/ogomezr)
 
## Licencia 📄

Este proyecto está bajo la Licencia MIT - más detalles en el archivo LICENSE.
