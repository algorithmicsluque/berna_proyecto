import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QListWidget, 
                             QInputDialog, QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bloc de Notas')
        self.setGeometry(100, 100, 900, 600)
        
        self.datos_file = 'datos.json'
        self.archivos_dir = 'archivos'
        self.current_file = None
        if not os.path.exists(self.archivos_dir):
            os.makedirs(self.archivos_dir)
        
        self.load_data()
        
        if not self.datos.get('nombre'):
            self.preguntar_nombre()
            
        self.init_ui()
        
        self.load_file_list()
    
    def load_data(self):
        """Cargar datos.json o crear uno nuevo"""
        if os.path.exists(self.datos_file):
            with open(self.datos_file, 'r', encoding='utf-8') as f:
                self.datos = json.load(f)
        else:
            self.datos = {'nombre': '', 'archivos': []}
            self.save_data()
    
    def save_data(self):
        """Guardar datos.json"""
        with open(self.datos_file, 'w', encoding='utf-8') as f:
            json.dump(self.datos, f, indent=4, ensure_ascii=False)
    
    def preguntar_nombre(self):
        """Pedir nombre al usuario"""
        nombre, ok = QInputDialog.getText(self, 'Bienvenido', 'Por favor, ingresa tu nombre:')
        if ok and nombre:
            self.datos['nombre'] = nombre
            self.save_data()
        else:
            self.datos['nombre'] = 'Usuario'
            self.save_data()
    
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # === PANEL IZQUIERDO ===
        left_layout = QVBoxLayout()
        
        # Botón Nuevo Archivo
        self.btn_nuevo = QPushButton('Nuevo Archivo')
        self.btn_nuevo.clicked.connect(self.nuevo_archivo)
        left_layout.addWidget(self.btn_nuevo)
        
        # Botón Guardar
        self.btn_guardar = QPushButton('Guardar')
        self.btn_guardar.clicked.connect(self.guardar_archivo)
        left_layout.addWidget(self.btn_guardar)
        
        # Lista de archivos
        self.list_archivos = QListWidget()
        self.list_archivos.itemClicked.connect(self.abrir_archivo)
        left_layout.addWidget(self.list_archivos)
        
        # Widget contenedor para el panel izquierdo
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(250)
        
        # === PANEL DERECHO ===
        right_layout = QVBoxLayout()
        
        # Editor de texto
        self.editor = QTextEdit()
        self.editor.setPlaceholderText('Escribe aquí tu texto...')
        right_layout.addWidget(self.editor)
        
        # Widget contenedor para el panel derecho
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # Agregar ambos paneles al layout principal
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
    
    def load_file_list(self):
        """Cargar la lista de archivos en el QListWidget"""
        self.list_archivos.clear()
        for archivo in self.datos.get('archivos', []):
            item = QListWidgetItem(archivo['nombre'])
            item.setData(Qt.UserRole, archivo['ruta'])
            self.list_archivos.addItem(item)
    
    def nuevo_archivo(self):
        """Crear un nuevo archivo"""
        nombre, ok = QInputDialog.getText(self, 'Nuevo Archivo', 'Nombre del archivo:')
        if ok and nombre:
            # Limpiar el editor
            self.editor.clear()
            
            # Crear ruta del archivo
            ruta = os.path.join(self.archivos_dir, f'{nombre}.txt')
            
            # Verificar si ya existe
            if any(a['nombre'] == nombre for a in self.datos['archivos']):
                QMessageBox.warning(self, 'Advertencia', 'Ya existe un archivo con ese nombre.')
                return
            
            # Guardar en datos.json
            self.datos['archivos'].append({
                'nombre': nombre,
                'ruta': ruta
            })
            self.save_data()
            
            # Crear archivo vacío
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write('')
            
            # Actualizar lista
            self.load_file_list()
            
            # Establecer como archivo actual
            self.current_file = ruta
            
            QMessageBox.information(self, 'Éxito', f'Archivo "{nombre}" creado correctamente.')
    
    def guardar_archivo(self):
        """Guardar el contenido actual del editor"""
        if not self.current_file:
            QMessageBox.warning(self, 'Advertencia', 'No hay ningún archivo abierto para guardar.')
            return
        
        try:
            contenido = self.editor.toPlainText()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(contenido)
            QMessageBox.information(self, 'Éxito', 'Archivo guardado correctamente.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al guardar el archivo: {str(e)}')
    
    def abrir_archivo(self, item):
        """Abrir un archivo seleccionado de la lista"""
        ruta = item.data(Qt.UserRole)
        
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            self.editor.setPlainText(contenido)
            self.current_file = ruta
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al abrir el archivo: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())