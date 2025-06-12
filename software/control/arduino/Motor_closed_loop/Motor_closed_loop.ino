// Pines de motor PWM (ajusta según tu conexión)
const int LL_PWM = 6;
const int LR_PWM = 5;
const int RL_PWM = 10;
const int RR_PWM = 11;

const int RELAY_PIN = 7;  // Pin para el relé

const int encoderPin1 = A0; //Pin encoder Motor L
const int encoderPin2 = A2; //Pin encoder Motor R

//Variables de encoder
int estadoAnterior_encoder1 = LOW;
int estadoAnterior_encoder2 = LOW;
volatile unsigned int contadorPulsos_encoder1 = 0;
volatile unsigned int contadorPulsos_encoder2 = 0;
const int PULSOS_POR_REV = 480;

//Control de lazo cerrado
// Parámetros PID motor L
float Kp1 = 1.0;
float Ki1 = 2.5;
float Kd1 = 0.0;

float error_previo1 = 0;
float integral1 = 0;

// Parámetros PID motor R
float Kp2 = 1.0;
float Ki2 = 2.5;
float Kd2 = 0.0;

float error_previo2 = 0;
float integral2 = 0;

// Variables PID
float velocidad_ref_L = 0;    
float velocidad_ref_R = 0; 
float velocidad_pala_ref_L = 0;    
float velocidad_pala_ref_R = 0;  
float output1 = 0;   
float output2 = 0; 

//Parámetros de Muestreo
unsigned long tiempoAnterior = 0;
const unsigned int intervaloMuestreo = 100; //50ms 20 Hz > 2*5.5 Hz por Nyquist

void setup() {
  // Pines de PWM de motores como salida
  pinMode(LR_PWM, OUTPUT);
  pinMode(LL_PWM, OUTPUT);
  pinMode(RR_PWM, OUTPUT);
  pinMode(RL_PWM, OUTPUT);

  //Pin de relé como salida
  pinMode(RELAY_PIN, OUTPUT);

  //Pin de encoder como entrada
  pinMode(encoderPin1, INPUT);

  // Iniciar comunicación serial
  Serial.begin(9600);

  //Estado inicial del relé
  digitalWrite(RELAY_PIN, LOW);

  //Tiempo de inicio controlador PID
  tiempoAnterior = millis();
}

void loop() {
//Detección de flancos de subida
int estadoActual_encoder1 = digitalRead(encoderPin1);
int estadoActual_encoder2 = digitalRead(encoderPin2);
if (estadoActual_encoder1 == HIGH && estadoAnterior_encoder1 == LOW) {
    contadorPulsos_encoder1++;  // Flanco de subida detectado
  }
if (estadoActual_encoder2 == HIGH && estadoAnterior_encoder2 == LOW) {
    contadorPulsos_encoder2++;  // Flanco de subida detectado
  }
estadoAnterior_encoder1 = estadoActual_encoder1;
estadoAnterior_encoder2 = estadoActual_encoder2;


//Cálculo de velocidad motores (Medición de encoder y estado actual)
unsigned long tiempoActual = millis();
if (tiempoActual - tiempoAnterior >= intervaloMuestreo) {
    float deltaTiempoSegundos = (tiempoActual - tiempoAnterior) / 1000.0;
    float revoluciones_encoder1 = (float)contadorPulsos_encoder1 / PULSOS_POR_REV;
    float velocidadRPS_encoder1 = revoluciones_encoder1 / deltaTiempoSegundos;     // revoluciones por segundo
    float velocidadRPM_encoder1 = velocidadRPS_encoder1 * 60.0;                     // revoluciones por minuto

    float revoluciones_encoder2 = (float)contadorPulsos_encoder2 / PULSOS_POR_REV;
    float velocidadRPS_encoder2 = revoluciones_encoder2 / deltaTiempoSegundos;     // revoluciones por segundo
    float velocidadRPM_encoder2 = velocidadRPS_encoder2 * 60.0;                     // revoluciones por minuto

    Serial.print("Velocidad_L:");
    Serial.print(velocidadRPM_encoder2);
    Serial.print(",");
    Serial.print("Referencia_L:");
    Serial.print(velocidad_ref_L);
    Serial.print(",");
    Serial.print("Velocidad_R:");
    Serial.print(velocidadRPM_encoder1);
    Serial.print(",");
    Serial.print("Referencia_R:");
    Serial.println(velocidad_ref_R);
    //Serial.print(" RPM, ");
    //Serial.print(velocidadRadS);
    //Serial.println(" rad/s");

    //Cálculos PID 1
    float error1 = abs(velocidad_ref_R) - velocidadRPM_encoder1;
    integral1 += error1 * deltaTiempoSegundos; 
    float derivada1 = (error1 - error_previo1) / deltaTiempoSegundos;

    //Salida PID 1

    output1 = Kp1 * error1 + Ki1 * integral1 + Kd1 * derivada1;
    output1 = constrain(output1, 0, 100); //Limitar PID a rango de PWM de analogWrite
  
    //Cálculos PID 2
    float error2 = abs(velocidad_ref_L) - velocidadRPM_encoder2;
    integral2 += error2 * deltaTiempoSegundos; 
    float derivada2 = (error2 - error_previo2) / deltaTiempoSegundos;

    //Salida PID 2

    output2 = Kp2 * error2 + Ki2 * integral2 + Kd2 * derivada2;
    output2 = constrain(output2, 0, 100); //Limitar PID a rango de PWM de analogWrite

   //Establecer valores para próximo muestreo
    contadorPulsos_encoder1 = 0;
    contadorPulsos_encoder2 = 0;
    error_previo1 = error1;
    error_previo2 = error2;
    tiempoAnterior = tiempoActual;

  }



  //Establecimiento de velocidad para motores
if(velocidad_ref_L >= 0){
    analogWrite(LR_PWM, output1); 
    analogWrite(LL_PWM, 0);
  }
else if(velocidad_ref_L < 0){
    analogWrite(LR_PWM, 0);
    analogWrite(LL_PWM, output1);
  }
if(velocidad_ref_R >= 0){
    analogWrite(RR_PWM, output2);
    analogWrite(RL_PWM, 0);
  }
else if(velocidad_ref_R < 0){
    analogWrite(RR_PWM, 0);
    analogWrite(RL_PWM, output2);
  }

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
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("Ready");}
    else if (comando == "stop"){
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("Emergency Stop");
    } else if (comando.indexOf(",") > 0){
      int firstComaIndex = comando.indexOf(",");
      int lastComaIndex = comando.lastIndexOf(",");
      String accion = comando.substring(0, firstComaIndex);
      if (accion == "move") {
        velocidad_ref_L = comando.substring(firstComaIndex + 1, lastComaIndex).toInt();
        velocidad_ref_R = comando.substring(lastComaIndex + 1).toInt();
        velocidad_pala_ref_L = 0;
        velocidad_pala_ref_R = 0;
        
        Serial.print(velocidad_ref_L);
        Serial.print(",");
        Serial.println(velocidad_ref_R);
      } else if (accion = "shovel"){
        velocidad_ref_L = 0;
        velocidad_ref_R = 0;
        velocidad_pala_ref_L = comando.substring(firstComaIndex + 1, lastComaIndex).toInt();
        velocidad_pala_ref_R = comando.substring(lastComaIndex + 1).toInt();
        }
    }

    //Resetear valores para nueva velocidad
    integral1 = 0;
    integral2 = 0;
    error_previo1 = 0; 
    error_previo2 = 0; 
    }
  }
