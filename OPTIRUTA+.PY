import pandas as pd 
import heapq
import os

# ========================== PRIM ALGORITHM CON MULTIPLES DEPOSITOS ==========================

# Datos de las ciudades y distancias entre ellas (sin tildes)
aristas = [
    (458, "Bogota", "Cali"),
    (418, "Bogota", "Medellin"),
    (239, "Medellin", "Pereira"),
    (84.6, "Pereira", "Armenia"),
    (5.4, "Armenia", "Ibague"),
    (211, "Ibague", "Neiva"),
    (469, "Neiva", "Pasto"),
    (386, "Cali", "Pasto"),
    (1002, "Bogota", "Barranquilla"),
    (949, "Barranquilla", "Santa_Marta"),
    (987, "Barranquilla", "Cartagena"),
    (753, "Medellin", "Barranquilla"),
    (396, "Pereira", "Villavicencio"),
    (123, "Bogota", "Villavicencio"),
    (177, "Pereira", "Manizales"),
    (163, "Manizales", "Ibague"),
    (382, "Medellin", "Bucaramanga"),
    (623, "Cartagena", "Bucaramanga"),
    (139, "Bogota", "Tunja")
]

class RutaPrimMultiDeposito:
    """
    Clase para construir el Arbol de Expansion Minimo (AEM) usando Prim
    con múltiples nodos de inicio (depósitos)
    """
    
    def __init__(self, aristas, depositos=None, output_dir=None):
        self.aristas = aristas
        self.depositos = depositos if depositos else ["Bogota"]  # Depositos iniciales
        self.mst = []  # Aristas del arbol minimo
        self.total_km = 0
        self.adyacencia = {}
        self.visitados = set()
        
        # Definir directorio de salida
        if output_dir is None:
            # Usar directorio actual si no se especifica
            self.output_dir = os.getcwd()
        else:
            self.output_dir = output_dir
            # Crear directorio si no existe
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
        
    def construir_grafo(self):
        """Construye la lista de adyacencia a partir de las aristas"""
        # Crear diccionario de adyacencia vacío
        nodos = set()
        for costo, ciudad1, ciudad2 in self.aristas:
            nodos.add(ciudad1)
            nodos.add(ciudad2)
        
        self.adyacencia = {nodo: [] for nodo in nodos}
        
        # Llenar el diccionario con las aristas
        for costo, ciudad1, ciudad2 in self.aristas:
            self.adyacencia[ciudad1].append((costo, ciudad2))
            self.adyacencia[ciudad2].append((costo, ciudad1))
    
    def prim_multi_deposito(self):
        """
        Implementa el algoritmo de Prim con múltiples depósitos
        
        Los depósitos se consideran como "ya visitados" desde el inicio,
        permitiendo que el árbol crezca desde múltiples puntos simultáneamente
        
        Returns:
            mst: Lista de aristas del arbol minimo
            total_km: Distancia total del arbol
        """
        
        cola = []
        
        # Inicializar: marcar depósitos como visitados y agregar sus vecinos
        for deposito in self.depositos:
            self.visitados.add(deposito)
            
            # Agregar todas las aristas desde cada depósito
            for peso, siguiente in self.adyacencia[deposito]:
                if siguiente not in self.visitados:
                    heapq.heappush(cola, (peso, deposito, siguiente))
        
        # Procesar la cola
        while cola:
            costo, origen, destino = heapq.heappop(cola)
            
            # Si ya fue visitado, saltar
            if destino in self.visitados:
                continue
            
            # Marcar como visitado
            self.visitados.add(destino)
            self.total_km += costo
            
            # Agregar la arista al MST
            self.mst.append((origen, destino, costo))
            
            # Agregar vecinos a la cola
            for peso, siguiente in self.adyacencia[destino]:
                if siguiente not in self.visitados:
                    heapq.heappush(cola, (peso, destino, siguiente))
        
        return self.mst, self.total_km
    
    def agrupar_por_deposito(self):
        """
        Agrupa las aristas del MST por depósito más cercano
        Útil para ver qué ciudades se atienden desde cada depósito
        """
        
        grupos = {deposito: set() for deposito in self.depositos}
        
        # Agregar depósitos a su propio grupo
        for deposito in self.depositos:
            grupos[deposito].add(deposito)
        
        # Para cada arista, asignar la ciudad destino al grupo del origen
        for origen, destino, costo in sorted(self.mst, key=lambda x: x[2]):
            # Encontrar a qué depósito pertenece el origen (recursivamente)
            deposito_responsable = self._encontrar_deposito(origen, grupos)
            grupos[deposito_responsable].add(destino)
        
        return grupos
    
    def _encontrar_deposito(self, ciudad, grupos):
        """Encuentra a qué depósito pertenece una ciudad"""
        for deposito, ciudades in grupos.items():
            if ciudad in ciudades:
                return deposito
        return self.depositos[0]  # Por defecto el primero
    
    def mostrar_resultados(self):
        """Imprime los resultados del algoritmo"""
        print("=" * 85)
        print("ARBOL DE EXPANSION MINIMO CON MULTIPLES DEPOSITOS (Algoritmo de Prim)")
        print("=" * 85)
        print(f"\nDepositos (puntos de origen): {', '.join(self.depositos)}")
        print(f"Total de ciudades conectadas: {len(self.visitados)}")
        print(f"Total de aristas en el MST: {len(self.mst)}\n")
        
        print("Rutas seleccionadas (ordenadas por distancia):")
        print("-" * 85)
        print(f"{'Origen':<20} {'Destino':<20} {'Km':<15} {'Tipo':<15}")
        print("-" * 85)
        
        for origen, destino, costo in sorted(self.mst, key=lambda x: x[2], reverse=True):
            tipo = "DEPOSITO" if origen in self.depositos else "Expansion"
            print(f"{origen:<20} {destino:<20} {costo:<15.2f} {tipo:<15}")
        
        print("-" * 85)
        print(f"TOTAL DE KILOMETROS: {self.total_km:.2f} km")
        print("=" * 85)
    
    def mostrar_agrupacion_por_deposito(self):
        """Muestra qué ciudades se atienden desde cada depósito"""
        grupos = self.agrupar_por_deposito()
        
        print("\n" + "=" * 85)
        print("CIUDADES ASIGNADAS A CADA DEPOSITO")
        print("=" * 85)
        
        for deposito in self.depositos:
            ciudades = sorted(grupos[deposito])
            num_ciudades = len(ciudades)
            print(f"\n {deposito.upper()}")
            print(f"   Total de ciudades: {num_ciudades}")
            print(f"   Ciudades: {', '.join(ciudades)}")
        
        print("\n" + "=" * 85)
    
    def exportar_resultados(self, filename='mst_prim_multi_deposito.csv'):
        """Guarda los resultados en CSV"""
        df_mst = pd.DataFrame(self.mst, columns=['Origen', 'Destino', 'Km'])
        df_mst['Tipo'] = df_mst['Origen'].apply(lambda x: 'DEPOSITO' if x in self.depositos else 'Expansion')
        df_mst = df_mst.sort_values('Km', ascending=False)
        
        # Usar ruta correcta
        filepath = os.path.join(self.output_dir, filename)
        df_mst.to_csv(filepath, index=False)
        print(f"\n Archivo guardado en: {filepath}")
        
        return df_mst


# ========================== EJECUCION ==========================

if __name__ == "__main__":
    # CAMBIA ESTO a tu ruta de Windows
    # Ejemplo: r"C:\Users\Karol\Downloads\6 semestre\diseño de algoritmos\OPTIRUTA"
    OUTPUT_DIR = os.getcwd()  # Usa el directorio actual
    
    # Definir los 3 depósitos
    depositos = ["Bogota", "Ibague", "Pereira", "Bucaramanga"]
    
    # Crear instancia de la clase con múltiples depósitos
    red = RutaPrimMultiDeposito(aristas, depositos=depositos, output_dir=OUTPUT_DIR)
    
    # Construir el grafo de adyacencia
    red.construir_grafo()
    
    # Ejecutar algoritmo de Prim con múltiples depósitos
    red.prim_multi_deposito()
    
    # Mostrar resultados
    red.mostrar_resultados()
    
    # Mostrar agrupación por depósito
    red.mostrar_agrupacion_por_deposito()
    
    # Exportar a CSV
    df = red.exportar_resultados('mst_prim_multi_deposito.csv')
    print("\nPrimeras filas del CSV:")
    print(df.head(10))
    
    print(f"\n Directorio de salida: {OUTPUT_DIR}")