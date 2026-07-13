CREATE TABLE monitoreos (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora          TEXT NOT NULL,
    cpu_nucleos         INTEGER NOT NULL,
    cpu_frecuencia_mhz  REAL,
    cpu_uso_porcentaje  REAL NOT NULL,
    mem_total_kb        INTEGER NOT NULL,
    mem_usada_kb        INTEGER NOT NULL,
    mem_libre_kb        INTEGER NOT NULL,
    swap_total_kb       INTEGER,
    swap_usada_kb       INTEGER,
    disco_total_kb      INTEGER NOT NULL,
    disco_usado_kb      INTEGER NOT NULL,
    disco_libre_kb      INTEGER NOT NULL,
    comentario          TEXT,
    etiqueta            TEXT
);

CREATE TABLE procesos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    monitoreo_id    INTEGER NOT NULL,
    pid             INTEGER NOT NULL,
    nombre          TEXT NOT NULL,
    estado          TEXT NOT NULL,
    usuario         TEXT NOT NULL,
    FOREIGN KEY (monitoreo_id) REFERENCES monitoreos(id) ON DELETE CASCADE
);

CREATE TABLE usuarios_conectados (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    monitoreo_id    INTEGER NOT NULL,
    usuario         TEXT NOT NULL,
    tiempo_conexion TEXT NOT NULL,
    FOREIGN KEY (monitoreo_id) REFERENCES monitoreos(id) ON DELETE CASCADE
);

CREATE TABLE interfaces_red (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    monitoreo_id        INTEGER NOT NULL,
    nombre_interfaz      TEXT NOT NULL,
    direccion_ip         TEXT,
    bytes_recibidos      INTEGER,
    bytes_enviados       INTEGER,
    paquetes_recibidos   INTEGER,
    paquetes_enviados    INTEGER,
    FOREIGN KEY (monitoreo_id) REFERENCES monitoreos(id) ON DELETE CASCADE
);

CREATE INDEX idx_monitoreos_fecha ON monitoreos(fecha_hora);
CREATE INDEX idx_monitoreos_etiqueta ON monitoreos(etiqueta);
CREATE INDEX idx_procesos_monitoreo ON procesos(monitoreo_id);