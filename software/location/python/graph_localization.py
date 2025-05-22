import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer

# Cargar CSV
df = pd.read_csv("gps_single_log.csv")

# Limpiar datos
df = df.dropna(subset=["lat", "lon"])
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df = df.dropna(subset=["lat", "lon"])

# Extraer como arrays 1D
lat = df["lat"].values
lon = df["lon"].values

if lat.ndim != 1 or lon.ndim != 1:
    raise ValueError("Las columnas 'lat' y 'lon' no son 1D.")

if len(lat) == 0 or len(lon) == 0:
    print("Error: no hay datos válidos para graficar.")
else:
    # Definir el sistema de referencia UTM zona 19S (EPSG:32719)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True)
    x, y = transformer.transform(lon, lat)

    # Restar el punto inicial para tener coordenadas relativas
    x = np.array(x) - x[0]
    y = np.array(y) - y[0]

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue', label="Trayectoria GPS (UTM)")
    plt.scatter(x[0], y[0], color='green', label="Inicio", zorder=5)
    plt.scatter(x[-1], y[-1], color='red', label="Fin", zorder=5)

    plt.title("Trayectoria GPS en metros (Datum: WGS84, UTM 19S)")
    plt.xlabel("Este (m)")
    plt.ylabel("Norte (m)")
    plt.grid(True)
    plt.axis("equal")
    plt.legend()
    plt.tight_layout()
    plt.show()
