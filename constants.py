#Map device status codes to readable text
DEVICE_STATUS_MAP: dict[int, str] = {
    0: "Voimassa",
    1: "Umpeutunut",
    2: "Työn alla",
    3: "Vain tarvittaessa",
    4: "Ei seurannan piirissä",
    5: "Laite rikki",
    6: "Laite poistettu käytöstä"
}