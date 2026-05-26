// ------------------------------------------------------------------------------- MIN HEAP IMPLEMENTATION ------------------------------------------------------------------------
class MinHeap {
    constructor() {
        this.heap = [];
    }

    push(item) {
        this.heap.push(item);
        this.bubbleUp(this.heap.length - 1);
    }

    pop() {
        if (this.heap.length === 0) return null;
        const min = this.heap[0];
        const last = this.heap.pop();
        if (this.heap.length > 0) {
            this.heap[0] = last;
            this.bubbleDown(0);
        }
        return min;
    }

    isEmpty() {
        return this.heap.length === 0;
    }

    bubbleUp(i) {
        while (i > 0) {
            const parent = Math.floor((i - 1) / 2);
            if (this.heap[parent].peso <= this.heap[i].peso) break;
            [this.heap[parent], this.heap[i]] = [this.heap[i], this.heap[parent]];
            i = parent;
        }
    }

    bubbleDown(i) {
        while (2 * i + 1 < this.heap.length) {
            let smallest = i;
            const left = 2 * i + 1;
            const right = 2 * i + 2;
            
            if (this.heap[left].peso < this.heap[smallest].peso) smallest = left;
            if (right < this.heap.length && this.heap[right].peso < this.heap[smallest].peso) smallest = right;
            
            if (smallest === i) break;
            [this.heap[i], this.heap[smallest]] = [this.heap[smallest], this.heap[i]];
            i = smallest;
        }
    }
}

// ------------------------------------------------------------------------------- CACHE MANAGER -------------------------------------------------------------------------------
class CacheManager {
    constructor() {
        this.rutas = new Map();
        this.knapsack = new Map();
    }

    obtenerRuta(origen, destino) {
        const clave = `${origen}->${destino}`;
        return this.rutas.get(clave);
    }

    guardarRuta(origen, destino, ruta) {
        const clave = `${origen}->${destino}`;
        this.rutas.set(clave, ruta);
    }

    existeRuta(origen, destino) {
        const clave = `${origen}->${destino}`;
        return this.rutas.has(clave);
    }

    obtenerKnapsack(paquetes, capacidad) {
        const clave = this.generarClaveKnapsack(paquetes, capacidad);
        return this.knapsack.get(clave);
    }

    guardarKnapsack(paquetes, capacidad, resultado) {
        const clave = this.generarClaveKnapsack(paquetes, capacidad);
        this.knapsack.set(clave, resultado);
    }

    existeKnapsack(paquetes, capacidad) {
        const clave = this.generarClaveKnapsack(paquetes, capacidad);
        return this.knapsack.has(clave);
    }

    generarClaveKnapsack(paquetes, capacidad) {
        const ids = paquetes.map(p => p.id).sort().join(',');
        return `${ids}|${capacidad}`;
    }

    limpiarKnapsack() {
        this.knapsack.clear();
    }
}

// ==================== GRAPH DATA ====================
const aristasGrafo = [ // Graph with all origin and destiny cities
    { peso: 458, origen: "Bogota", destino: "Cali" },
    { peso: 418, origen: "Bogota", destino: "Medellin" },
    { peso: 239, origen: "Medellin", destino: "Pereira" },
    { peso: 84.6, origen: "Pereira", destino: "Armenia" },
    { peso: 5.4, origen: "Armenia", destino: "Ibague" },
    { peso: 211, origen: "Ibague", destino: "Neiva" },
    { peso: 469, origen: "Neiva", destino: "Pasto" },
    { peso: 386, origen: "Cali", destino: "Pasto" },
    { peso: 1002, origen: "Bogota", destino: "Barranquilla" },
    { peso: 949, origen: "Barranquilla", destino: "Santa_Marta" },
    { peso: 987, origen: "Barranquilla", destino: "Cartagena" },
    { peso: 753, origen: "Medellin", destino: "Barranquilla" },
    { peso: 396, origen: "Pereira", destino: "Villavicencio" },
    { peso: 123, origen: "Bogota", destino: "Villavicencio" },
    { peso: 177, origen: "Pereira", destino: "Manizales" },
    { peso: 163, origen: "Manizales", destino: "Ibague" },
    { peso: 382, origen: "Medellin", destino: "Bucaramanga" },
    { peso: 623, origen: "Cartagena", destino: "Bucaramanga" },
    { peso: 139, origen: "Bogota", destino: "Tunja" }
];

const coordenadasCiudades = { // Coordinates for google maps
    "Bogota": { lat: 4.7110, lng: -74.0721 },
    "Cali": { lat: 3.4516, lng: -76.5320 },
    "Medellin": { lat: 6.2442, lng: -75.5812 },
    "Pereira": { lat: 4.8133, lng: -75.6961 },
    "Armenia": { lat: 4.5339, lng: -75.6811 },
    "Ibague": { lat: 4.4389, lng: -75.2322 },
    "Neiva": { lat: 2.9273, lng: -75.2819 },
    "Pasto": { lat: 1.2136, lng: -77.2811 },
    "Barranquilla": { lat: 10.9685, lng: -74.7813 },
    "Santa_Marta": { lat: 11.2408, lng: -74.1990 },
    "Cartagena": { lat: 10.3910, lng: -75.4794 },
    "Villavicencio": { lat: 4.1420, lng: -73.6266 },
    "Manizales": { lat: 5.0689, lng: -75.5174 },
    "Bucaramanga": { lat: 7.1193, lng: -73.1227 },
    "Tunja": { lat: 5.5353, lng: -73.3678 }
};

const depositosDefinidos = ["Bogota", "Ibague", "Pereira", "Bucaramanga"]; // Main distribution centers from which the packages will be shipped

// ------------------------------------------------------------------------------- GLOBAL STATE -------------------------------------------------------------------------------
let map = null;
let datasetCompletoCSV = []; // All info of the CSV
let paquetesPorCiudad = {}; // Packages grouped by city for efficient processing
let ciudadesValidas = new Set(); // Set of valid cities for O(1) lookup
let lineasRuta = [];
let marcadoresDinamicos = [];
let adyacenciaMST = {}; // MST: all the cities that were selected as the best route
let grafoMST = {}; // Copy of MST for Dijkstra algorithm
let cache = new CacheManager(); // Cache manager for routes and knapsack results

// ------------------------------------------------------------------------------- UTILITY FUNCTIONS -------------------------------------------------------------------------------
function limpiarTextoCiudad(texto) {
    if (!texto) return "";
    return texto.normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/ /g, "_");
}

// ------------------------------------------------------------------------------- LOAD DATASET FROM JSON -------------------------------------------------------------------------------
async function cargarDatasetInstantaneo() {
    const statusLabel = document.getElementById("csv-status");
    try {
        const respuesta = await fetch('dataset.json');
        if (!respuesta.ok) throw new Error("No se encontró el archivo dataset.json");
        
        const datosCargados = await respuesta.json();
        
        datasetCompletoCSV = [];        // Optimized: normalize and group by city in one pass
        paquetesPorCiudad = {};
        
        datosCargados.forEach(p => {
            const ciudadNormalizada = limpiarTextoCiudad(p.Ciudad_Destino);
            const peso = parseFloat(p.Peso_kg) || 1.0;
            
            const paquete = {
                ID_Paquete: p.ID_Paquete,
                Cliente: p.Cliente,
                Ciudad_Destino: ciudadNormalizada,
                Peso_kg: peso
            };
            
            datasetCompletoCSV.push(paquete);
            
            if (!paquetesPorCiudad[ciudadNormalizada]) {      // Group packages by city
                paquetesPorCiudad[ciudadNormalizada] = [];
            }
            paquetesPorCiudad[ciudadNormalizada].push(paquete);
        });

        statusLabel.innerText = `Base Conectada: ${datasetCompletoCSV.length} registros cargados.`;
        statusLabel.style.color = "#16a34a";

    } catch (error) {
        statusLabel.innerText = "Error al mapear el archivo dataset.json local.";
        statusLabel.style.color = "#dc2626";
    }
}

// ------------------------------------------------------------------------------- PRIM ALGORITHM (OPTIMIZED WITH MIN HEAP) -------------------------------------------------------------------------------
function calcularPrimMultiDeposito() {
    let visitados = new Set(depositosDefinidos);
    let colaPrioridad = new MinHeap(); // Use Min Heap instead of array with sort

    // Initialize MST adjacency lists
    Object.keys(coordenadasCiudades).forEach(c => {
        adyacenciaMST[c] = [];
        grafoMST[c] = [];
    });

    // Build complete graph with adjacency list representation
    let grafoCompleto = {};
    Object.keys(coordenadasCiudades).forEach(c => grafoCompleto[c] = []);
    aristasGrafo.forEach(a => {
        grafoCompleto[a.origen].push({ destino: a.destino, peso: a.peso });
        grafoCompleto[a.destino].push({ destino: a.origen, peso: a.peso });
    });

    // Add initial candidates from all deposits
    depositosDefinidos.forEach(dep => {
        grafoCompleto[dep].forEach(vecino => {
            if (!visitados.has(vecino.destino)) {
                colaPrioridad.push({ 
                    peso: vecino.peso, 
                    origen: dep, 
                    destino: vecino.destino 
                });
            }
        });
    });

    while (!colaPrioridad.isEmpty()) {
        let aristaActual = colaPrioridad.pop();

        if (visitados.has(aristaActual.destino)) continue;
        visitados.add(aristaActual.destino);

        adyacenciaMST[aristaActual.origen].push({ 
            destino: aristaActual.destino, 
            peso: aristaActual.peso 
        });
        adyacenciaMST[aristaActual.destino].push({ 
            destino: aristaActual.origen, 
            peso: aristaActual.peso 
        });

        grafoMST[aristaActual.origen].push({    // Keep copy of MST for Dijkstra
            destino: aristaActual.destino, 
            peso: aristaActual.peso 
        });
        grafoMST[aristaActual.destino].push({ 
            destino: aristaActual.origen, 
            peso: aristaActual.peso 
        });

        grafoCompleto[aristaActual.destino].forEach(vecino => {         // Explore neighbors of newly added city
            if (!visitados.has(vecino.destino)) {
                colaPrioridad.push({ 
                    peso: vecino.peso, 
                    origen: aristaActual.destino, 
                    destino: vecino.destino 
                });
            }
        });
    }
}

// ------------------------------------------------------------------------------- DIJKSTRA ALGORITHM -------------------------------------------------------------------------------

function calcularDijkstra(origen, destino) {
    let distancias = {};
    let predecesores = {};
    let visitados = new Set();
    let cola = new MinHeap(); // Use Min Heap instead of array with sort

    // Initialize distances to infinity
    Object.keys(grafoMST).forEach(ciudad => {
        distancias[ciudad] = Infinity;
        predecesores[ciudad] = null;
    });

    distancias[origen] = 0;
    cola.push({ ciudad: origen, dist: 0, peso: 0 });

    while (!cola.isEmpty()) {
        let { ciudad: u } = cola.pop();

        if (visitados.has(u)) continue;
        visitados.add(u);

        if (u === destino) break;

        // Relax edges
        grafoMST[u].forEach(vecino => {
            if (!visitados.has(vecino.destino)) {
                let nuevaDist = distancias[u] + vecino.peso;
                if (nuevaDist < distancias[vecino.destino]) {
                    distancias[vecino.destino] = nuevaDist;
                    predecesores[vecino.destino] = u;
                    cola.push({ 
                        ciudad: vecino.destino, 
                        dist: nuevaDist, 
                        peso: vecino.peso 
                    });
                }
            }
        });
    }

    // Reconstruct path
    let camino = [];
    let actual = destino;
    while (actual !== null) {
        camino.push(actual);
        actual = predecesores[actual];
    }
    camino.reverse();
    
    return camino[0] === origen ? camino : [];
}
// Wrapper function that checks cache before computing Dijkstra
function obtenerRuta(origen, destino) {
    if (cache.existeRuta(origen, destino)) {     // Check if route already computed and cached
        return cache.obtenerRuta(origen, destino);
    }

    // Compute and cache the route
    const ruta = calcularDijkstra(origen, destino);
    cache.guardarRuta(origen, destino, ruta);
    return ruta;
}

// ------------------------------------------------------------------------------- KNAPSACK ALGORITHM -------------------------------------------------------------------------------

function optimizarEmpaqueKnapsack(paquetes, capacidadMax) {
    let n = paquetes.length;
    if (n === 0 || capacidadMax <= 0) return { seleccionados: [], pesoTotal: 0 };

    let capInt = Math.floor(capacidadMax);
    
    let dp = new Uint32Array(capInt + 1);     // Use Typed Arrays for better memory efficiency and performance
    let elecciones = Array(n + 1).fill().map(() => new Uint8Array(capInt + 1)); // 1 byte per boolean

    for (let i = 1; i <= n; i++) {     // Fill DP table
        let pesoItem = Math.floor(paquetes[i - 1].peso);
        for (let w = capInt; w >= pesoItem; w--) {
            if (dp[w - pesoItem] + 1 > dp[w]) {
                dp[w] = dp[w - pesoItem] + 1;
                elecciones[i][w] = 1;
            }
        }
    }

    let w = capInt;     // Reconstruct selected items
    let seleccionados = [];
    for (let i = n; i > 0; i--) {
        if (elecciones[i][w]) {
            seleccionados.push(paquetes[i - 1]);
            w -= Math.floor(paquetes[i - 1].peso);
        }
    }

    let pesoTotal = seleccionados.reduce((sum, p) => sum + p.peso, 0);
    return { seleccionados, pesoTotal };
}

// Wrapper function that checks cache before computing knapsack
function optimizarConCache(paquetes, capacidad) {
    if (cache.existeKnapsack(paquetes, capacidad)) {
        return cache.obtenerKnapsack(paquetes, capacidad);
    }

    // Compute and cache the result
    const resultado = optimizarEmpaqueKnapsack(paquetes, capacidad);
    cache.guardarKnapsack(paquetes, capacidad, resultado);
    return resultado;
}

// ------------------------------------------------------------------------------- GOOGLE MAPS INITIALIZATION -------------------------------------------------------------------------------
function iniciarMapaMundial() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 4.5709, lng: -74.2973 },
        zoom: 6,
        mapTypeControl: false,
        streetViewControl: false
    });

    ciudadesValidas = new Set(Object.keys(coordenadasCiudades));

    calcularPrimMultiDeposito();     // Build MST using Prim algorithm
    
    renderizarPinesFijosDepositos();     // Render deposit markers and info
    
    cargarDatasetInstantaneo();     // Load dataset from JSON file
}

function renderizarPinesFijosDepositos() {
    const contenedor = document.getElementById("depositos-container");
    if (!contenedor) return;
    contenedor.innerHTML = "";

    depositosDefinidos.forEach(dep => {
        new google.maps.Marker({
            position: coordenadasCiudades[dep],
            map: map,
            title: `Centro Logístico: ${dep}`,
            label: "🏬"
        });

        contenedor.innerHTML += `
            <div class="deposito-card">
                <div class="deposito-title">📍 Hub Activo: ${dep}</div>
                <div class="deposito-meta">Conectado al subárbol de cobertura.</div>
            </div>`;
    });
}

function limpiarRender() {
    lineasRuta.forEach(l => l.setMap(null));    // Clear all route lines from map
    marcadoresDinamicos.forEach(m => m.setMap(null));    // Clear all dynamic markers from map
    lineasRuta = [];
    marcadoresDinamicos = [];
}

// ------------------------------------------------------------------------------- EVENT LISTENER (OPTIMIZED) -------------------------------------------------------------------------------
document.getElementById("btn-calcular").addEventListener("click", () => {
    if (!map || datasetCompletoCSV.length === 0) return;

    const origenSeleccionado = document.getElementById("select-deposito").value;

    limpiarRender();    // Clean previous render
    
    cache.limpiarKnapsack();     // Clear knapsack cache when changing depot 

    let listaPaquetesFiltrados = [];
    
    Object.keys(paquetesPorCiudad).forEach(destino => {
        if (ciudadesValidas.has(destino)) {
            const ruta = obtenerRuta(origenSeleccionado, destino);
            
            if (ruta.length > 0) {
                const paquetes = paquetesPorCiudad[destino].map(p => ({                 // Add all packages for this city
                    id: p.ID_Paquete,
                    destino: destino,
                    peso: p.Peso_kg
                }));
                listaPaquetesFiltrados.push(...paquetes);
            }
        }
    });

    // Render routes on map
    const bounds = new google.maps.LatLngBounds();
    const rutasRenderizadas = new Set(); // Track rendered routes to avoid duplicates

    Object.keys(paquetesPorCiudad).forEach(destino => {
        if (ciudadesValidas.has(destino)) {
            const ruta = obtenerRuta(origenSeleccionado, destino); // Cache hit
            
            if (ruta.length > 0 && !rutasRenderizadas.has(destino)) {
                rutasRenderizadas.add(destino);
                
                // Convert city names to coordinates
                let mapaCoordenadas = ruta.map(c => coordenadasCiudades[c]);
                mapaCoordenadas.forEach(coord => bounds.extend(coord));

                // Draw polyline for the route
                let polilinea = new google.maps.Polyline({
                    path: mapaCoordenadas,
                    geodesic: true,
                    strokeColor: "#2563eb",
                    strokeOpacity: 0.8,
                    strokeWeight: 4
                });
                polilinea.setMap(map);
                lineasRuta.push(polilinea);

                // Add numbered markers for each stop
                ruta.forEach((ciudad, index) => {
                    if (index > 0) {
                        let marker = new google.maps.Marker({
                            position: coordenadasCiudades[ciudad],
                            map: map,
                            label: String(index),
                            title: `Punto de parada: ${ciudad}`
                        });
                        marcadoresDinamicos.push(marker);
                    }
                });
            }
        }
    });

    const contenedorVehiculos = document.getElementById("lista-vehiculos-detallada");     // Display vehicle assignment results
    contenedorVehiculos.innerHTML = "";

    let pesoTotalPedidos = listaPaquetesFiltrados.reduce((sum, p) => sum + p.peso, 0);    // Calculate total weight of filtered packages
    
    let capacidadFlota = 30;
    let tipoUnidad = "Flota de Motos Urbanas";

    if (pesoTotalPedidos > 2000) {
        capacidadFlota = 3000;
        tipoUnidad = "Camión Pesado Nacional";
    } else if (pesoTotalPedidos > 100) {
        capacidadFlota = 1000;
        tipoUnidad = "Furgoneta Mediana Regional";
    }

    // Optimize packing using dynamic programming with cache
    let resultadoEmpaque = optimizarConCache(listaPaquetesFiltrados, capacidadFlota);

    // Display results
    if (resultadoEmpaque.seleccionados.length === 0) {
        contenedorVehiculos.innerHTML = `<p class="text-placeholder">No se encontraron entregas programadas en el grafo para este origen.</p>`;
    } else {
        let porcentajeUso = ((resultadoEmpaque.pesoTotal / capacidadFlota) * 100).toFixed(1);
        contenedorVehiculos.innerHTML = `
            <div class="card-vehiculo-asignado" style="border-left: 4px solid #16a34a; background: #fff; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h4 style="margin: 0 0 8px 0; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; color: #1e293b;">📦 DESPACHO INTEGRAL CONSOLIDADO</span>
                    <span style="background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-size:10px;">${porcentajeUso}% Eficiencia</span>
                </h4>
                <p style="margin: 4px 0; font-size: 12px; color: #475569;"><strong>Vehículo Sugerido:</strong> ${tipoUnidad}</p>
                <p style="margin: 4px 0; font-size: 12px; color: #475569;"><strong>Carga del Dataset:</strong> ${resultadoEmpaque.pesoTotal.toFixed(2)} / ${capacidadFlota} kg</p>
                <p style="margin: 4px 0; font-size: 12px; color: #475569;"><strong>Paquetes Asegurados:</strong> ${resultadoEmpaque.seleccionados.length} unidades procesadas.</p>
            </div>
        `;
    }

    if (!bounds.isEmpty()) map.fitBounds(bounds);     // Fit map to bounds of all displayed routes
});