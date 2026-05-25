
const aristasGrafo = [
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

const coordenadasCiudades = {
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

const depositosDefinidos = ["Bogota", "Ibague", "Pereira", "Bucaramanga"];

let map = null;
let datasetCompletoCSV = []; 
let lineasRuta = [];
let marcadoresDinamicos = [];
let adyacenciaMST = {}; 

function limpiarTextoCiudad(texto) {
    if (!texto) return "";
    return texto.normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(" ", "_");
}

//-------------------------------------------------------------------------------------Load info for dataset.json------------------------------------------------------------------------------
async function cargarDatasetInstantaneo() {
    const statusLabel = document.getElementById("csv-status");
    try {
        const respuesta = await fetch('dataset.json');
        if (!respuesta.ok) throw new Error("No se encontró el archivo dataset.json");
        
        const datosCargados = await respuesta.json();
        
        datasetCompletoCSV = datosCargados.map(p => ({
            ID_Paquete: p.ID_Paquete,
            Cliente: p.Cliente,
            Ciudad_Destino: p.Ciudad_Destino,
            Peso_kg: parseFloat(p.Peso_kg) || 0
        }));

        statusLabel.innerText = `Base Conectada: ${datasetCompletoCSV.length} registros cargados.`;
        statusLabel.style.color = "#16a34a";

    } catch (error) {
        console.error(error);
        statusLabel.innerText = "Error al mapear el archivo dataset.json local.";
        statusLabel.style.color = "#dc2626";
    }
}

//-----------------------------------------------------------------------------------Prim Algorithm-------------------------------------------------------------------------------------------

function calcularPrimMultiDeposito() {
    let visitados = new Set(depositosDefinidos);
    let colaPrioridad = [];

    Object.keys(coordenadasCiudades).forEach(c => adyacenciaMST[c] = []);

    let grafoCompleto = {};
    Object.keys(coordenadasCiudades).forEach(c => grafoCompleto[c] = []);
    aristasGrafo.forEach(a => {
        grafoCompleto[a.origen].push({ destino: a.destino, peso: a.peso });
        grafoCompleto[a.destino].push({ destino: a.origen, peso: a.peso });
    });

    depositosDefinidos.forEach(dep => {
        grafoCompleto[dep].forEach(vecino => {
            if (!visitados.has(vecino.destino)) {
                colaPrioridad.push({ peso: vecino.peso, origen: dep, destino: vecino.destino });
            }
        });
    });

    while (colaPrioridad.length > 0) {
        colaPrioridad.sort((a, b) => a.peso - b.peso);
        let aristaActual = colaPrioridad.shift();

        if (visitados.has(aristaActual.destino)) continue;
        visitados.add(aristaActual.destino);

        adyacenciaMST[aristaActual.origen].push({ destino: aristaActual.destino, peso: aristaActual.peso });
        adyacenciaMST[aristaActual.destino].push({ destino: aristaActual.origen, peso: aristaActual.peso });

        grafoCompleto[aristaActual.destino].forEach(vecino => {
            if (!visitados.has(vecino.destino)) {
                colaPrioridad.push({ peso: vecino.peso, origen: aristaActual.destino, destino: vecino.destino });
            }
        });
    }
}

//-----------------------------------------------------------------------------------Dikstra algorithm------------------------------------------------------------------------------------------------------

function calcularDijkstra(origen, destino) {
    let distancias = {}; let predecesores = {};
    let visitados = new Set(); let cola = [];

    Object.keys(adyacenciaMST).forEach(ciudad => {
        distancias[ciudad] = Infinity; predecesores[ciudad] = null;
    });

    distancias[origen] = 0;
    cola.push({ ciudad: origen, dist: 0 });

    while (cola.length > 0) {
        cola.sort((a, b) => a.dist - b.dist);
        let { ciudad: u } = cola.shift();

        if (visitados.has(u)) continue;
        visitados.add(u);

        if (u === destino) break;

        adyacenciaMST[u].forEach(vecino => {
            if (!visitados.has(vecino.destino)) {
                let nuevaDist = distancias[u] + vecino.peso;
                if (nuevaDist < distancias[vecino.destino]) {
                    distancias[vecino.destino] = nuevaDist;
                    predecesores[vecino.destino] = u;
                    cola.push({ ciudad: vecino.destino, dist: nuevaDist });
                }
            }
        });
    }

    let camino = []; let actual = destino;
    while (actual !== null) {
        camino.push(actual); actual = predecesores[actual];
    }
    camino.reverse();
    return camino[0] === origen ? camino : [];
}

//--------------------------------------------------------------------------------------Knapsack algorithm----------------------------------------------------------------------------------
function optimizarEmpaqueKnapsack(paquetes, capacidadMax) {
    let n = paquetes.length;
    if (n === 0 || capacidadMax <= 0) return { seleccionados: [], pesoTotal: 0 };

    let capInt = Math.floor(capacidadMax);
    let dp = Array(capInt + 1).fill(0);
    let elecciones = Array(n + 1).fill().map(() => Array(capInt + 1).fill(false));

    for (let i = 1; i <= n; i++) {
        let pesoItem = Math.floor(paquetes[i - 1].peso);
        for (let w = capInt; w >= pesoItem; w--) {
            if (dp[w - pesoItem] + 1 > dp[w]) {
                dp[w] = dp[w - pesoItem] + 1;
                elecciones[i][w] = true;
            }
        }
    }

    let w = capInt;
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

//---------------------------------------------------------------------------------------Google maps-----------------------------------------------------------------------------------------------------------------
function iniciarMapaMundial() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 4.5709, lng: -74.2973 },
        zoom: 6,
        mapTypeControl: false,
        streetViewControl: false
    });

    calcularPrimMultiDeposito();
    renderizarPinesFijosDepositos();
    cargarDatasetInstantaneo(); 
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

document.getElementById("btn-calcular").addEventListener("click", () => {
    if (!map || datasetCompletoCSV.length === 0) return;

    const origenSeleccionado = document.getElementById("select-deposito").value;

    // Limpieza total del render anterior
    lineasRuta.forEach(l => l.setMap(null)); marcadoresDinamicos.forEach(m => m.setMap(null));
    lineasRuta = []; marcadoresDinamicos = [];

    let ciudadesDestinoEncontradas = new Set();
    let listaPaquetesFiltrados = [];

    datasetCompletoCSV.forEach(row => {
        let destinoNormalizado = limpiarTextoCiudad(row.Ciudad_Destino);
        
        if (coordenadasCiudades[destinoNormalizado]) {
            let rutaCalculada = calcularDijkstra(origenSeleccionado, destinoNormalizado);
            
            if (rutaCalculada.length > 0) {
                ciudadesDestinoEncontradas.add(destinoNormalizado);
                listaPaquetesFiltrados.push({
                    id: row.ID_Paquete,
                    destino: destinoNormalizado,
                    peso: parseFloat(row.Peso_kg) || 1.0
                });
            }
        }
    });

    const bounds = new google.maps.LatLngBounds();
    ciudadesDestinoEncontradas.forEach(destino => {
        let caminoNodos = calcularDijkstra(origenSeleccionado, destino);
        let mapaCoordenadas = caminoNodos.map(c => coordenadasCiudades[c]);

        mapaCoordenadas.forEach(coord => bounds.extend(coord));

        let polilinea = new google.maps.Polyline({
            path: mapaCoordenadas,
            geodesic: true,
            strokeColor: "#2563eb",
            strokeOpacity: 0.8,
            strokeWeight: 4
        });
        polilinea.setMap(map);
        lineasRuta.push(polilinea);

        caminoNodos.forEach((ciudad, index) => {
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
    });

    const contenedorVehiculos = document.getElementById("lista-vehiculos-detallada");
    contenedorVehiculos.innerHTML = "";

    let pesoTotalPedidos = listaPaquetesFiltrados.reduce((sum, p) => sum + p.peso, 0);
    
    let capacidadFlota = 30; 
    let tipoUnidad = "Flota de Motos Urbanas";

    if (pesoTotalPedidos > 2000) {
        capacidadFlota = 3000;
        tipoUnidad = "Camión Pesado Nacional";
    } else if (pesoTotalPedidos > 100) {
        capacidadFlota = 1000;
        tipoUnidad = "Furgoneta Mediana Regional";
    }

    let resultadoEmpaque = optimizarEmpaqueKnapsack(listaPaquetesFiltrados, capacidadFlota);

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

    if (!bounds.isEmpty()) map.fitBounds(bounds);
});