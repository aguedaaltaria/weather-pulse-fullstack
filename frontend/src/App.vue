<script setup>
import { ref } from "vue";
import MapaClima from "./components/MapaClima.vue";
import HistorialClima from "./components/HistorialClima.vue";

// En desarrollo (Vite) apunta al puerto 5003; en producción usa la misma dirección del servidor
// In development (Vite) points to port 5003; in production uses the same server address
let direccionServidor = "";
if (import.meta.env.DEV) {
  direccionServidor = "http://127.0.0.1:5003";
}

const tituloAplicacion = "WeatherPulse Studio";
const nombreAutora = "Águeda Arelis Guzmán Durán";

const idiomaActual = ref("en");
const mostrarVentanaInfo = ref(false);

// Sistema de unidades: "metrico" (°C, km/h) o "imperial" (°F, mph)
// Unit system: "metrico" (°C, km/h) or "imperial" (°F, mph)
const sistemaUnidades = ref("metrico");

const textoBusqueda = ref("Sunnyvale, California");
const datosClima = ref(null);
const estaCargando = ref(false);
const mensajeError = ref("");

const textosPorIdioma = {
  en: {
    creadoPor: "Built by",
    botonIdioma: "Español",
    botonInfo: "Info",
    tituloModal: "About Product Manager Accelerator",
    descripcionModal:
      "Product Manager Accelerator (PMA) is a global community and training program dedicated to helping professionals launch impactful careers in Product Management, Software Engineering, and AI Product Development.",
    botonCerrar: "Close",
    textoGuiaBusqueda: "City, ZIP code, landmark, or GPS (lat, lon)...",
    botonBuscar: "Search",
    botonUbicacion: "My Location",
    cargandoClima: "Fetching live weather...",
    enTiempoReal: "Live Weather",
    sensacionTermica: "Feels like",
    humedad: "Humidity",
    viento: "Wind",
    tituloConsejoIA: "Gemini AI Weather Tip",
    tituloPronostico: "5-Day Forecast",
    tituloCurva: "Weekly Temperature Curve",
    tituloMapa: "Interactive Location Map",
    errorSinGeolocalizacion: "Your browser does not support geolocation.",
    errorPermisoUbicacion: "Location permission was denied.",
  },
  es: {
    creadoPor: "Creado por",
    botonIdioma: "English",
    botonInfo: "Info",
    tituloModal: "Sobre Product Manager Accelerator",
    descripcionModal:
      "Product Manager Accelerator (PMA) es una red global de formación dedicada a impulsar a profesionales en el lanzamiento de productos de Inteligencia Artificial, Ingeniería de Software y Gestión de Productos.",
    botonCerrar: "Cerrar",
    textoGuiaBusqueda: "Ciudad, código postal, lugar o GPS (lat, lon)...",
    botonBuscar: "Buscar",
    botonUbicacion: "Mi Ubicación",
    cargandoClima: "Consultando el clima en vivo...",
    enTiempoReal: "En Tiempo Real",
    sensacionTermica: "Sensación térmica",
    humedad: "Humedad",
    viento: "Viento",
    tituloConsejoIA: "Consejo del Clima con Gemini IA",
    tituloPronostico: "Pronóstico de 5 Días",
    tituloCurva: "Curva Semanal de Temperaturas",
    tituloMapa: "Mapa Interactivo de Ubicación",
    errorSinGeolocalizacion: "Tu navegador no soporta geolocalización.",
    errorPermisoUbicacion: "El permiso de ubicación fue denegado.",
  },
};

function cambiarIdioma() {
  if (idiomaActual.value === "en") {
    idiomaActual.value = "es";
  } else {
    idiomaActual.value = "en";
  }

  if (datosClima.value !== null) {
    buscarClimaPorTexto();
  }
}

function cambiarSistemaUnidades() {
  if (sistemaUnidades.value === "metrico") {
    sistemaUnidades.value = "imperial";
  } else {
    sistemaUnidades.value = "metrico";
  }
}

function obtenerTextoBotonUnidades() {
  if (sistemaUnidades.value === "metrico") {
    return "°F / mph";
  }
  return "°C / km/h";
}

function formatearTemperatura(gradosCelsius) {
  if (gradosCelsius === null || gradosCelsius === undefined) {
    return "—";
  }
  if (sistemaUnidades.value === "imperial") {
    const gradosFahrenheit = (gradosCelsius * 9) / 5 + 32;
    return Math.round(gradosFahrenheit) + "°F";
  }
  return Math.round(gradosCelsius) + "°C";
}

function formatearViento(kilometrosPorHora) {
  if (kilometrosPorHora === null || kilometrosPorHora === undefined) {
    return "—";
  }
  if (sistemaUnidades.value === "imperial") {
    const millasPorHora = kilometrosPorHora * 0.621371;
    return millasPorHora.toFixed(1) + " mph";
  }
  return kilometrosPorHora + " km/h";
}

function obtenerIconoClima(nombreIcono) {
  const mapaIconos = {
    clear: "☀️",
    "partly-cloudy": "⛅",
    cloudy: "☁️",
    fog: "🌫️",
    drizzle: "🌦️",
    rain: "🌧️",
    snow: "❄️",
    storm: "⛈️",
  };
  return mapaIconos[nombreIcono] || "🌤️";
}

function calcularAlturaBarra(temperaturaMaxima) {
  const porcentaje = Math.min(Math.max((temperaturaMaxima + 5) * 2.5, 25), 100);
  return porcentaje + "%";
}

function abrirVentanaInfo() {
  mostrarVentanaInfo.value = true;
}

function cerrarVentanaInfo() {
  mostrarVentanaInfo.value = false;
}

async function buscarClimaPorTexto() {
  const textoLimpio = textoBusqueda.value.trim();
  if (textoLimpio === "") {
    return;
  }

  estaCargando.value = true;
  mensajeError.value = "";

  try {
    const ubicacionCodificada = encodeURIComponent(textoLimpio);
    const enlacePeticion =
      direccionServidor +
      "/api/weather?location=" +
      ubicacionCodificada +
      "&lang=" +
      idiomaActual.value;

    const respuesta = await fetch(enlacePeticion);
    const datos = await respuesta.json();

    if (!respuesta.ok) {
      throw new Error(datos.error || "No se pudo obtener el clima.");
    }

    datosClima.value = datos;
  } catch (error) {
    mensajeError.value = error.message;
  } finally {
    estaCargando.value = false;
  }
}

function buscarClimaPorUbicacionActual() {
  if (!navigator.geolocation) {
    mensajeError.value =
      textosPorIdioma[idiomaActual.value].errorSinGeolocalizacion;
    return;
  }

  estaCargando.value = true;
  mensajeError.value = "";

  navigator.geolocation.getCurrentPosition(
    async function alObtenerUbicacion(posicion) {
      try {
        const latitud = posicion.coords.latitude;
        const longitud = posicion.coords.longitude;
        const enlacePeticion =
          direccionServidor +
          "/api/weather?lat=" +
          latitud +
          "&lon=" +
          longitud +
          "&lang=" +
          idiomaActual.value;

        const respuesta = await fetch(enlacePeticion);
        const datos = await respuesta.json();

        if (!respuesta.ok) {
          throw new Error(datos.error || "No se pudo obtener el clima por GPS.");
        }

        datosClima.value = datos;
        textoBusqueda.value = datos.location.resolved_name;
      } catch (error) {
        mensajeError.value = error.message;
      } finally {
        estaCargando.value = false;
      }
    },
    function alFallarUbicacion() {
      estaCargando.value = false;
      mensajeError.value =
        textosPorIdioma[idiomaActual.value].errorPermisoUbicacion;
    }
  );
}
</script>

<template>
  <div class="app-shell">
    <!-- Encabezado superior / Top header -->
    <header class="clay-card encabezado-superior">
      <div>
        <h1>☀️ {{ tituloAplicacion }}</h1>
        <p>
          {{ textosPorIdioma[idiomaActual].creadoPor }}
          <strong>{{ nombreAutora }}</strong>
        </p>
      </div>

      <div class="botones-encabezado">
        <button class="clay-btn" @click="cambiarSistemaUnidades">
          🌡️ {{ obtenerTextoBotonUnidades() }}
        </button>

        <button class="clay-btn" @click="cambiarIdioma">
          🌐 {{ textosPorIdioma[idiomaActual].botonIdioma }}
        </button>

        <button class="clay-btn clay-btn-primary" @click="abrirVentanaInfo">
          ℹ️ {{ textosPorIdioma[idiomaActual].botonInfo }}
        </button>
      </div>
    </header>

    <!-- Barra de búsqueda / Search bar -->
    <section class="clay-card caja-busqueda">
      <form class="formulario-busqueda" @submit.prevent="buscarClimaPorTexto">
        <input
          v-model="textoBusqueda"
          type="text"
          class="clay-input"
          :placeholder="textosPorIdioma[idiomaActual].textoGuiaBusqueda"
        />
        <button
          type="submit"
          class="clay-btn clay-btn-primary"
          :disabled="estaCargando"
        >
          🔍 {{ textosPorIdioma[idiomaActual].botonBuscar }}
        </button>

        <button
          type="button"
          class="clay-btn"
          :disabled="estaCargando"
          @click="buscarClimaPorUbicacionActual"
        >
          📍 {{ textosPorIdioma[idiomaActual].botonUbicacion }}
        </button>
      </form>
    </section>

    <div v-if="mensajeError !== ''" class="error-banner">
      ⚠️ {{ mensajeError }}
    </div>

    <div v-if="estaCargando" class="clay-card caja-carga">
      {{ textosPorIdioma[idiomaActual].cargandoClima }}
    </div>

    <!-- Panel principal unificado / Unified main dashboard -->
    <main v-if="datosClima !== null && !estaCargando">
      <!-- Fila 1: Clima actual + Condiciones detalladas + Gemini IA -->
      <div class="main-grid">
        <section class="tarjeta-hero-terracota">
          <div class="hero-encabezado">
            <span class="pildora-en-vivo">
              ● {{ textosPorIdioma[idiomaActual].enTiempoReal }}
            </span>
            <span class="icono-clima-grande">
              {{ obtenerIconoClima(datosClima.current.icon) }}
            </span>
          </div>

          <p class="hero-ubicacion">📍 {{ datosClima.location.resolved_name }}</p>
          <p class="hero-descripcion">{{ datosClima.current.description }}</p>

          <div class="hero-pie">
            <span class="temperatura-grande">
              {{ formatearTemperatura(datosClima.current.temperature) }}
            </span>
            <span class="pildora-sensacion">
              {{ textosPorIdioma[idiomaActual].sensacionTermica }}:
              {{ formatearTemperatura(datosClima.current.apparent_temperature) }}
            </span>
          </div>
        </section>

        <div class="columna-derecha">
          <div class="cuadricula-condiciones">
            <div class="clay-card mini-tarjeta-metrica">
              <span class="etiqueta-metrica">
                💧 {{ textosPorIdioma[idiomaActual].humedad }}
              </span>
              <strong class="valor-metrica">
                {{ datosClima.current.humidity }}%
              </strong>
              <div class="barra-progreso-fondo">
                <div
                  class="barra-progreso-relleno"
                  :style="{ width: datosClima.current.humidity + '%' }"
                ></div>
              </div>
            </div>

            <div class="clay-card mini-tarjeta-metrica">
              <span class="etiqueta-metrica">
                💨 {{ textosPorIdioma[idiomaActual].viento }}
              </span>
              <strong class="valor-metrica">
                {{ formatearViento(datosClima.current.wind_speed) }}
              </strong>
              <div class="barra-progreso-fondo">
                <div
                  class="barra-progreso-relleno"
                  :style="{
                    width: Math.min(datosClima.current.wind_speed * 3, 100) + '%',
                  }"
                ></div>
              </div>
            </div>
          </div>

          <section class="tarjeta-ia-durazno">
            <h3>✨ {{ textosPorIdioma[idiomaActual].tituloConsejoIA }}</h3>
            <p class="texto-consejo-ia">{{ datosClima.ai_advice }}</p>
            <small class="etiqueta-modelo">
              Modelo: {{ datosClima.ai_model }}
            </small>
          </section>
        </div>
      </div>

      <!-- Fila 2: Pronóstico de 5 días + Curva Semanal lado a lado -->
      <div class="cuadricula-pronostico-curva">
        <section class="clay-card">
          <h3>📅 {{ textosPorIdioma[idiomaActual].tituloPronostico }}</h3>
          <div class="lista-pronostico">
            <div
              v-for="dia in datosClima.forecast_5_days"
              :key="dia.date"
              class="fila-dia-pronostico"
            >
              <div class="dia-izquierda">
                <span class="icono-dia">{{ obtenerIconoClima(dia.icon) }}</span>
                <div>
                  <strong>{{ dia.date }}</strong>
                  <p class="descripcion-dia">{{ dia.description }}</p>
                </div>
              </div>

              <div class="dia-derecha">
                <span class="temperatura-minima">
                  {{ formatearTemperatura(dia.temperature_min) }}
                </span>
                <span class="barra-temperatura"></span>
                <span class="temperatura-maxima">
                  {{ formatearTemperatura(dia.temperature_max) }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <section class="clay-card tarjeta-curva">
          <h3>📊 {{ textosPorIdioma[idiomaActual].tituloCurva }}</h3>
          <div class="grafica-barras">
            <div
              v-for="dia in datosClima.forecast_5_days"
              :key="dia.date + '-barra'"
              class="columna-barra"
            >
              <span class="etiqueta-temp-barra">
                {{ formatearTemperatura(dia.temperature_max) }}
              </span>
              <div class="pista-barra-vertical">
                <div
                  class="barra-vertical"
                  :style="{ height: calcularAlturaBarra(dia.temperature_max) }"
                ></div>
              </div>
              <small class="fecha-corta">{{ dia.date.slice(5) }}</small>
            </div>
          </div>
        </section>
      </div>

      <!-- Fila 3: Mapa interactivo -->
      <MapaClima
        :latitud="datosClima.location.latitude"
        :longitud="datosClima.location.longitude"
        :nombreUbicacion="datosClima.location.resolved_name"
        :tituloMapa="textosPorIdioma[idiomaActual].tituloMapa"
      />
    </main>

    <!-- Fila 4: Historial CRUD y Exportación -->
    <HistorialClima
      :idiomaActual="idiomaActual"
      :direccionServidor="direccionServidor"
    />

    <!-- Ventana modal de PM Accelerator / PM Accelerator info modal -->
    <div
      v-if="mostrarVentanaInfo"
      class="fondo-modal"
      @click.self="cerrarVentanaInfo"
    >
      <div class="clay-card tarjeta-modal">
        <h2>{{ textosPorIdioma[idiomaActual].tituloModal }}</h2>
        <p class="texto-modal">
          {{ textosPorIdioma[idiomaActual].descripcionModal }}
        </p>
        <button class="clay-btn clay-btn-primary" @click="cerrarVentanaInfo">
          {{ textosPorIdioma[idiomaActual].botonCerrar }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.encabezado-superior {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.botones-encabezado {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.caja-busqueda {
  margin-top: 18px;
  padding: 16px 20px;
}

.formulario-busqueda {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.formulario-busqueda .clay-input {
  flex: 1;
  min-width: 220px;
}

.caja-carga {
  margin-top: 20px;
  text-align: center;
  font-weight: 700;
}

.tarjeta-hero-terracota {
  background: linear-gradient(145deg, #e87a64 0%, #f3a183 100%);
  color: #ffffff;
  border-radius: var(--radio-grande);
  padding: 26px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow:
    12px 14px 28px rgba(224, 114, 92, 0.35),
    inset 3px 3px 8px rgba(255, 255, 255, 0.35);
}

.hero-encabezado {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.pildora-en-vivo {
  background: rgba(255, 255, 255, 0.22);
  padding: 6px 14px;
  border-radius: var(--radio-pildora);
  font-size: 0.8rem;
  font-weight: 700;
}

.icono-clima-grande {
  font-size: 3.4rem;
  line-height: 1;
  filter: drop-shadow(0 6px 10px rgba(0, 0, 0, 0.15));
}

.hero-ubicacion {
  font-size: 0.95rem;
  font-weight: 700;
  opacity: 0.95;
  margin-top: 10px;
}

.hero-descripcion {
  font-size: 1.35rem;
  font-weight: 800;
  margin-top: 4px;
}

.hero-pie {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
  margin-top: 18px;
}

.temperatura-grande {
  font-size: 3.6rem;
  font-weight: 800;
  line-height: 1;
}

.pildora-sensacion {
  background: rgba(255, 255, 255, 0.22);
  padding: 8px 14px;
  border-radius: var(--radio-pildora);
  font-size: 0.85rem;
  font-weight: 700;
}

.columna-derecha {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cuadricula-condiciones {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.mini-tarjeta-metrica {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.etiqueta-metrica {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--color-texto-suave);
}

.valor-metrica {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--color-texto);
}

.barra-progreso-fondo {
  width: 100%;
  height: 8px;
  background: var(--color-superficie-suave);
  border-radius: var(--radio-pildora);
  overflow: hidden;
  margin-top: 6px;
}

.barra-progreso-relleno {
  height: 100%;
  background: linear-gradient(90deg, var(--color-secundario), var(--color-primario));
  border-radius: var(--radio-pildora);
}

.tarjeta-ia-durazno {
  background: linear-gradient(145deg, #fde8dc, #fff4ee);
  border-radius: var(--radio-grande);
  padding: 20px 22px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
  box-shadow: var(--sombra-clay);
}

.texto-consejo-ia {
  font-size: 0.95rem;
  line-height: 1.5;
}

.etiqueta-modelo {
  color: var(--color-texto-suave);
  font-weight: 700;
}

/* Fila 2: Pronóstico y Curva lado a lado / Row 2: Forecast and Curve side-by-side */
.cuadricula-pronostico-curva {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 20px;
  margin-top: 22px;
}

.lista-pronostico {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.fila-dia-pronostico {
  background: var(--color-superficie-suave);
  border-radius: var(--radio-mediano);
  padding: 12px 16px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  box-shadow: var(--sombra-clay-pequena);
}

.dia-izquierda {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icono-dia {
  font-size: 1.5rem;
}

.descripcion-dia {
  font-size: 0.82rem;
  color: var(--color-texto-suave);
}

.dia-derecha {
  display: flex;
  align-items: center;
  gap: 8px;
}

.barra-temperatura {
  width: 56px;
  height: 8px;
  border-radius: var(--radio-pildora);
  background: linear-gradient(90deg, #f4c2a3, #e67862);
}

.temperatura-maxima {
  font-weight: 800;
  color: var(--color-primario-oscuro);
}

.temperatura-minima {
  font-weight: 700;
  color: var(--color-texto-suave);
}

.tarjeta-curva {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.grafica-barras {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  margin-top: 20px;
  align-items: end;
}

.columna-barra {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.etiqueta-temp-barra {
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--color-primario-oscuro);
}

.pista-barra-vertical {
  width: 24px;
  height: 150px;
  background: var(--color-superficie-suave);
  border-radius: var(--radio-pildora);
  display: flex;
  align-items: flex-end;
  padding: 4px;
  box-shadow: inset 2px 2px 6px rgba(186, 128, 108, 0.16);
}

.barra-vertical {
  width: 100%;
  border-radius: var(--radio-pildora);
  background: linear-gradient(180deg, var(--color-primario), var(--color-secundario));
}

.fecha-corta {
  font-weight: 700;
  color: var(--color-texto-suave);
}

.fondo-modal {
  position: fixed;
  inset: 0;
  background: rgba(61, 44, 46, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1000;
}

.tarjeta-modal {
  max-width: 480px;
  width: 100%;
}

.texto-modal {
  margin: 14px 0 20px;
}

@media (max-width: 820px) {
  .cuadricula-pronostico-curva {
    grid-template-columns: 1fr;
  }
}
</style>