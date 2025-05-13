import pandas as pd
import matplotlib.pyplot as plt

# Leer CSV
df = pd.read_csv("gps_log.csv")

# Graficar
plt.figure(figsize=(10, 6))
plt.plot(df["raw_lon"], df["raw_lat"], label="Sin corrección", color="red", linestyle="--")
#plt.plot(df["corrected_lon"], df["corrected_lat"], label="Corregido", color="blue")

#plt.title("Comparación de trayectorias GPS")
plt.title("Trayectorias GPS")
plt.xlabel("Longitud")
plt.ylabel("Latitud")
plt.legend()
plt.grid(True)
plt.axis("equal")
plt.show()