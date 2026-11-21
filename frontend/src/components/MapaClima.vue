<script setup>
import { onMounted, onBeforeUnmount, watch } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Importar las imágenes del marcador para que Vite las incluya al compilar (npm run build)
// Import marker images so Vite bundles them during production build
import iconoMarcador from "leaflet/dist/images/marker-icon.png";
import iconoMarcador2x from "leaflet/dist/images/marker-icon-2x.png";
import sombraMarcador from "leaflet/dist/images/marker-shadow.png";

const propiedades = defineProps({
  latitud: {
    type: Number,
    required: true,
  },
  longitud: {
    type: Number,
    required: true,
  },
  nombreUbicacion: {
    type: String,
    required: true,
  },
  tituloMapa: {
    type: String,
    required: true,
  },
});

const iconoPersonalizado = L.icon({
  iconUrl: iconoMarcador,
  iconRetinaUrl: iconoMarcador2x,
  shadowUrl: sombraMarcador,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

let instanciaMapa = null;
let marcadorUbicacion = null;

onMounted(function iniciarMapa() {
  instanciaMapa = L.map("contenedor-mapa-clima").setView(
    [propiedades.latitud, propiedades.longitud],
    11
  );

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(instanciaMapa);

  marcadorUbicacion = L.marker([propiedades.latitud, propiedades.longitud], {
    icon: iconoPersonalizado,
  })
    .addTo(instanciaMapa)
    .bindPopup(propiedades.nombreUbicacion)
    .openPopup();
});

watch(
  function observarCoordenadas() {
    return [propiedades.latitud, propiedades.longitud, propiedades.nombreUbicacion];
  },
  function actualizarPosicionMapa([nuevaLatitud, nuevaLongitud, nuevoNombre]) {
    if (instanciaMapa !== null && marcadorUbicacion !== null) {
      instanciaMapa.setView([nuevaLatitud, nuevaLongitud], 11);
      marcadorUbicacion.setLatLng([nuevaLatitud, nuevaLongitud]);
      marcadorUbicacion.bindPopup(nuevoNombre).openPopup();
    }
  }
);

onBeforeUnmount(function limpiarMapa() {
  if (instanciaMapa !== null) {
    instanciaMapa.remove();
    instanciaMapa = null;
  }
});
</script>

<template>
  <section class="clay-card caja-mapa">
    <h3>🗺️ {{ propiedades.tituloMapa }}</h3>
    <div id="contenedor-mapa-clima" class="lienzo-mapa"></div>
  </section>
</template>

<style scoped>
.caja-mapa {
  margin-top: 22px;
}

.lienzo-mapa {
  height: 300px;
  width: 100%;
  margin-top: 14px;
  border-radius: var(--radio-mediano);
  overflow: hidden;
  z-index: 1;
}
</style>