Eclipse IDE
===========

Aquí se listan las instrucciones para instalar y configurar Eclipse como IDE para OpenERP

Instalación en ubuntu 12.04
---------------------------
*   Instalar eclipse y el soporte para GIT ejecutando
    sudo apt-get install eclipse eclipse-egit
*   Instalar el módulo PyDEV para desarrollo en Python
    * Ingresar a la opción del menú **Help > Install New Software**
    * En el cuadro de dialogo diligenciar **Work with:** con el valor http://pydev.org/updates y presionar la tecla **enter**
    * Seleccionar en la lista que aparece luego de unos segundos **PyDEV** o el botón **Select All**
    * Presionar el botón **Next**
    * Presionar nuevamente el botón **Next**
    * Aceptar la licencia de usuario y presionar **Finish**
    * Se iniciará el proceso de descarga e instalación
    * Luego de unos minutos aparecerá un cuadro de dialogo preguntando si confia en el certificado, Clickea **Select All** y **OK**
    * Por último presiona el boton **Restart now** cuando se le pregunte
*   Instalar el módulo Web Tools para incluir editores para otras tecnologías web como XML, Javascript entre otros
    * Ingresar a la opción del menú **Help > Install New Software**
    * En el cuadro de dialogo diligenciar **Work with:** con el valor http://download.eclipse.org/webtools/repository/helios y presionar la tecla **enter**
    * Seleccionar en la lista que aparece seleccione los paquetes que desee para la versión **Web Tools Platform SDK (WTP SDK) 3.2.5**, como mínimo escoger
      * Eclipse XML Editors and Tools SDK 3.2.5
      * JavaScript Development Tools SDK 1.2.5
    * Presionar el botón **Next** y continuar como se hizo para el módulo PyDEV
