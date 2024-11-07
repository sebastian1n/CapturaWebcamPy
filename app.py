import cv2
import sqlite3
import numpy as np
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import Label, Entry, Button

# Configuración de la base de datos
conn = sqlite3.connect("imagenes.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS imagenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    imagen BLOB NOT NULL
)
''')
conn.commit()

# Función para mostrar la vista previa de la cámara, invertir la imagen y guardar una captura
def guardar_imagen():
    nombre = simpledialog.askstring("Guardar imagen", "Ingrese el nombre de la imagen:")
    if not nombre:
        messagebox.showwarning("Advertencia", "Debe ingresar un nombre.")
        return

    camara = cv2.VideoCapture(0)
    
    if not camara.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara.")
        return
    
    messagebox.showinfo("Vista previa", "Presiona 'Espacio' para capturar y 'Esc' para cancelar.")
    
    while True:
        ret, frame = camara.read()
        if not ret:
            break
        
        # Invertir el cuadro horizontalmente (efecto espejo)
        frame = cv2.flip(frame, 1)
        
        cv2.imshow("Vista previa de la cámara", frame)
        
        # Captura la imagen cuando se presiona la tecla 'Espacio'
        key = cv2.waitKey(1)
        if key == 32:  # Tecla 'Espacio' para capturar
            _, buffer = cv2.imencode('.jpg', frame)
            imagen_blob = buffer.tobytes()
            
            # Guardar la imagen en la base de datos
            cursor.execute("INSERT INTO imagenes (nombre, imagen) VALUES (?, ?)", (nombre, imagen_blob))
            conn.commit()
            messagebox.showinfo("Éxito", f"Imagen '{nombre}' guardada exitosamente.")
            break
        elif key == 27:  # Tecla 'Esc' para cancelar
            messagebox.showinfo("Cancelado", "Captura cancelada.")
            break
    
    camara.release()
    cv2.destroyAllWindows()

# Función para buscar y mostrar una imagen
def buscar_imagen():
    nombre = simpledialog.askstring("Buscar imagen", "Ingrese el nombre de la imagen:")
    if not nombre:
        messagebox.showwarning("Advertencia", "Debe ingresar un nombre.")
        return
    
    cursor.execute("SELECT imagen FROM imagenes WHERE nombre = ?", (nombre,))
    resultado = cursor.fetchone()
    
    if resultado:
        imagen_blob = resultado[0]
        np_array = np.frombuffer(imagen_blob, np.uint8)
        imagen = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        cv2.imshow(f"Imagen: {nombre}", imagen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        messagebox.showinfo("No encontrado", f"No se encontró ninguna imagen con el nombre '{nombre}'.")

# Función para ver todas las imágenes almacenadas
def ver_todas_imagenes():
    cursor.execute("SELECT nombre, imagen FROM imagenes")
    resultados = cursor.fetchall()
    
    if not resultados:
        messagebox.showinfo("Sin imágenes", "No hay imágenes guardadas.")
        return
    
    imagenes = []
    for nombre, imagen_blob in resultados:
        np_array = np.frombuffer(imagen_blob, np.uint8)
        imagen = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        imagenes.append((nombre, imagen))
    
    # Mostrar las imágenes una por una
    def mostrar_imagen(index=0):
        if index < len(imagenes):
            cv2.imshow(f"Imagen: {imagenes[index][0]}", imagenes[index][1])
            key = cv2.waitKey(0)  # Espera hasta que se presione una tecla
            if key == 27:  # Tecla 'Esc' para salir
                cv2.destroyAllWindows()
            elif key == 32:  # Tecla 'Espacio' para siguiente imagen
                cv2.destroyAllWindows()
                mostrar_imagen(index + 1)  # Mostrar siguiente imagen
        else:
            cv2.destroyAllWindows()
    
    mostrar_imagen()

# Función para borrar una imagen por su nombre
def borrar_imagen():
    nombre = simpledialog.askstring("Borrar imagen", "Ingrese el nombre de la imagen que desea borrar:")
    if not nombre:
        messagebox.showwarning("Advertencia", "Debe ingresar un nombre.")
        return
    
    cursor.execute("DELETE FROM imagenes WHERE nombre = ?", (nombre,))
    conn.commit()
    
    if cursor.rowcount > 0:
        messagebox.showinfo("Éxito", f"Imagen '{nombre}' borrada exitosamente.")
    else:
        messagebox.showinfo("No encontrada", f"No se encontró ninguna imagen con el nombre '{nombre}'.")

# Crear la ventana principal con tkinter
ventana = tk.Tk()
ventana.title("Captura de Imágenes con OpenCV y SQLite")
ventana.geometry("400x250")

# Etiqueta y botones en la interfaz
Label(ventana, text="Aplicación de Captura de Imágenes", font=("Arial", 16)).pack(pady=10)
Button(ventana, text="Capturar y Guardar Imagen", font=("Arial", 12), command=guardar_imagen).pack(pady=10)
Button(ventana, text="Buscar y Mostrar Imagen", font=("Arial", 12), command=buscar_imagen).pack(pady=10)
Button(ventana, text="Ver Todas las Imágenes", font=("Arial", 12), command=ver_todas_imagenes).pack(pady=10)
Button(ventana, text="Borrar Imagen", font=("Arial", 12), command=borrar_imagen).pack(pady=10)

# Ejecutar la aplicación de tkinter
ventana.mainloop()

# Cerrar la conexión con la base de datos al cerrar la aplicación
conn.close()
