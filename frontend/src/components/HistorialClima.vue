<script setup>
import { ref, onMounted } from "vue";

const propiedades = defineProps({
  idiomaActual: {
    type: String,
    required: true,
  },
  direccionServidor: {
    type: String,
    required: true,
  },
});

// Variables del formulario CREATE / CREATE form variables
const ubicacionFormulario = ref("Sunnyvale, California");
const fechaInicio = ref("2026-11-10");
const fechaFin = ref("2026-11-15");
const notasFormulario = ref("");

// Variables de estado y lista / State and list variables
const listaRegistros = ref([]);
const cargandoHistorial = ref(false);
const mensajeErrorHistorial = ref("");

// Variables del modo UPDATE / UPDATE mode variables
const idEditando = ref(null);
const ubicacionEditada = ref("");
const fechaInicioEditada = ref("");
const fechaFinEditada = ref("");
const textoNotaEditada = ref("");

const textos = {
  en: {
    titulo: "Saved Weather History (CRUD & Export)",
    ubicacion: "Location",
    notas: "Notes (optional)",
    botonGuardar: "Save Record",
    exportar: "Export all records:",
    sinRegistros: "No saved records yet. Add your first one above!",
    promedio: "Avg Temp",
    editar: "Edit",
    guardarCambios: "Save Changes",
    cancelar: "Cancel",
    eliminar: "Delete",
  },
  es: {
    titulo: "Historial Guardado del Clima (CRUD y Exportación)",
    ubicacion: "Ubicación",
    notas: "Notas (opcional)",
    botonGuardar: "Guardar Registro",
    exportar: "Exportar todos los registros:",
    sinRegistros: "Aún no hay registros guardados. ¡Crea el primero arriba!",
    promedio: "Temp. Promedio",
    editar: "Editar",
    guardarCambios: "Guardar Cambios",
    cancelar: "Cancelar",
    eliminar: "Eliminar",
  },
};

function obtenerPromedio(registro) {
  if (registro.average_temperature !== undefined && registro.average_temperature !== null) {
    return registro.average_temperature;
  }
  if (registro.average_temp !== undefined && registro.average_temp !== null) {
    return registro.average_temp;
  }
  return "—";
}

// READ: Cargar registros / Load records
async function cargarRegistros() {
  cargandoHistorial.value = true;
  mensajeErrorHistorial.value = "";
  try {
    const respuesta = await fetch(propiedades.direccionServidor + "/api/records");
    const datos = await respuesta.json();
    listaRegistros.value = datos.records || datos;
  } catch (error) {
    mensajeErrorHistorial.value = "Error loading history: " + error.message;
  } finally {
    cargandoHistorial.value = false;
  }
}

// CREATE: Guardar nuevo registro / Save new record
async function crearRegistro() {
  cargandoHistorial.value = true;
  mensajeErrorHistorial.value = "";
  try {
    const respuesta = await fetch(propiedades.direccionServidor + "/api/records", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: ubicacionFormulario.value,
        start_date: fechaInicio.value,
        end_date: fechaFin.value,
        notes: notasFormulario.value,
      }),
    });
    const datos = await respuesta.json();
    if (!respuesta.ok) {
      throw new Error(datos.error || "Could not save record.");
    }
    notasFormulario.value = "";
    await cargarRegistros();
  } catch (error) {
    mensajeErrorHistorial.value = error.message;
  } finally {
    cargandoHistorial.value = false;
  }
}

// Activar edición con todos los campos / Enable editing with all fields
function iniciarEdicion(registro) {
  idEditando.value = registro.id;
  ubicacionEditada.value = registro.location_query || registro.resolved_name || "";
  fechaInicioEditada.value = registro.start_date || "";
  fechaFinEditada.value = registro.end_date || "";
  textoNotaEditada.value = registro.notes || "";
  mensajeErrorHistorial.value = "";
}

function cancelarEdicion() {
  idEditando.value = null;
  ubicacionEditada.value = "";
  fechaInicioEditada.value = "";
  fechaFinEditada.value = "";
  textoNotaEditada.value = "";
}

// UPDATE: Enviar ubicación, fechas y notas validadas / Send validated location, dates, and notes
async function guardarEdicion(idRegistro) {
  cargandoHistorial.value = true;
  mensajeErrorHistorial.value = "";
  try {
    const respuesta = await fetch(
      propiedades.direccionServidor + "/api/records/" + idRegistro,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location: ubicacionEditada.value,
          start_date: fechaInicioEditada.value,
          end_date: fechaFinEditada.value,
          notes: textoNotaEditada.value,
        }),
      }
    );
    const datos = await respuesta.json();
    if (!respuesta.ok) {
      throw new Error(datos.error || "Could not update record.");
    }
    cancelarEdicion();
    await cargarRegistros();
  } catch (error) {
    mensajeErrorHistorial.value = error.message;
  } finally {
    cargandoHistorial.value = false;
  }
}

// DELETE: Borrar registro / Delete record
async function eliminarRegistro(idRegistro) {
  mensajeErrorHistorial.value = "";
  try {
    const respuesta = await fetch(
      propiedades.direccionServidor + "/api/records/" + idRegistro,
      { method: "DELETE" }
    );
    if (!respuesta.ok) {
      throw new Error("Could not delete record.");
    }
    await cargarRegistros();
  } catch (error) {
    mensajeErrorHistorial.value = error.message;
  }
}

function exportarHistorial(formato) {
  const enlaceDescarga =
    propiedades.direccionServidor + "/api/export/" + formato;
  window.open(enlaceDescarga, "_blank");
}

onMounted(function alIniciarComponente() {
  cargarRegistros();
});
</script>

<template>
  <section class="clay-card caja-historial">
    <h3>🗂️ {{ textos[propiedades.idiomaActual].titulo }}</h3>

    <!-- Formulario CREATE / CREATE Form -->
    <form class="formulario-crud" @submit.prevent="crearRegistro">
      <input
        v-model="ubicacionFormulario"
        type="text"
        class="clay-input"
        :placeholder="textos[propiedades.idiomaActual].ubicacion"
        required
      />
      <input v-model="fechaInicio" type="date" class="clay-input" required />
      <input v-model="fechaFin" type="date" class="clay-input" required />
      <input
        v-model="notasFormulario"
        type="text"
        class="clay-input"
        :placeholder="textos[propiedades.idiomaActual].notas"
      />
      <button
        type="submit"
        class="clay-btn clay-btn-primary"
        :disabled="cargandoHistorial"
      >
        💾 {{ textos[propiedades.idiomaActual].botonGuardar }}
      </button>
    </form>

    <!-- Botones de exportación / Export buttons -->
    <div class="barra-exportar">
      <span>{{ textos[propiedades.idiomaActual].exportar }}</span>
      <button class="clay-btn" @click="exportarHistorial('json')">JSON</button>
      <button class="clay-btn" @click="exportarHistorial('csv')">CSV</button>
      <button class="clay-btn" @click="exportarHistorial('md')">Markdown</button>
      <button class="clay-btn" @click="exportarHistorial('pdf')">PDF</button>
    </div>

    <div v-if="mensajeErrorHistorial !== ''" class="error-banner">
      ⚠️ {{ mensajeErrorHistorial }}
    </div>

    <p v-if="listaRegistros.length === 0 && !cargandoHistorial" class="texto-vacio">
      {{ textos[propiedades.idiomaActual].sinRegistros }}
    </p>

    <div v-else class="lista-registros">
      <article
        v-for="registro in listaRegistros"
        :key="registro.id"
        class="tarjeta-registro"
      >
        <!-- Modo edición completo (UPDATE) / Full edit mode (UPDATE) -->
        <form
          v-if="idEditando === registro.id"
          class="formulario-edicion"
          @submit.prevent="guardarEdicion(registro.id)"
        >
          <input
            v-model="ubicacionEditada"
            type="text"
            class="clay-input"
            :placeholder="textos[propiedades.idiomaActual].ubicacion"
            required
          />
          <input v-model="fechaInicioEditada" type="date" class="clay-input" required />
          <input v-model="fechaFinEditada" type="date" class="clay-input" required />
          <input
            v-model="textoNotaEditada"
            type="text"
            class="clay-input"
            :placeholder="textos[propiedades.idiomaActual].notas"
          />
          <div class="acciones-registro">
            <button
              type="submit"
              class="clay-btn clay-btn-primary"
              :disabled="cargandoHistorial"
            >
              💾 {{ textos[propiedades.idiomaActual].guardarCambios }}
            </button>
            <button type="button" class="clay-btn" @click="cancelarEdicion">
              {{ textos[propiedades.idiomaActual].cancelar }}
            </button>
          </div>
        </form>

        <!-- Modo lectura normal / Normal read mode -->
        <div v-else>
          <div class="cabecera-registro">
            <strong>📍 {{ registro.resolved_name }}</strong>
            <span class="insignia-fechas">
              {{ registro.start_date }} → {{ registro.end_date }}
            </span>
          </div>

          <p class="dato-promedio">
            🌡️ {{ textos[propiedades.idiomaActual].promedio }}:
            <strong>{{ obtenerPromedio(registro) }}°C</strong>
          </p>

          <div class="pie-registro">
            <p class="texto-notas">📝 {{ registro.notes || "—" }}</p>
            <div class="acciones-registro">
              <button class="clay-btn" @click="iniciarEdicion(registro)">
                ✏️ {{ textos[propiedades.idiomaActual].editar }}
              </button>
              <button
                class="clay-btn boton-peligro"
                @click="eliminarRegistro(registro.id)"
              >
                🗑️ {{ textos[propiedades.idiomaActual].eliminar }}
              </button>
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.caja-historial {
  margin-top: 22px;
}

.formulario-crud,
.formulario-edicion {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.barra-exportar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  font-weight: 700;
}

.texto-vacio {
  margin-top: 18px;
  color: var(--color-texto-suave);
}

.lista-registros {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}

.tarjeta-registro {
  background: var(--color-superficie-suave);
  border-radius: var(--radio-mediano);
  padding: 16px;
  box-shadow: var(--sombra-clay-pequena);
}

.cabecera-registro {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
}

.insignia-fechas {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-primario-oscuro);
}

.dato-promedio {
  margin: 8px 0;
}

.pie-registro {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.texto-notas {
  color: var(--color-texto-suave);
  font-size: 0.92rem;
}

.acciones-registro {
  display: flex;
  gap: 8px;
}

.boton-peligro {
  color: var(--color-peligro);
}
</style>