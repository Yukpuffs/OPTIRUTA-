import pandas as pd
import heapq
import os
from collections import defaultdict
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ========================== DIJKSTRA PARA RUTAS DE PAQUETES ==========================

class RutaDijkstra:
    """
    Clase para calcular la ruta más corta de cada paquete desde su depósito
    usando el algoritmo de Dijkstra
    """
    
    def __init__(self, grafo_path=None, dataset_path=None, output_dir=None):
        """
        Args:
            grafo_path: Ruta al CSV generado por Prim (mst_prim_multi_deposito.csv)
            dataset_path: Ruta al dataset de paquetes limpio
            output_dir: Directorio para guardar resultados
        """
        self.grafo = {}  # Diccionario de adyacencia
        self.depositos = set()
        self.dataset = None
        self.rutas_paquetes = []
        self.output_dir = output_dir if output_dir else os.getcwd()
        
        # Cargar datos
        if grafo_path:
            self._cargar_grafo(grafo_path)
        if dataset_path:
            self._cargar_dataset(dataset_path)
    
    def _cargar_grafo(self, grafo_path):
        """Carga el MST generado por Prim y construye la lista de adyacencia"""
        print(f"\nCargando grafo desde: {grafo_path}")
        
        try:
            df_mst = pd.read_csv(grafo_path)
        except FileNotFoundError:
            print(f"Error: No se encontro {grafo_path}")
            return False
        
        # Construir diccionario de adyacencia
        self.grafo = defaultdict(list)
        
        for _, row in df_mst.iterrows():
            origen = row['Origen']
            destino = row['Destino']
            km = row['Km']
            
            # Agregar aristas en ambas direcciones (grafo no dirigido)
            self.grafo[origen].append((destino, km))
            self.grafo[destino].append((origen, km))
            
            # Identificar depósitos (nodos con tipo DEPOSITO)
            if row['Tipo'] == 'DEPOSITO':
                self.depositos.add(origen)
        
        # Agregar depósitos que podrían no aparecer en la columna Tipo
        self.depositos.add('Bogota')
        self.depositos.add('Ibague')
        self.depositos.add('Pereira')
        
        print(f"Grafo cargado: {len(self.grafo)} ciudades")
        print(f"Depositos identificados: {sorted(self.depositos)}")
        return True
    
    def _cargar_dataset(self, dataset_path):
        """Carga el dataset de paquetes"""
        print(f"Cargando dataset desde: {dataset_path}")
        
        try:
            self.dataset = pd.read_csv(dataset_path)
        except FileNotFoundError:
            print(f"Error: No se encontro {dataset_path}")
            return False
        
        print(f"Dataset cargado: {len(self.dataset)} paquetes")
        return True
    
    def dijkstra(self, origen, destino):
        """
        Implementa el algoritmo de Dijkstra para encontrar la ruta más corta
        
        Args:
            origen: Ciudad de origen (depósito)
            destino: Ciudad de destino
        
        Returns:
            tuple: (ruta como lista, distancia_total)
        """
        
        # Inicializar
        distancias = {ciudad: float('inf') for ciudad in self.grafo}
        distancias[origen] = 0
        predecesores = {ciudad: None for ciudad in self.grafo}
        visitados = set()
        cola = [(0, origen)]
        
        # Ejecutar Dijkstra
        while cola:
            dist_actual, ciudad_actual = heapq.heappop(cola)
            
            # Si ya fue visitado, saltar
            if ciudad_actual in visitados:
                continue
            
            visitados.add(ciudad_actual)
            
            # Si llegamos al destino, podemos terminar
            if ciudad_actual == destino:
                break
            
            # Revisar vecinos
            for vecino, peso in self.grafo.get(ciudad_actual, []):
                if vecino not in visitados:
                    nueva_dist = dist_actual + peso
                    
                    # Si encontramos una ruta más corta, actualizar
                    if nueva_dist < distancias[vecino]:
                        distancias[vecino] = nueva_dist
                        predecesores[vecino] = ciudad_actual
                        heapq.heappush(cola, (nueva_dist, vecino))
        
        # Reconstruir la ruta
        ruta = []
        ciudad = destino
        while ciudad is not None:
            ruta.append(ciudad)
            ciudad = predecesores[ciudad]
        ruta.reverse()
        
        # Si no se encontró ruta, devolver None
        if ruta[0] != origen:
            return None, float('inf')
        
        return ruta, distancias[destino]
    
    def _encontrar_deposito_mas_cercano(self, ciudad_destino):
        """
        Encuentra cuál depósito está más cerca de la ciudad destino
        """
        deposito_cercano = None
        distancia_minima = float('inf')
        
        for deposito in self.depositos:
            ruta, distancia = self.dijkstra(deposito, ciudad_destino)
            if ruta and distancia < distancia_minima:
                distancia_minima = distancia
                deposito_cercano = deposito
        
        return deposito_cercano, distancia_minima
    
    def procesar_paquetes(self):
        """
        Calcula la ruta más corta para cada paquete en el dataset
        """
        if self.dataset is None:
            print("Error: Dataset no cargado")
            return False
        
        print("\n" + "=" * 100)
        print("CALCULANDO RUTAS PARA CADA PAQUETE (Dijkstra)")
        print("=" * 100)
        
        total_paquetes = len(self.dataset)
        paquetes_procesados = 0
        paquetes_sin_ruta = 0
        
        for idx, fila in self.dataset.iterrows():
            id_paquete = fila['ID_Paquete']
            cliente = fila['Cliente']
            ciudad_destino = fila['Ciudad_Destino']
            peso = fila['Peso_kg']
            volumen = fila['Volumen_Paquete_m3']
            
            # Validar que la ciudad esté en el grafo
            if ciudad_destino not in self.grafo:
                paquetes_sin_ruta += 1
                self.rutas_paquetes.append({
                    'ID_Paquete': id_paquete,
                    'Cliente': cliente,
                    'Ciudad_Destino': ciudad_destino,
                    'Peso_kg': peso,
                    'Volumen_m3': volumen,
                    'Deposito_Origen': None,
                    'Ruta': 'NO EXISTE EN GRAFO',
                    'Km_Total': None,
                    'Num_Paradas': 0
                })
                continue
            
            # Encontrar el depósito más cercano
            deposito, distancia = self._encontrar_deposito_mas_cercano(ciudad_destino)
            
            if deposito is None:
                paquetes_sin_ruta += 1
                self.rutas_paquetes.append({
                    'ID_Paquete': id_paquete,
                    'Cliente': cliente,
                    'Ciudad_Destino': ciudad_destino,
                    'Peso_kg': peso,
                    'Volumen_m3': volumen,
                    'Deposito_Origen': None,
                    'Ruta': 'SIN RUTA DISPONIBLE',
                    'Km_Total': None,
                    'Num_Paradas': 0
                })
                continue
            
            # Calcular la ruta
            ruta, km_total = self.dijkstra(deposito, ciudad_destino)
            
            if ruta is None:
                paquetes_sin_ruta += 1
                ruta_str = 'SIN RUTA'
                num_paradas = 0
            else:
                ruta_str = ' -> '.join(ruta)
                num_paradas = len(ruta) - 1  # Número de paradas (sin contar origen)
            
            # Guardar información del paquete
            self.rutas_paquetes.append({
                'ID_Paquete': id_paquete,
                'Cliente': cliente,
                'Ciudad_Destino': ciudad_destino,
                'Peso_kg': peso,
                'Volumen_m3': volumen,
                'Deposito_Origen': deposito,
                'Ruta': ruta_str,
                'Km_Total': km_total if km_total != float('inf') else None,
                'Num_Paradas': num_paradas
            })
            
            paquetes_procesados += 1
            
            # Mostrar progreso cada 100 paquetes
            if (idx + 1) % 100 == 0:
                print(f"Procesados: {idx + 1}/{total_paquetes}")
        
        print("=" * 100)
        print(f"Paquetes procesados: {paquetes_procesados}")
        print(f"Paquetes sin ruta: {paquetes_sin_ruta}")
        print("=" * 100)
        
        return True
    
    def mostrar_resultados(self, num_filas=10):
        """Muestra un resumen de los resultados"""
        if not self.rutas_paquetes:
            print("Error: No hay rutas calculadas. Ejecuta procesar_paquetes() primero")
            return
        
        df_rutas = pd.DataFrame(self.rutas_paquetes)
        
        print("\n" + "=" * 140)
        print("RUTAS DE PAQUETES CALCULADAS")
        print("=" * 140)
        print(f"\nPrimeras {num_filas} filas:")
        # Convertir a string con encoding seguro
        resultado = df_rutas.head(num_filas).to_string(index=False)
        print(resultado)
        
        print("\n" + "=" * 140)
        print("ESTADISTICAS")
        print("=" * 140)
        
        print(f"\nTotal de paquetes: {len(df_rutas)}")
        print(f"Paquetes con ruta valida: {len(df_rutas[df_rutas['Km_Total'].notna()])}")
        print(f"Paquetes sin ruta: {len(df_rutas[df_rutas['Km_Total'].isna()])}")
        
        print(f"\nDistancias:")
        print(f"  Minima: {df_rutas['Km_Total'].min():.2f} km")
        print(f"  Maxima: {df_rutas['Km_Total'].max():.2f} km")
        print(f"  Promedio: {df_rutas['Km_Total'].mean():.2f} km")
        print(f"  Total: {df_rutas['Km_Total'].sum():.2f} km")
        
        print(f"\nDistribucion por deposito:")
        dist_depositos = df_rutas['Deposito_Origen'].value_counts()
        for deposito, count in dist_depositos.items():
            porcentaje = (count / len(df_rutas)) * 100
            print(f"  {deposito}: {count} paquetes ({porcentaje:.1f}%)")
        
        print("\n" + "=" * 140)
    
    def exportar_resultados(self, filename='rutas_paquetes_dijkstra.csv'):
        """Guarda las rutas en CSV"""
        if not self.rutas_paquetes:
            print("Error: No hay rutas para exportar")
            return False
        
        df_rutas = pd.DataFrame(self.rutas_paquetes)
        filepath = os.path.join(self.output_dir, filename)
        df_rutas.to_csv(filepath, index=False)
        
        print(f"\nRutas exportadas a: {filepath}")
        return df_rutas


# ========================== EJECUCION ==========================

if __name__ == "__main__":
    # Configurar pandas para mejor output
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', None)
    
    # CAMBIA ESTAS RUTAS A TUS DIRECTORIOS
    GRAFO_PATH = "mst_prim_multi_deposito.csv"
    DATASET_PATH = "dataset_amazon_colombia_limpio.csv"
    OUTPUT_DIR = os.getcwd()
    
    print("Iniciando Dijkstra para calculo de rutas...\n")
    
    # Crear instancia
    dijkstra = RutaDijkstra(
        grafo_path=GRAFO_PATH,
        dataset_path=DATASET_PATH,
        output_dir=OUTPUT_DIR
    )
    
    # Procesar paquetes
    dijkstra.procesar_paquetes()
    
    # Mostrar resultados
    dijkstra.mostrar_resultados(num_filas=15)
    
    # Exportar a CSV
    df_final = dijkstra.exportar_resultados('rutas_paquetes_dijkstra.csv')
    
    print("\nPrimeras 10 filas del resultado:")
    print(df_final.head(10).to_string())