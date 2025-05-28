

float error_previo1 = 0;
float integral1 = 0;

float error_previo2 = 0;
float integral2 = 0;

float velocidad_ref_L = 0;    
float velocidad_ref_R = 0;  


void setup() {
  // put your setup code here, to run once:
  // Iniciar comunicación serial
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:

  //Verificar Inputs
  verificarComando();
}

// Revisa si se envió "stop" mientras ejecuta ciclos
void verificarComando() {
  // Verificar si hay datos en el puerto serie
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();  // Elimina espacios en blanco
    if (comando == "on") {
      Serial.println("Ready");}
    else if (comando == "stop"){
      Serial.println("Emergency Stop");
    } else if (comando.indexOf(",") > 0){
      int comaIndex = comando.indexOf(",");
      velocidad_ref_L = comando.substring(0, comaIndex).toInt();
      velocidad_ref_R = comando.substring(comaIndex + 1).toInt();
      Serial.print(velocidad_ref_L);
      Serial.print(",");
      Serial.println(velocidad_ref_R);
    }

    //Resetear valores para nueva velocidad
    integral1 = 0;
    integral2 = 0;
    error_previo1 = 0; 
    error_previo2 = 0; 
    }
  }
