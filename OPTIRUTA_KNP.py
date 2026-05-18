import pandas as pd
import os
from collections import defaultdict

# ========================== KNAPSACK 0/1 CON PROGRAMACION DINAMICA ==========================

class KnapsackVehiculosOptimizado:
    """
    Clase para empacar paquetes en vehiculos usando Knapsack 0/1 con DP
    Optimiza el uso de capacidad de forma significativa
    """
    
    def __init__(self, rutas_path=None, output_dir=None):
        """
        Args:
            rutas_path: Ruta al CSV de rutas generado por Dijkstra
            output_dir: Directorio para guardar resultados
        """
        self.rutas_df = None
        self.vehiculos = []
        self.output_dir = output_dir if output_dir else os.getcwd()
        self.contador_vehiculos = {'Moto': 0, 'Furgoneta': 0, 'Camion': 0}
        self.stats = {'paquetes_totales': 0, 'paquetes_empacados': 0, 'capacidad_usada': 0}
        
        if rutas_path:
            self._cargar_rutas(rutas_path)
    
    def _cargar_rutas(self, rutas_path):
        """Carga el dataframe de rutas"""
        print(f"Cargando rutas desde: {rutas_path}")
        
        try:
            self.rutas_df = pd.read_csv(rutas_path)
            print(f"Rutas cargadas: {len(self.rutas_df)} paquetes")
            return True
        except FileNotFoundError:
            print(f"Error: No se encontro {rutas_path}")
            return False
    
    def _contar_ciudades_en_ruta(self, ruta_str):
        """Cuenta el numero de ciudades en una ruta"""
        if pd.isna(ruta_str) or ruta_str == 'NO EXISTE EN GRAFO' or ruta_str == 'SIN RUTA':
            return 0
        return len(ruta_str.split('->'))
    
    def _determinar_tipo_vehiculo(self, ruta_str):
        """Determina el tipo de vehiculo segun el numero de ciudades en la ruta"""
        num_ciudades = self._contar_ciudades_en_ruta(ruta_str)
        
        if num_ciudades == 1:
            return 'Moto'
        elif num_ciudades == 2:
            return 'Furgoneta'
        elif num_ciudades >= 3:
            return 'Camion'
        else:
            return None
    
    def knapsack_dp(self, paquetes, capacidad):
        """
        Implementa Knapsack 0/1 usando Programacion Dinamica
        
        Args:
            paquetes: Lista de paquetes con columna 'Peso_kg'
            capacidad: Capacidad maxima del vehiculo
        
        Returns:
            tuple: (indices de paquetes seleccionados, peso total)
        """
        n = len(paquetes)
        
        if n == 0 or capacidad <= 0:
            return [], 0
        
        # Extraer pesos
        pesos = [float(p['Peso_kg']) for p in paquetes]
        
        # Tabla DP: dp[i][w] = peso maximo usando primeros i items con capacidad w
        # Usar enteros para capacidad (escalar a gramos para evitar problemas con floats)
        cap_int = int(capacidad * 1000)
        
        # Inicializar DP
        dp = [[0 for _ in range(cap_int + 1)] for _ in range(n + 1)]
        
        # Llenar tabla DP
        for i in range(1, n + 1):
            peso_item = int(pesos[i-1] * 1000)
            
            for w in range(cap_int + 1):
                # No tomar el item
                dp[i][w] = dp[i-1][w]
                
                # Tomar el item si cabe
                if peso_item <= w:
                    dp[i][w] = max(dp[i][w], dp[i-1][w - peso_item] + peso_item)
        
        # Backtracking para encontrar que items fueron seleccionados
        w = cap_int
        indices_seleccionados = []
        
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                indices_seleccionados.append(i - 1)
                peso_item = int(pesos[i-1] * 1000)
                w -= peso_item
        
        indices_seleccionados.reverse()
        
        # Calcular peso real
        peso_total = sum(pesos[i] for i in indices_seleccionados) / 1000
        
        return indices_seleccionados, peso_total
    
    def empacar_paquetes(self):
        """
        Empaca paquetes en vehiculos usando Knapsack 0/1 optimizado
        """
        
        if self.rutas_df is None:
            print("Error: Rutas no cargadas")
            return False
        
        print("\n" + "="*100)
        print("EMPACANDO PAQUETES EN VEHICULOS (Knapsack 0/1 con DP)")
        print("="*100)
        
        # Filtrar paquetes con ruta valida
        paquetes_validos = self.rutas_df[self.rutas_df['Km_Total'].notna()].copy()
        print(f"\nPaquetes a empacar: {len(paquetes_validos)}")
        self.stats['paquetes_totales'] = len(paquetes_validos)
        
        # Agrupar por tipo de ruta
        paquetes_por_tipo = defaultdict(list)
        
        for _, paquete in paquetes_validos.iterrows():
            tipo = self._determinar_tipo_vehiculo(paquete['Ruta'])
            if tipo:
                paquetes_por_tipo[tipo].append(paquete)
        
        # Empacar cada tipo
        print("\n" + "-"*100)
        print("MOTOS (1 ciudad, max 3 motos por ciudad, capacidad 15kg)")
        print("-"*100)
        self._empacar_motos(paquetes_por_tipo['Moto'])
        
        print("\n" + "-"*100)
        print("FURGONETAS (2 ciudades, 1 por trayecto, capacidad 35kg)")
        print("-"*100)
        self._empacar_furgonetas(paquetes_por_tipo['Furgoneta'])
        
        print("\n" + "-"*100)
        print("CAMIONES (3+ ciudades, 2 por trayecto, capacidad 3000kg)")
        print("-"*100)
        self._empacar_camiones(paquetes_por_tipo['Camion'])
        
        return True
    
    def _empacar_motos(self, paquetes):
        """Empaca motos usando Knapsack 0/1"""
        if not paquetes:
            print("Sin paquetes para empacar en motos")
            return
        
        # Agrupar por ciudad
        por_ciudad = defaultdict(list)
        for paquete in paquetes:
            ciudad = paquete['Ciudad_Destino']
            por_ciudad[ciudad].append(paquete)
        
        paquetes_empacados = 0
        
        for ciudad, paquetes_ciudad in por_ciudad.items():
            # Ordenar por peso descendente (heuristica)
            paquetes_ciudad.sort(key=lambda x: x['Peso_kg'], reverse=True)
            
            motos_en_ciudad = 0
            indices_globales_empacados = set()
            
            while motos_en_ciudad < 20:
                motos_en_ciudad += 1
                self.contador_vehiculos['Moto'] += 1
                id_moto = f"MOTO_{self.contador_vehiculos['Moto']}"
                
                # Filtrar paquetes no empacados
                paquetes_disponibles = [
                    (i, p) for i, p in enumerate(paquetes_ciudad) 
                    if i not in indices_globales_empacados
                ]
                
                if not paquetes_disponibles:
                    break
                
                # Extraer solo paquetes para Knapsack
                solo_paquetes = [p for _, p in paquetes_disponibles]
                
                # Usar Knapsack 0/1 para empacar optimalmente
                indices_seleccionados, peso_total = self.knapsack_dp(
                    solo_paquetes, 15
                )
                
                if not indices_seleccionados:
                    break
                
                # Mapear indices de disponibles a globales
                for idx_local in indices_seleccionados:
                    idx_global = paquetes_disponibles[idx_local][0]
                    indices_globales_empacados.add(idx_global)
                
                paquetes_en_moto = [solo_paquetes[i] for i in indices_seleccionados]
                ids_paquetes = [str(int(p['ID_Paquete'])) for p in paquetes_en_moto]
                
                self.vehiculos.append({
                    'ID_Vehiculo': id_moto,
                    'Tipo': 'Moto',
                    'Ciudad_Destino': ciudad,
                    'Num_Ciudades': 1,
                    'Peso_kg': peso_total,
                    'Capacidad_kg': 30,
                    'Uso_Capacidad_%': (peso_total / 30) * 100,
                    'Num_Paquetes': len(paquetes_en_moto),
                    'IDs_Paquetes': ','.join(ids_paquetes),
                    'Km_Ruta': paquetes_en_moto[0]['Km_Total']
                })
                
                paquetes_empacados += len(paquetes_en_moto)
                print(f"{id_moto} -> {ciudad}: {len(paquetes_en_moto)} paquetes, {peso_total:.2f}kg / 15kg ({(peso_total/30)*100:.1f}%)")
            
            sin_empacar = len(paquetes_ciudad) - len(indices_globales_empacados)
            if sin_empacar > 0:
                print(f"Advertencia: {sin_empacar} paquetes no empacados en {ciudad}")
        
        self.stats['paquetes_empacados'] += paquetes_empacados
        print(f"Total motos: {self.contador_vehiculos['Moto']}, Paquetes empacados: {paquetes_empacados}")
    
    def _empacar_furgonetas(self, paquetes):
        """Empaca furgonetas usando Knapsack 0/1"""
        if not paquetes:
            print("Sin paquetes para empacar en furgonetas")
            return
        
        por_ruta = defaultdict(list)
        for paquete in paquetes:
            ruta = paquete['Ruta']
            por_ruta[ruta].append(paquete)
        
        paquetes_empacados = 0
        
        for ruta, paquetes_ruta in por_ruta.items():
            paquetes_ruta.sort(key=lambda x: x['Peso_kg'], reverse=True)
            
            # Solo 1 furgoneta por trayecto
            self.contador_vehiculos['Furgoneta'] += 20
            id_furgoneta = f"FURGONETA_{self.contador_vehiculos['Furgoneta']}"
            
            # Knapsack 0/1
            indices_seleccionados, peso_total = self.knapsack_dp(paquetes_ruta, 1000)
            
            if indices_seleccionados:
                paquetes_en_furgoneta = [paquetes_ruta[i] for i in indices_seleccionados]
                ids_paquetes = [str(int(p['ID_Paquete'])) for p in paquetes_en_furgoneta]
                
                self.vehiculos.append({
                    'ID_Vehiculo': id_furgoneta,
                    'Tipo': 'Furgoneta',
                    'Ciudad_Destino': paquetes_ruta[0]['Ciudad_Destino'],
                    'Num_Ciudades': 2,
                    'Peso_kg': peso_total,
                    'Capacidad_kg': 1000,
                    'Uso_Capacidad_%': (peso_total / 100) * 100,
                    'Num_Paquetes': len(paquetes_en_furgoneta),
                    'IDs_Paquetes': ','.join(ids_paquetes),
                    'Km_Ruta': paquetes_ruta[0]['Km_Total']
                })
                
                paquetes_empacados += len(paquetes_en_furgoneta)
                print(f"{id_furgoneta} -> {ruta}: {len(paquetes_en_furgoneta)} paquetes, {peso_total:.2f}kg / 35kg ({(peso_total/1000)*100:.1f}%)")
            
            sin_empacar = len(paquetes_ruta) - len(indices_seleccionados)
            if sin_empacar > 0:
                print(f"Advertencia: {sin_empacar} paquetes no empacados en ruta {ruta}")
        
        self.stats['paquetes_empacados'] += paquetes_empacados
        print(f"Total furgonetas: {self.contador_vehiculos['Furgoneta']}, Paquetes empacados: {paquetes_empacados}")
    
    def _empacar_camiones(self, paquetes):
        """Empaca camiones usando Knapsack 0/1"""
        if not paquetes:
            print("Sin paquetes para empacar en camiones")
            return
        
        por_ruta = defaultdict(list)
        for paquete in paquetes:
            ruta = paquete['Ruta']
            por_ruta[ruta].append(paquete)
        
        paquetes_empacados = 0
        
        for ruta, paquetes_ruta in por_ruta.items():
            paquetes_ruta.sort(key=lambda x: x['Peso_kg'], reverse=True)
            
            camiones_en_ruta = 0
            indices_empacados = set()
            
            while camiones_en_ruta < 2:
                camiones_en_ruta += 1
                self.contador_vehiculos['Camion'] += 1
                id_camion = f"CAMION_{self.contador_vehiculos['Camion']}"
                
                # Filtrar paquetes no empacados
                paquetes_disponibles = [
                    p for i, p in enumerate(paquetes_ruta)
                    if i not in indices_empacados
                ]
                
                if not paquetes_disponibles:
                    break
                
                # Knapsack 0/1
                indices_seleccionados, peso_total = self.knapsack_dp(
                    paquetes_disponibles, 3000
                )
                
                if not indices_seleccionados:
                    break
                
                paquetes_en_camion = [paquetes_disponibles[i] for i in indices_seleccionados]
                
                for p in paquetes_en_camion:
                    # idx_global = paquetes_ruta.index(p) - removido
                    indices_empacados.add(idx_global)
                
                ids_paquetes = [str(int(p['ID_Paquete'])) for p in paquetes_en_camion]
                
                self.vehiculos.append({
                    'ID_Vehiculo': id_camion,
                    'Tipo': 'Camion',
                    'Ciudad_Destino': paquetes_en_camion[0]['Ciudad_Destino'],
                    'Num_Ciudades': self._contar_ciudades_en_ruta(ruta),
                    'Peso_kg': peso_total,
                    'Capacidad_kg': 3000,
                    'Uso_Capacidad_%': (peso_total / 3000) * 100,
                    'Num_Paquetes': len(paquetes_en_camion),
                    'IDs_Paquetes': ','.join(ids_paquetes),
                    'Km_Ruta': paquetes_en_camion[0]['Km_Total']
                })
                
                paquetes_empacados += len(paquetes_en_camion)
                print(f"{id_camion} -> {ruta}: {len(paquetes_en_camion)} paquetes, {peso_total:.2f}kg / 3000kg ({(peso_total/3000)*100:.1f}%)")
            
            sin_empacar = len(paquetes_ruta) - len(indices_empacados)
            if sin_empacar > 0:
                print(f"Advertencia: {sin_empacar} paquetes no empacados en ruta {ruta}")
        
        self.stats['paquetes_empacados'] += paquetes_empacados
        print(f"Total camiones: {self.contador_vehiculos['Camion']}, Paquetes empacados: {paquetes_empacados}")
    
    def mostrar_resultados(self):
        """Muestra resumen de empaque"""
        if not self.vehiculos:
            print("Error: No hay vehiculos empacados")
            return
        
        df_vehiculos = pd.DataFrame(self.vehiculos)
        
        print("\n" + "="*100)
        print("RESUMEN DE VEHICULOS EMPACADOS (Knapsack 0/1 Optimizado)")
        print("="*100)
        
        print(f"\nTotal de vehiculos: {len(df_vehiculos)}")
        print(f"  - Motos: {self.contador_vehiculos['Moto']}")
        print(f"  - Furgonetas: {self.contador_vehiculos['Furgoneta']}")
        print(f"  - Camiones: {self.contador_vehiculos['Camion']}")
        
        print(f"\nPaquetes:")
        print(f"  Total: {self.stats['paquetes_totales']}")
        print(f"  Empacados: {self.stats['paquetes_empacados']}")
        print(f"  No empacados: {self.stats['paquetes_totales'] - self.stats['paquetes_empacados']}")
        
        print(f"\nUso de capacidad por tipo:")
        for tipo in ['Moto', 'Furgoneta', 'Camion']:
            df_tipo = df_vehiculos[df_vehiculos['Tipo'] == tipo]
            if len(df_tipo) > 0:
                uso_promedio = df_tipo['Uso_Capacidad_%'].mean()
                uso_maximo = df_tipo['Uso_Capacidad_%'].max()
                print(f"  {tipo}: Promedio {uso_promedio:.1f}%, Maximo {uso_maximo:.1f}%")
        
        print(f"\nCapacidad total utilizada: {df_vehiculos['Peso_kg'].sum():.2f} kg")
        
        print("\n" + "="*100)
        print("PRIMEROS 10 VEHICULOS:")
        print("="*100)
        print(df_vehiculos[['ID_Vehiculo', 'Tipo', 'Num_Ciudades', 'Num_Paquetes', 'Peso_kg', 'Uso_Capacidad_%']].head(10).to_string(index=False))
    
    def exportar_resultados(self, filename='vehiculos_knapsack_optimizado.csv'):
        """Guarda los resultados en CSV"""
        if not self.vehiculos:
            print("Error: No hay vehiculos para exportar")
            return False
        
        df_vehiculos = pd.DataFrame(self.vehiculos)
        filepath = os.path.join(self.output_dir, filename)
        df_vehiculos.to_csv(filepath, index=False)
        
        print(f"\nVehiculos exportados a: {filepath}")
        return df_vehiculos


# ========================== EJECUCION ==========================

if __name__ == "__main__":
    RUTAS_PATH = "rutas_paquetes_dijkstra.csv"
    OUTPUT_DIR = os.getcwd()
    
    print("Iniciando Knapsack 0/1 optimizado para empaque de vehiculos...\n")
    
    # Crear instancia
    knapsack = KnapsackVehiculosOptimizado(
        rutas_path=RUTAS_PATH,
        output_dir=OUTPUT_DIR
    )
    
    # Empacar paquetes
    knapsack.empacar_paquetes()
    
    # Mostrar resultados
    knapsack.mostrar_resultados()
    
    # Exportar a CSV
    df_final = knapsack.exportar_resultados('vehiculos_knapsack_optimizado.csv')
    
    print("\nPrimeras 15 filas:")
    print(df_final.head(15).to_string(index=False))