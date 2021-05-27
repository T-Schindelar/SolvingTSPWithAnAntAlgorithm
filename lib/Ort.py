# Konstruktor für ein Ort mit seinen GPS-Koordinaten

class Ort:
    # Konstruktor für einen Ort
    def __init__(self, name, breitengrad, laengengrad):
        self.name = name
        self.breitengrad = float(breitengrad)
        self.laengengrad = float(laengengrad)
