<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue';
import cursoService from '../api/cursoService';
import Swal from 'sweetalert2';
import html2canvas from 'html2canvas';  // para imprimir en imagen ps
import jsPDF from 'jspdf';


const props = defineProps({
  show: Boolean,
  planVersionId: Number,
  planNombre: String
});

const emit = defineEmits(['close']);

// Datos
const cursos = ref([]);
const loading = ref(false);
const itemRefs = ref({}); // Referencias a los elementos DOM de las tarjetas

// Estado de "Juego/Edición"
const isLinkingMode = ref(false);
const sourceCourse = ref(null); // El curso "Requisito" seleccionado

// Flechas calculadas para dibujar
const arrows = ref([]);

// --- CARGA DE DATOS ---
watch(() => props.planVersionId, async (newId) => {
  if (newId && props.show) {
    await loadCursosMalla(newId);
  }
});

const loadCursosMalla = async (idVersion) => {
  loading.value = true;
  try {
    // Asegúrate que tu backend devuelva el campo 'requisitos' o 'es_requisito_de'
    // Necesitamos saber quién es requisito de quién.
    // Si usas Pydantic, asegúrate que el schema CursoResponse incluya 'requisitos'
    const data = await cursoService.getAll(); // O getByVersion si ya lo tienes
    
    // Filtrar manualmente si el endpoint trae todo
    cursos.value = data.filter(c => c.id_plan_version === idVersion);
    
    // Esperar a que el DOM se pinte para calcular flechas
    await nextTick();
    drawArrows();
    
  } catch (error) {
    console.error("Error cargando malla", error);
  } finally {
    loading.value = false;
  }
};

// --- LÓGICA DE DIBUJO MEJORADA ---
const drawArrows = async () => {
  if (!props.show) return;
  arrows.value = [];
  await nextTick();

  const container = document.querySelector('.malla-body');
  if (!container) return;
  
  const containerRect = container.getBoundingClientRect();
  const scrollLeft = container.scrollLeft;
  const scrollTop = container.scrollTop;

  const newArrows = [];

  cursos.value.forEach(curso => {
    if (curso.requisitos && curso.requisitos.length > 0) {
      curso.requisitos.forEach(req => {
        const startEl = itemRefs.value[req.id];
        const endEl = itemRefs.value[curso.id];

        if (startEl && endEl) {
          const startRect = startEl.getBoundingClientRect();
          const endRect = endEl.getBoundingClientRect();

          // PUNTOS DE CONEXIÓN
          // Salida: Lado DERECHO del requisito
          const startX = (startRect.right - containerRect.left) + scrollLeft;
          const startY = (startRect.top + (startRect.height / 2) - containerRect.top) + scrollTop;
          
          // Entrada: Lado IZQUIERDO del destino
          const endX = (endRect.left - containerRect.left) + scrollLeft;
          const endY = (endRect.top + (endRect.height / 2) - containerRect.top) + scrollTop;

          // CÁLCULO ORTOGONAL LIMPIO
          // Calculamos un punto medio en el espacio vacío entre columnas (gap)
          // El gap es de 40px, así que nos movemos 20px a la derecha
          const midX = startX + 20; 

          // Lógica de camino:
          // 1. Moverse al inicio
          // 2. Salir un poco a la derecha (midX)
          // 3. Subir/Bajar a la altura del destino (endY)
          // 4. Ir a la izquierda del destino (endX)
          
          // Ajuste para evitar solapamiento si están en la misma fila visual
          // Si es una línea recta horizontal, el SVG a veces la oculta si el stroke es fino
          // Pero con fill:none se arregla.
          
          const path = `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${endY} L ${endX} ${endY}`;

          newArrows.push({
            id: `${req.id}-${curso.id}`,
            d: path,
            reqId: req.id,
            targetId: curso.id
          });
        }
      });
    }
  });
  arrows.value = newArrows;
};

// Recalcular flechas si cambia el tamaño de la ventana
window.addEventListener('resize', drawArrows);
onUnmounted(() => window.removeEventListener('resize', drawArrows));


// --- INTERACCIÓN "JUEGO" DE ENLAZAR ---

const toggleLinkMode = () => {
    isLinkingMode.value = !isLinkingMode.value;
    sourceCourse.value = null; // Resetear selección
};

const handleCardClick = async (curso) => {
    if (!isLinkingMode.value) return;

    // 1. Selección del ORIGEN (El curso Requisito)
    if (!sourceCourse.value) {
        sourceCourse.value = curso;
        return;
    }

    // 2. Selección del DESTINO (El curso superior)
    const targetCourse = curso;
    const requisito = sourceCourse.value;

    // A. Cancelar si es el mismo curso
    if (targetCourse.id === requisito.id) {
        sourceCourse.value = null; 
        return;
    }

    // B. VERIFICAR SI YA EXISTE LA RELACIÓN (Para poder borrarla)
    // Buscamos si el 'requisito' seleccionado ya está en la lista de requisitos del 'target'
    const relacionExiste = targetCourse.requisitos.some(req => req.id === requisito.id);

    if (relacionExiste) {
        // --- MODO ELIMINACIÓN ---
        const confirm = await Swal.fire({
            title: '¿Eliminar relación?',
            text: `¿Quitar "${requisito.codigo}" como requisito de "${targetCourse.codigo}"?`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        });

        if (confirm.isConfirmed) {
            try {
                await cursoService.removeRequisito(targetCourse.id, requisito.id);
                // Recargar malla
                await loadCursosMalla(props.planVersionId);
                // Feedback visual rápido
                Swal.fire({
                     icon: 'success', 
                     title: 'Eliminado', 
                     toast: true, 
                     position: 'top-end', 
                     showConfirmButton: false, 
                     timer: 1500 
                });
            } catch (error) {
                Swal.fire('Error', 'No se pudo eliminar la relación', 'error');
            }
        }
        // Reseteamos selección pase lo que pase
        sourceCourse.value = null;
        return;
    }

    // C. VALIDACIÓN DE CICLOS (Solo si estamos creando)
    if (requisito.ciclo >= targetCourse.ciclo) {
        Swal.fire({
            icon: 'warning',
            title: 'Lógica incorrecta',
            text: `El requisito (Ciclo ${requisito.ciclo}) debe ser anterior al curso (Ciclo ${targetCourse.ciclo}).`
        });
        sourceCourse.value = null;
        return;
    }

    // D. CREACIÓN DE RELACIÓN
    try {
        await cursoService.addRequisito(targetCourse.id, requisito.id, props.planVersionId);
        await loadCursosMalla(props.planVersionId);
        
        Swal.fire({
             icon: 'success', 
             title: 'Enlazado', 
             toast: true, 
             position: 'top-end', 
             showConfirmButton: false, 
             timer: 1500 
        });
    } catch (error) {
        Swal.fire('Error', 'No se pudo crear el enlace', 'error');
    } finally {
        sourceCourse.value = null;
    }
};
const handleArrowClick = async (arrow) => {
    if (!isLinkingMode.value) return;

    const result = await Swal.fire({
        title: '¿Eliminar prerrequisito?',
        text: 'Se romperá el enlace entre estos cursos.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, romper',
        confirmButtonColor: '#d33'
    });

    if (result.isConfirmed) {
        try {
            // arrow.targetId es el curso, arrow.reqId es el requisito
            await cursoService.removeRequisito(arrow.targetId, arrow.reqId);
            await loadCursosMalla(props.planVersionId);
        } catch (error) {
            Swal.fire('Error', 'No se pudo eliminar', 'error');
        }
    }
};


// --- ORGANIZACIÓN DE CICLOS (Igual que antes) ---
const ciclosMalla = computed(() => {
  const ciclos = {};
  for (let i = 1; i <= 10; i++) ciclos[i] = { obligatorios: [], electivos: [] };

  cursos.value.forEach(curso => {
    const c = curso.ciclo || 1;
    if (!ciclos[c]) ciclos[c] = { obligatorios: [], electivos: [] };
    if (curso.tipo_curso === 'ELECTIVO') ciclos[c].electivos.push(curso);
    else ciclos[c].obligatorios.push(curso);
  });
  return ciclos;
});

const close = () => {
    isLinkingMode.value = false;
    emit('close');
};



const getClasePorTipo = (tipo) => {
    // Ajusta estos strings según lo que devuelva tu base de datos exactamente
    if (!tipo) return 'tipo-general';
    const t = tipo.toUpperCase();
    if (t.includes('ESPECIFI') || t.includes('CARRERA')) return 'tipo-especifico';
    if (t.includes('GENERAL') || t.includes('TRONCO')) return 'tipo-general';
    return 'tipo-general'; // Default
};


// --- FUNCIÓN CORREGIDA: DESCARGAR PDF (ESTABLE) ---
const downloadMalla = async () => {
    // Seleccionamos el contenedor general
    const element = document.querySelector('.malla-container');
    if (!element) return;

    // Guardamos la posición actual del scroll para restaurarla luego
    const originalScrollX = window.scrollX;
    const originalScrollY = window.scrollY;

    // Truco: Scrollear al inicio para evitar cortes en la captura
    window.scrollTo(0, 0);

    try {
        Swal.fire({ 
            title: 'Generando PDF...', 
            text: 'Procesando malla curricular...',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading() 
        });
        
        const canvas = await html2canvas(element, {
            scale: 2, // Calidad alta (2 o 3 está bien)
            useCORS: true,
            backgroundColor: '#ffffff', // Fondo blanco
            scrollY: 0, // Forzar inicio en Y=0
            scrollX: 0, // Forzar inicio en X=0
            
            // --- AQUÍ ESTÁ LA SOLUCIÓN AL ERROR ---
            // En lugar de ignoreElements, usamos onclone.
            // Esto modifica la COPIA invisible, no tu pantalla real.
            onclone: (clonedDoc) => {
                // 1. Ocultar botones en el PDF
                const actionsDiv = clonedDoc.querySelector('.header-actions');
                const closeBtn = clonedDoc.querySelector('.btn-close');
                
                if (actionsDiv) actionsDiv.style.display = 'none'; // Ocultar acciones
                if (closeBtn) closeBtn.style.display = 'none';     // Ocultar la X
                
                // 2. Forzar que el contenedor se expanda totalmente en el PDF
                // Esto evita que salga con barras de scroll
                const clonedContainer = clonedDoc.querySelector('.malla-container');
                const clonedBody = clonedDoc.querySelector('.malla-body');
                
                if (clonedContainer) {
                    clonedContainer.style.height = 'auto';
                    clonedContainer.style.width = 'fit-content';
                    clonedContainer.style.overflow = 'visible';
                }
                if (clonedBody) {
                    clonedBody.style.height = 'auto';
                    clonedBody.style.overflow = 'visible';
                }
            }
        });

        // --- Generación del PDF ---
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('l', 'mm', 'a4'); // Horizontal
        
        const pageWidth = 297; 
        const pageHeight = 210;
        const margin = 10; 

        const imgWidth = canvas.width;
        const imgHeight = canvas.height;
        
        // Ajuste de escala para que entre en la hoja
        const maxW = pageWidth - (margin * 2);
        const maxH = pageHeight - (margin * 2);

        // Calculamos el ratio manteniendo proporciones
        const ratio = Math.min(maxW / imgWidth, maxH / imgHeight);
        
        const finalW = imgWidth * ratio;
        const finalH = imgHeight * ratio;

        // Centrar
        const x = (pageWidth - finalW) / 2;
        const y = (pageHeight - finalH) / 2;

        pdf.addImage(imgData, 'PNG', x, y, finalW, finalH);
        
        const cleanName = props.planNombre ? props.planNombre.replace(/[^a-zA-Z0-9]/g, '_') : 'Malla';
        pdf.save(`Malla_${cleanName}.pdf`);
        
        Swal.close();
        Swal.fire({
             icon: 'success', 
             title: 'PDF Generado', 
             toast: true, 
             position: 'bottom-end', 
             showConfirmButton: false, 
             timer: 3000 
        });

    } catch (error) {
        console.error("Error PDF:", error);
        Swal.fire('Error', 'No se pudo generar el PDF. Intenta reducir el zoom del navegador al 100%.', 'error');
    } finally {
        // Restaurar scroll del usuario
        window.scrollTo(originalScrollX, originalScrollY);
    }
};

</script>

<template>
  <div v-if="show" class="malla-backdrop" @click.self="close">
    <div class="malla-container">
      <div class="actions">
            <button class="btn-action" title="Descargar PDF" @click="downloadMalla">
                📄 Descargar PDF
            </button>
            <button 
                @click="toggleLinkMode" 
                :class="['btn-link-mode', isLinkingMode ? 'active' : '']"
            >
                {{ isLinkingMode ? '🛑 Terminar Edición' : '🔗 Conectar Cursos' }}
            </button>
            <button class="btn-close" @click="close">×</button>
        </div>
      <div class="malla-header">
        
        <div>
           <h2>Malla Curricular Interactiva</h2>
           <p class="text-sm text-gray">{{ planNombre }}</p>
        </div>
        
        
      </div>

      <div class="malla-body">
        <div class="malla-content-wrapper">

            <svg class="arrows-layer">
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
                    </marker>
                    <marker id="arrowhead-hover" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
                    </marker>
                </defs>
                <g v-for="arrow in arrows" :key="arrow.id" class="arrow-group" @click="handleArrowClick(arrow)">
                     <path :d="arrow.d" class="click-zone" />
                     <path :d="arrow.d" class="connector-line" :class="{ 'danger-line': isLinkingMode }" marker-end="url(#arrowhead)" />
                </g>
            </svg>

            <div v-if="loading" class="loading-state">Cargando...</div>
            
            <div v-else class="ciclos-grid">
              <div v-for="(grupo, cicloNum) in ciclosMalla" :key="cicloNum" class="ciclo-column">
                <div class="ciclo-header">Ciclo {{ cicloNum }}</div>
                
                <div class="cursos-list">
                  <div 
                    v-for="curso in grupo.obligatorios" 
                    :key="curso.id"
                    :ref="(el) => { itemRefs[curso.id] = el }" 
                    class="curso-card"
                    :class="[
                        getClasePorTipo(curso.tipo_curso),
                        isLinkingMode ? 'mode-edit' : '',
                        sourceCourse && sourceCourse.id === curso.id ? 'selected-source' : ''
                    ]"
                    @click="handleCardClick(curso)"
                  >
                    <div class="curso-codigo">{{ curso.codigo }}</div>
                    <div class="curso-nombre">{{ curso.nombre }}</div>
                    <div class="curso-creditos">{{ curso.creditos }} CR</div>
                  </div>

                  <div v-if="grupo.electivos.length > 0" class="electivos-container">
                      <div class="electivos-label">Electivos</div>
                      <div 
                        v-for="curso in grupo.electivos" 
                        :key="curso.id"
                        :ref="(el) => { itemRefs[curso.id] = el }"
                        class="curso-card tipo-electivo"
                        :class="[
                            isLinkingMode ? 'mode-edit' : '',
                            sourceCourse && sourceCourse.id === curso.id ? 'selected-source' : ''
                        ]"
                        @click="handleCardClick(curso)"
                      >
                        <div class="curso-codigo">{{ curso.codigo }}</div>
                        <div class="curso-nombre">{{ curso.nombre }}</div>
                        <div class="curso-creditos">{{ curso.creditos }} CR</div>
                      </div>
                  </div>
                </div>
              </div>
            </div>
            </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.malla-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #fffbf0;; z-index: 999; display: flex; justify-content: center; align-items: center; }
.malla-container {background: #ffffff; color: #1e293b; min-width: fit-content;  width: 95%; height: 95%; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; position: relative; }

.malla-header { background: transparent; padding-bottom: 10px; margin-bottom: 20px; border-bottom: 2px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; z-index: 10; }
.actions { display: flex; gap: 15px; align-items: center; }

/* Botón de Modo Juego */
.btn-link-mode { 
    padding: 8px 16px; border-radius: 20px; border: 2px solid #3b82f6; 
    background: white; color: #3b82f6; font-weight: bold; cursor: pointer; transition: 0.2s;
}
.btn-link-mode.active { background: #3b82f6; color: white; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }
.btn-close { font-size: 2rem; background: none; border: none; cursor: pointer; color: #64748b; }

/* Body y SVG */
.malla-body { flex: 1; overflow: auto; padding: 2rem; position: relative;background: #ffffff; }
.arrows-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; min-width: 1600px; /* Asegurar que cubra el scroll */ }

.connector-line {fill: none; stroke: #475569; stroke-width: 1.5px; stroke-linejoin: round; transition: all 0.3s ease; }
.connector-line:hover {stroke: #000;stroke-width: 3px;z-index: 100;}
.connector-line.clickable { pointer-events: stroke; cursor: pointer; }
.connector-line.clickable:hover { stroke: #ef4444; marker-end: url(#arrowhead-hover); stroke-width: 3px; }

/* Grid */
.ciclos-grid { display: grid; grid-template-columns: repeat(10, 160px); gap: 15px; min-width: 1500px; position: relative; z-index: 2; padding-bottom: 30px;}
.ciclo-column { background: transparent !important; border-right: 1px dashed #e2e8f0; border-radius: 0; display: flex; flex-direction: column; height: 100%; }
.ciclo-header { background: transparent; color: #64748b; text-align: center; padding: 8px; 
  font-weight: 900; height: 100%; font-size: 0.9rem;letter-spacing: 1px;border-radius: 8px 8px 0 0; text-transform: uppercase; 
  border-bottom: 2px solid #3b82f6; margin-bottom: 20px; padding-bottom: 5px; border-radius: 0;
}
.cursos-list { padding: 10px; display: flex; flex-direction: column; gap: 10px; }
 
/* Tarjetas */
.curso-card { 
    background: white; 
    border: 1px solid #e2e8f0;
    border-radius: 12px; /* Bordes muy redondeados */
    padding: 10px; 
    margin-bottom: 15px;
    font-size: 0.8rem; 
    cursor: default; 
    position: relative;
    z-index: 10; /* Encima de las líneas */
    transition: transform 0.2s;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);

    /* Flex para centrar contenido */
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 80px;
}
.curso-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.curso-card.tipo-general {
    border-color: #2dd4bf; /* Teal-400 */
    color: #0f766e;
}
.curso-card.tipo-especifico .curso-nombre { color: #881337; }

/* .curso-card.electivo { border-left-color: #f59e0b; background: #fffbeb; } */
.curso-card.tipo-electivo {
    border-color: #f59e0b; /* Amber-500 */
    border-style: dashed; /* Estilo diferente para electivos */
    background: #fffbeb;
}

/* Estilos de Modo Edición */
.curso-card.mode-edit { cursor: pointer; border: 2px dashed #cbd5e1; }
.curso-card.mode-edit:hover { transform: scale(1.05); border-color: #3b82f6; }
.curso-card.selected-source { background: #dcfce7; border-color: #22c55e; box-shadow: 0 0 15px rgba(34, 197, 94, 0.4); transform: scale(1.05); }

.curso-codigo { font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 2px;}
.curso-nombre { font-size: 0.8rem; font-weight: 700; line-height: 1.2; text-align: center;}
.curso-creditos { font-size: 0.65rem; text-align: right; margin-top: 5px; opacity: 0.7;}
.electivos-separator { text-align: center; font-size: 0.7rem; color: #94a3b8; margin: 10px 0; border-top: 1px dashed #cbd5e1; }


.electivos-container {
    margin-top: auto; /* Empuja hacia abajo si el contenedor padre tiene altura */
    padding-top: 20px;
}
.electivos-label {
    text-align: center;
    font-size: 0.7rem;
    color: #cbd5e1;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
    position: relative;
}
.electivos-label::before {
    content: '';
    position: absolute;
    top: 50%; left: 0; right: 0;
    height: 1px;
    background: #e2e8f0;
    z-index: -1;
}

curso-card.mode-edit { cursor: pointer; animation: pulse 2s infinite; }
.curso-card.selected-source { background: #1e293b; border-color: #1e293b; color: white !important; }
.curso-card.selected-source .curso-nombre { color: white !important; }

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
    70% { box-shadow: 0 0 0 6px rgba(59, 130, 246, 0); }
    100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}
</style>