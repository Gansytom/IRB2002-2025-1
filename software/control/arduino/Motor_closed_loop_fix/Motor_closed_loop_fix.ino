// Pines de motor PWM (ajusta según tu conexión)
const int LL_PWM = 6;
const int LR_PWM = 5;
const int RL_PWM = 10;
const int RR_PWM = 11;

const int RELAY_PIN = 7;

const int encoderPin1 = A0; // Encoder Motor L
const int encoderPin2 = A2; // Encoder Motor R

// Variables encoder
int estadoAnterior_encoder1 = LOW;
int estadoAnterior_encoder2 = LOW;
volatile unsigned int contadorPulsos_encoder1 = 0;
volatile unsigned int contadorPulsos_encoder2 = 0;
const int PULSOS_POR_REV = 480;

// PID parámetros motor L
float Kp1 = 0.5, Ki1 = 2.5, Kd1 = 0.0;
float error_previo1 = 0, integral1 = 0;

// PID parámetros motor R
float Kp2 = 0.5, Ki2 = 2.5, Kd2 = 0.0;
float error_previo2 = 0, integral2 = 0;

// Referencias de velocidad
float velocidad_ref_L = 0, velocidad_ref_R = 0;
float velocidad_ref_L_deseada = 0, velocidad_ref_R_deseada = 0;
float velocidad_pala_ref_L = 0, velocidad_pala_ref_R = 0;
float output1 = 0, output2 = 0;
int velocidad_limite = 150;  

// Interpolación
const float incrementoMaximo = 5.0; // RPM por ciclo

// PWM seguro
int direccion_previa_L = 0;
int direccion_previa_R = 0;

// Muestreo
unsigned long tiempoAnterior = 0;
const unsigned int intervaloMuestreo = 100;

void setup() {
  pinMode(LR_PWM, OUTPUT);
  pinMode(LL_PWM, OUTPUT);
  pinMode(RR_PWM, OUTPUT);
  pinMode(RL_PWM, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(encoderPin1, INPUT);
  pinMode(encoderPin2, INPUT);
  Serial.begin(9600);
  digitalWrite(RELAY_PIN, LOW);
  tiempoAnterior = millis();
}

void loop() {
  // Lectura encoder
  int estadoActual_encoder1 = digitalRead(encoderPin1);
  int estadoActual_encoder2 = digitalRead(encoderPin2);
  if (estadoActual_encoder1 == HIGH && estadoAnterior_encoder1 == LOW) contadorPulsos_encoder1++;
  if (estadoActual_encoder2 == HIGH && estadoAnterior_encoder2 == LOW) contadorPulsos_encoder2++;
  estadoAnterior_encoder1 = estadoActual_encoder1;
  estadoAnterior_encoder2 = estadoActual_encoder2;

  // Cálculo de velocidad
  unsigned long tiempoActual = millis();
  if (tiempoActual - tiempoAnterior >= intervaloMuestreo) {
    float deltaTiempo = (tiempoActual - tiempoAnterior) / 1000.0;

    float rpm1 = ((float)contadorPulsos_encoder1 / PULSOS_POR_REV) / deltaTiempo * 60.0;
    float rpm2 = ((float)contadorPulsos_encoder2 / PULSOS_POR_REV) / deltaTiempo * 60.0;

    Serial.print("Velocidad_L:"); Serial.print(rpm2);
    Serial.print(",Referencia_L:"); Serial.print(velocidad_ref_L);
    Serial.print(",Velocidad_R:"); Serial.print(rpm1);
    Serial.print(",Referencia_R:"); Serial.println(velocidad_ref_R);

    // PID 1
    float error1 = abs(velocidad_ref_R) - rpm1;
    integral1 += error1 * deltaTiempo;
    float derivada1 = (error1 - error_previo1) / deltaTiempo;
    float salida_sin_constrain1 = Kp1 * error1 + Ki1 * integral1 + Kd1 * derivada1;
    output1 = constrain(salida_sin_constrain1, 0, 255);
    if (output1 != salida_sin_constrain1) integral1 -= error1 * deltaTiempo; // Anti-windup
    error_previo1 = error1;

    // PID 2
    float error2 = abs(velocidad_ref_L) - rpm2;
    integral2 += error2 * deltaTiempo;
    float derivada2 = (error2 - error_previo2) / deltaTiempo;
    float salida_sin_constrain2 = Kp2 * error2 + Ki2 * integral2 + Kd2 * derivada2;
    output2 = constrain(salida_sin_constrain2, 0, 255);
    if (output2 != salida_sin_constrain2) integral2 -= error2 * deltaTiempo; // Anti-windup
    error_previo2 = error2;

    // Reset para próxima muestra
    contadorPulsos_encoder1 = 0;
    contadorPulsos_encoder2 = 0;
    tiempoAnterior = tiempoActual;
  }

  // Interpolación suave
  velocidad_ref_L += constrain(velocidad_ref_L_deseada - velocidad_ref_L, -incrementoMaximo, incrementoMaximo);
  velocidad_ref_R += constrain(velocidad_ref_R_deseada - velocidad_ref_R, -incrementoMaximo, incrementoMaximo);

  // Control de dirección segura
  int nueva_direccion_L = (velocidad_ref_L >= 0) ? 1 : -1;
  int nueva_direccion_R = (velocidad_ref_R >= 0) ? 1 : -1;

  if (nueva_direccion_L != direccion_previa_L) {
    integral2 = 0;
    error_previo2 = 0;
    analogWrite(LR_PWM, 0); analogWrite(LL_PWM, 0);
    delay(20);
  }
  if (nueva_direccion_R != direccion_previa_R) {
    integral1 = 0;
    error_previo1 = 0;
    analogWrite(RR_PWM, 0); analogWrite(RL_PWM, 0);
    delay(20);
  }

  direccion_previa_L = nueva_direccion_L;
  direccion_previa_R = nueva_direccion_R;

  // Aplicar PWM
  if (velocidad_ref_L >= 0) {
    analogWrite(LR_PWM, 0); analogWrite(LL_PWM, output1);
  } else {
    analogWrite(LR_PWM, output1); analogWrite(LL_PWM, 0);
  }

  if (velocidad_ref_R >= 0) {
    analogWrite(RR_PWM, 0); analogWrite(RL_PWM, output2);
  } else {
    analogWrite(RR_PWM, output2); analogWrite(RL_PWM, 0);
  }

  verificarComando(); // Leer comandos desde Serial
}

void verificarComando() {
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    Serial.println(comando);
    comando.trim();

    if (comando == "on") {
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("Ready");
    } else if (comando == "stop") {
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("Emergency Stop");
      integral1 = 0; integral2 = 0;
      error_previo1 = 0; error_previo2 = 0;
    } else if (comando.indexOf(",") > 0) {
      int firstComa = comando.indexOf(",");
      int lastComa = comando.lastIndexOf(",");
      String accion = comando.substring(0, firstComa);

      if (accion == "move") {
        velocidad_ref_L_deseada = comando.substring(firstComa + 1, lastComa).toInt();
        velocidad_ref_R_deseada = comando.substring(lastComa + 1).toInt();
        velocidad_pala_ref_L = 0;
        velocidad_pala_ref_R = 0;
        if (velocidad_ref_L > velocidad_limite){
        velocidad_ref_L = velocidad_limite;
        }
        else if (velocidad_ref_L < -velocidad_limite){
          velocidad_ref_L = -velocidad_limite;
        }
        if (velocidad_ref_R > velocidad_limite){
          velocidad_ref_R = velocidad_limite;
        }
        else if (velocidad_ref_R < -velocidad_limite){
          velocidad_ref_R = -velocidad_limite;
        }
        Serial.print(velocidad_ref_L_deseada);
        Serial.print(",");
        Serial.println(velocidad_ref_R_deseada);
      } else if (accion == "shovel") {
        velocidad_ref_L_deseada = 0;
        velocidad_ref_R_deseada = 0;
        velocidad_pala_ref_L = comando.substring(firstComa + 1, lastComa).toInt();
        velocidad_pala_ref_R = comando.substring(lastComa + 1).toInt();
      }
    }

    // Reset PID (comentar para que no se reinicie)
//    integral1 = 0; integral2 = 0;
//    error_previo1 = 0; error_previo2 = 0;
  }
}
