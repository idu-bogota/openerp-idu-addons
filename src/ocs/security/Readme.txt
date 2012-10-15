Detalles para no tener inconvenientes con la implementacion del esquema de seguridad:

1. El archivo ir.model.access.csv es separado por comas, a veces cuando se hace la exportacion
de libreoffice y no se tiene el cuidado se separa por ";" y uno no se da cuenta del error


2. model_id:id -> cuando se llenan los datos de esta columna es importante la forma en que se define
el campo 
debe seguir los siguientes parametros:


modulo.model_funcion del modelo ejemplo:

ocs.model_ocs_sub_district

3. En los menus de la vista no se debe poner groups="mi grupo" para restringir el acceso a la vista
ya que funciona de momento pero cuando se instala el modulo de ceros genera un error, por eso en lugar
de eso se debe colocar en el xml de seguridad una referencia al menú donde se haga la restricción.


<record model="ir.ui.menu" id="menu_ocs_settings">
        		<field eval="[(4, ref('group_ocs_manager'))]" name="groups_id"/>
</record>
