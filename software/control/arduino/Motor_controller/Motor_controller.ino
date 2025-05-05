// Control de motor con BTS7960
// Oscar Gonzalez - BricoGeek.com
int LL_PWM = 6;
int LR_PWM = 5;
int RL_PWM = 10;
int RR_PWM = 11;
int RELE = 7;

void setup() {
 pinMode(LL_PWM, OUTPUT);
 pinMode(LR_PWM, OUTPUT);
 pinMode(RL_PWM, OUTPUT);
 pinMode(RR_PWM, OUTPUT);
 pinMode(RELE, OUTPUT);
 Serial.begin(9600);
 digitalWrite(RELE, HIGH);
}

void loop() {
  int velocidad_max = 0; // Valor entre 0 y 254
  
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.print("You sent me: ");
    Serial.println(data);
    velocidad_max = data.toInt(); // Valor entre 0 y 254
  }

  if (velocidad_max != 0) {
     // Giro derecha
    for (int i = 0; i < velocidad_max; i++) {
       analogWrite(LR_PWM, i);
       analogWrite(LL_PWM, 0);
       analogWrite(RR_PWM, i);
       analogWrite(RL_PWM, 0);
       delay(50);
            }
    
       delay(1000); // Esperamos 1 segundo
    
    for (int i = velocidad_max; i > 0; i--) {
       analogWrite(LR_PWM, i);
       analogWrite(LL_PWM, 0);
       analogWrite(RR_PWM, i);
       analogWrite(RL_PWM, 0);
       delay(50);
            }
     
       delay(1000); // Esperamos 1 segundo
    
    for (int i = 0; i < velocidad_max; i++) {
       analogWrite(LR_PWM, 0);
       analogWrite(LL_PWM, i);
       analogWrite(RR_PWM, 0);
       analogWrite(RL_PWM, i);
       delay(50);
            }
    
       delay(1000); // Esperamos 1 segundo
    
    for (int i = velocidad_max; i > 0; i--) {
       analogWrite(LR_PWM, 0);
       analogWrite(LL_PWM, i);
       analogWrite(RR_PWM, 0);
       analogWrite(RL_PWM, i);
       delay(50);
            }
      
        delay(1000); // Esperamos 1 segundo
    }
}
