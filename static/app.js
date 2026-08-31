const copy = {
  es: {
    dashboard:"Inicio", records:"Expedientes", results:"Resultados", trends:"Tendencias", library:"Biblioteca PDF", references:"Referencia médica", profiles:"Perfiles", settings:"Configuración",
    appName:"Registros Clínicos", byCodeCafe:"by CodeCafe", tag:"REGISTROS CLÍNICOS · LOCAL", patient:"Paciente", noPatient:"Sin paciente", simple:"Modo simple", advanced:"Modo avanzado", doctor:"Vista médica", newPdf:"Importar PDF", bulkPdf:"Importar carpeta / Bulk",
    subtitle:"Registros clínicos organizados por paciente", welcome:"Tus estudios, organizados y fáciles de consultar.", welcomeSub:"Guarda reportes, revisa resultados y conserva el documento original.",
    reports:"Reportes PDF", observations:"Resultados guardados", flagged:"Fuera de rango", review:"Por revisar", latest:"Estudios recientes", quick:"Acciones rápidas",
    openLibrary:"Abrir biblioteca", viewTrends:"Ver tendencias", viewRecords:"Ver expedientes", addPatient:"Agregar paciente", addResult:"Agregar resultado",
    emptyDocs:"Todavía no hay reportes para este paciente.", emptyObs:"Todavía no hay resultados estructurados para este paciente.", noPatients:"Agrega un perfil para comenzar. Cada persona mantiene sus documentos y resultados separados.",
    date:"Fecha", lab:"Laboratorio", study:"Estudio", specimen:"Muestra", file:"Archivo", status:"Estado", notes:"Notas", open:"Abrir", source:"PDF fuente", statusReview:"Revisar", statusConfirmed:"Confirmado",
    test:"Prueba / analito", value:"Valor", unit:"Unidad", range:"Rango de referencia", low:"Límite bajo", high:"Límite alto", normal:"Dentro del rango", recorded:"Registrado", highFlag:"Alto", lowFlag:"Bajo",
    trendPick:"Selecciona una prueba para ver su evolución.", noTrend:"Se necesitan al menos dos resultados para dibujar una tendencia.", patientHistory:"Historial del paciente",
    libraryTitle:"Biblioteca PDF", libraryHelp:"Explora los reportes originales en una ventana limpia. Los filtros afectan solo al paciente activo.", search:"Buscar", all:"Todos", from:"Desde", to:"Hasta", clear:"Limpiar",
    profileName:"Nombre", birthDate:"Fecha de nacimiento", initials:"Iniciales", save:"Guardar", cancel:"Cancelar", delete:"Eliminar", select:"Seleccionar", edit:"Editar", active:"Activo",
    importTitle:"Importar reporte PDF", manualFirst:"Selecciona un PDF. La aplicación usará texto nativo cuando exista y OCR local cuando sea un escaneo; después detectará columnas, laboratorio y resultados para revisión antes de guardar.", selectPdf:"Seleccionar PDF", pdfOnly:"Selecciona un archivo PDF válido.", duplicate:"Este PDF ya existe en la biblioteca.", analyzing:"Analizando PDF…", extractionReady:"Extracción lista", extractionFailed:"No se pudo completar la extracción automática. Revisa y completa los campos manualmente.", detectedPatient:"Paciente detectado", detectedOrder:"Orden", branch:"Sucursal", provider:"Proveedor", pages:"Páginas", resultsDetected:"resultados detectados", importDetected:"Importar resultados detectados", parserWarnings:"Revisión necesaria", patientMismatch:"El nombre detectado no parece coincidir con el perfil activo. Verifica el paciente antes de guardar.", bulkTitle:"Importación múltiple de PDFs", bulkHelp:"Selecciona una carpeta o varios PDFs. La aplicación analizará todo primero y mostrará una revisión antes de guardar.", selectFolder:"Seleccionar carpeta", selectMultiple:"Seleccionar varios PDFs", includeSubfolders:"Incluir subcarpetas", bulkAnalyzing:"Analizando carpeta…", bulkReady:"Revisión de importación", bulkImportSelected:"Importar seleccionados", bulkNoPdfs:"No se encontraron PDFs en la selección.", bulkDuplicate:"Ya existe", bulkResults:"Resultados", bulkSelected:"seleccionados", bulkImported:"PDFs importados", bulkFolderOnly:"La selección de carpeta está disponible en la aplicación de escritorio.", bulkSelectAtLeastOne:"Selecciona al menos un PDF para importar.", bulkAnalysisFailed:"No se pudo analizar este PDF",
    resultTitle:"Agregar resultado", associatedPdf:"PDF asociado", none:"Ninguno", settingsTitle:"Simple por defecto. Potente cuando lo necesitas.", settingsText:"El modo simple mantiene visibles solo las funciones esenciales. El modo avanzado agrega captura detallada, perfiles y opciones técnicas.",
    language:"Idioma", interfaceMode:"Interfaz", simpleExplanation:"Diseñado para navegación clara, texto legible y pocas decisiones por pantalla.", advancedExplanation:"Muestra captura detallada, perfiles, referencias y opciones técnicas.",
    backup:"Respaldo", exportMeta:"Exportar metadatos", exportFull:"Respaldo completo", backupNote:"El respaldo completo contiene la base de datos y los PDFs. Es información médica privada: guárdalo de forma segura.", cloud:"Nube y sincronización", planned:"Planeado",
    referenceTitle:"Biblioteca de referencia médica", referenceText:"Esta sección enlazará cada prueba normalizada con fuentes médicas autoritativas. No emitirá diagnósticos.", sourceTrace:"Cada resultado conservará vínculo con su PDF fuente, laboratorio, fecha, unidad y rango original.",
    doctorTitle:"Vista médica", doctorSub:"Resumen de solo lectura para mostrar en consulta.", recentResults:"Resultados recientes", abnormal:"Resultados fuera del rango capturado", noAbnormal:"No hay resultados fuera del rango capturado.", close:"Cerrar", print:"Imprimir",
    stored:"Guardado", confirmDelete:"¿Eliminar este registro?", cannotDelete:"No se puede eliminar: todavía tiene registros asociados.", medicalDisclaimer:"Información organizativa y de referencia. No sustituye la interpretación de un profesional de la salud.",
    original:"Documento original preservado", hash:"Huella SHA-256", pdfPages:"Páginas", pdfLoading:"Preparando documento…", pdfPage:"Página", externalPdf:"Abrir PDF externamente", confirm:"Confirmar revisión", deletePdf:"Eliminar PDF", documentHasResults:"No se puede eliminar un PDF que tiene resultados asociados.",
    settingsUpdated:"Configuración actualizada", profileStored:"Perfil guardado", resultStored:"Resultado guardado", pdfStored:"PDF guardado", required:"Completa los campos obligatorios.", noSource:"Sin PDF asociado",
    fullBackup:"Incluye PDFs", advancedOnly:"Disponible en modo avanzado", filterStudy:"Estudio", filterLab:"Laboratorio", manageProfiles:"Administrar perfiles", local:"Datos locales · no requiere internet",
    authoritative:"Fuente médica", normalizedUnit:"Unidad homologada", originalUnit:"Unidad original", mappingReview:"Homologación pendiente", mappingConfirmed:"Homologado", aliases:"Alias", unresolved:"Pendientes", clinicalDictionary:"Diccionario clínico", dictionaryHelp:"Los nombres de distintos laboratorios se vinculan a un analito canónico. Las coincidencias ambiguas nunca se fusionan automáticamente.", mapTo:"Homologar con", apply:"Aplicar", collapseAll:"Colapsar todo", expandLatest:"Abrir más reciente", resultsOnDate:"resultados", normalizedValue:"Valor homologado", sourceInfo:"Información",
    measurements:"Mediciones", dailyReadings:"Mediciones diarias", dailyReadingsSub:"Registra presión arterial, glucosa y peso en una pantalla sencilla. Cada lectura queda separada por paciente y lista para futuras capturas desde el teléfono.", bloodPressure:"Presión arterial", glucoseReading:"Glucosa", weightReading:"Peso", addBloodPressure:"Registrar presión", addGlucose:"Registrar glucosa", addWeight:"Registrar peso", systolic:"Sistólica", diastolic:"Diastólica", pulse:"Pulso", measuredAt:"Fecha y hora", glucoseContext:"Momento", fasting:"Ayuno", beforeMeal:"Antes de comer", afterMeal1:"1 h después de comer", afterMeal2:"2 h después de comer", bedtime:"Antes de dormir", random:"Aleatoria", other:"Otro", device:"Dispositivo", manual:"Manual", sourceType:"Origen", latestMeasurement:"Última medición", noMeasurements:"Todavía no hay mediciones diarias para este paciente.", measurementStored:"Medición guardada", glucoseUnit:"Unidad de glucosa", weightUnit:"Unidad de peso", normalizedKg:"Equivalente kg", scanPlanned:"La captura por cámara del display se conectará a este mismo registro cuando esté disponible la app móvil.", dailyCount:"lecturas", normalizedMgDl:"Equivalente mg/dL", importFailed:"No se pudo guardar el PDF. Revisa la terminal del servidor para el detalle.", textSize:"Tamaño de texto", textNormal:"Normal", textLarge:"Grande", textXLarge:"Muy grande", textSizeHelp:"El modo simple usa texto grande por defecto. Puedes aumentarlo aún más sin cambiar las funciones.", closeApp:"Cerrar aplicación", closeAppConfirm:"¿Cerrar Registros Clínicos?", appClosed:"Registros Clínicos está cerrado. Ya puedes cerrar esta pestaña.", ocrNotice:"Los PDFs escaneados se leen con OCR local. Revisa los valores detectados antes de confirmar el reporte.", about:"Acerca de", developedBy:"Desarrollado por", projectPurpose:"Organizador familiar de análisis clínicos y registros médicos, con énfasis en conservar y localizar rápidamente los documentos originales.", versionLabel:"Versión", systemInfo:"Información del sistema", desktopWindow:"Aplicación de escritorio", browserMode:"Abrir también en navegador", browserModeHelp:"Opción avanzada para diagnóstico o acceso local desde un navegador.", copyrightLabel:"Autoría"
  },
  en: {
    dashboard:"Home", records:"Records", results:"Results", trends:"Trends", library:"PDF Library", references:"Medical reference", profiles:"Profiles", settings:"Settings",
    appName:"Clinical Records", byCodeCafe:"by CodeCafe", tag:"CLINICAL RECORDS · LOCAL", patient:"Patient", noPatient:"No patient", simple:"Simple mode", advanced:"Advanced mode", doctor:"Doctor view", newPdf:"Import PDF",
    subtitle:"Clinical records organized by patient", welcome:"Your lab history, organized and easy to browse.", welcomeSub:"Preserve reports, review results and keep the original document.",
    reports:"PDF reports", observations:"Saved results", flagged:"Out of range", review:"Needs review", latest:"Recent studies", quick:"Quick actions",
    openLibrary:"Open library", viewTrends:"View trends", viewRecords:"View records", addPatient:"Add patient", addResult:"Add result",
    emptyDocs:"There are no reports for this patient yet.", emptyObs:"There are no structured results for this patient yet.", noPatients:"Add a profile to begin. Each person keeps separate documents and results.",
    date:"Date", lab:"Laboratory", study:"Study", specimen:"Specimen", file:"File", status:"Status", notes:"Notes", open:"Open", source:"Source PDF", statusReview:"Review", statusConfirmed:"Confirmed",
    test:"Test / analyte", value:"Value", unit:"Unit", range:"Reference range", low:"Low limit", high:"High limit", normal:"Within range", recorded:"Recorded", highFlag:"High", lowFlag:"Low",
    trendPick:"Select a test to see its evolution.", noTrend:"At least two results are needed to draw a trend.", patientHistory:"Patient history",
    libraryTitle:"PDF Library", libraryHelp:"Browse original reports in a clean window. Filters apply only to the active patient.", search:"Search", all:"All", from:"From", to:"To", clear:"Clear",
    profileName:"Name", birthDate:"Date of birth", initials:"Initials", save:"Save", cancel:"Cancel", delete:"Delete", select:"Select", edit:"Edit", active:"Active",
    importTitle:"Import PDF report", manualFirst:"Select a PDF. The app uses native text when available and local OCR for scans, then detects columns, laboratory metadata and results for review before saving.", selectPdf:"Select PDF", pdfOnly:"Select a valid PDF file.", duplicate:"This PDF already exists in the library.", analyzing:"Analyzing PDF…", extractionReady:"Extraction ready", extractionFailed:"Automatic extraction could not be completed. Review and complete the fields manually.", detectedPatient:"Detected patient", detectedOrder:"Order", branch:"Branch", provider:"Provider", pages:"Pages", resultsDetected:"results detected", importDetected:"Import detected results", parserWarnings:"Needs review", patientMismatch:"The detected name does not appear to match the active profile. Verify the patient before saving.", bulkTitle:"Bulk PDF import", bulkHelp:"Select a folder or multiple PDFs. The app analyzes everything first and shows a review before anything is saved.", selectFolder:"Select folder", selectMultiple:"Select multiple PDFs", includeSubfolders:"Include subfolders", bulkAnalyzing:"Analyzing folder…", bulkReady:"Import review", bulkImportSelected:"Import selected", bulkNoPdfs:"No PDFs were found in the selection.", bulkDuplicate:"Already stored", bulkResults:"Results", bulkSelected:"selected", bulkImported:"PDFs imported", bulkFolderOnly:"Folder selection is available in the desktop application.", bulkSelectAtLeastOne:"Select at least one PDF to import.", bulkAnalysisFailed:"This PDF could not be analyzed",
    resultTitle:"Add result", associatedPdf:"Associated PDF", none:"None", settingsTitle:"Simple by default. Powerful when you need it.", settingsText:"Simple mode keeps only essential functions visible. Advanced mode adds detailed capture, profiles and technical options.",
    language:"Language", interfaceMode:"Interface", simpleExplanation:"Designed for clear navigation, readable text and few decisions per screen.", advancedExplanation:"Shows detailed capture, profiles, references and technical options.",
    backup:"Backup", exportMeta:"Export metadata", exportFull:"Full backup", backupNote:"The full backup contains the database and PDFs. It is private medical information: store it securely.", cloud:"Cloud and synchronization", planned:"Planned",
    referenceTitle:"Medical reference library", referenceText:"This section will connect each normalized test with authoritative medical sources. It will not issue diagnoses.", sourceTrace:"Every result will retain a link to its source PDF, laboratory, date, unit and original reference range.",
    doctorTitle:"Doctor view", doctorSub:"Read-only summary designed to show during an appointment.", recentResults:"Recent results", abnormal:"Results outside the captured range", noAbnormal:"No results are outside the captured reference range.", close:"Close", print:"Print",
    stored:"Saved", confirmDelete:"Delete this record?", cannotDelete:"Cannot delete: it still has associated records.", medicalDisclaimer:"Organizational and reference information. It does not replace interpretation by a healthcare professional.",
    original:"Original document preserved", hash:"SHA-256 fingerprint", pdfPages:"Pages", pdfLoading:"Preparing document…", pdfPage:"Page", externalPdf:"Open PDF externally", confirm:"Confirm review", deletePdf:"Delete PDF", documentHasResults:"A PDF with associated results cannot be deleted.",
    settingsUpdated:"Settings updated", profileStored:"Profile saved", resultStored:"Result saved", pdfStored:"PDF saved", required:"Complete the required fields.", noSource:"No associated PDF",
    fullBackup:"Includes PDFs", advancedOnly:"Available in advanced mode", filterStudy:"Study", filterLab:"Laboratory", manageProfiles:"Manage profiles", local:"Local data · no internet required",
    authoritative:"Medical source", normalizedUnit:"Normalized unit", originalUnit:"Original unit", mappingReview:"Mapping review needed", mappingConfirmed:"Mapped", aliases:"Aliases", unresolved:"Pending", clinicalDictionary:"Clinical dictionary", dictionaryHelp:"Names from different laboratories are linked to a canonical analyte. Ambiguous matches are never silently merged.", mapTo:"Map to", apply:"Apply", collapseAll:"Collapse all", expandLatest:"Open latest", resultsOnDate:"results", normalizedValue:"Normalized value", sourceInfo:"Information",
    measurements:"Measurements", dailyReadings:"Daily readings", dailyReadingsSub:"Record blood pressure, glucose and weight in a simple screen. Every reading stays separated by patient and is ready for future phone display capture.", bloodPressure:"Blood pressure", glucoseReading:"Glucose", weightReading:"Weight", addBloodPressure:"Record pressure", addGlucose:"Record glucose", addWeight:"Record weight", systolic:"Systolic", diastolic:"Diastolic", pulse:"Pulse", measuredAt:"Date and time", glucoseContext:"Timing", fasting:"Fasting", beforeMeal:"Before meal", afterMeal1:"1 h after meal", afterMeal2:"2 h after meal", bedtime:"Bedtime", random:"Random", other:"Other", device:"Device", manual:"Manual", sourceType:"Source", latestMeasurement:"Latest reading", noMeasurements:"There are no daily readings for this patient yet.", measurementStored:"Reading saved", glucoseUnit:"Glucose unit", weightUnit:"Weight unit", normalizedKg:"kg equivalent", scanPlanned:"Camera capture of the meter display will feed this same record when the mobile app is available.", dailyCount:"readings", normalizedMgDl:"mg/dL equivalent", importFailed:"The PDF could not be saved. Check the server terminal for details.", textSize:"Text size", textNormal:"Normal", textLarge:"Large", textXLarge:"Very large", textSizeHelp:"Simple mode uses large text by default. You can enlarge it further without changing features.", closeApp:"Close App", closeAppConfirm:"Close Clinical Records?", appClosed:"Clinical Records is closed. You may close this tab.", ocrNotice:"Scanned PDFs are read with local OCR. Review detected values before confirming the report.", about:"About", developedBy:"Developed by", projectPurpose:"Family clinical-lab and medical-record organizer focused on preserving and quickly finding the original documents.", versionLabel:"Version", systemInfo:"System information", desktopWindow:"Desktop application", browserMode:"Also open in browser", browserModeHelp:"Advanced option for diagnostics or local browser access.", copyrightLabel:"Authorship"
  }
};

let state = window.__INITIAL_STATE__;
let section = "dashboard";
let filters = {q:"", lab:"", study:"", from:"", to:""};
const $ = s => document.querySelector(s);
const t = key => copy[state.language]?.[key] ?? key;
const e = value => String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
const today = () => new Date().toISOString().slice(0,10);
const nowLocalInput = () => { const d=new Date(); d.setMinutes(d.getMinutes()-d.getTimezoneOffset()); return d.toISOString().slice(0,16); };

function activePatient(){ return state.patients.find(p=>p.id===state.activePatientId) || null; }
function docs(){ return state.documents.filter(d=>d.patient_id===state.activePatientId); }
function obs(){ return state.observations.filter(o=>o.patient_id===state.activePatientId); }
function measures(){ return (state.dailyMeasurements||[]).filter(m=>m.patient_id===state.activePatientId); }
function flag(o){
  const numeric=o.value_numeric;
  if(numeric===null || numeric===undefined || numeric==="") return "neutral";
  const value=Number(numeric), ref=String(o.reference_text||"").trim().replace(/,/g,".");
  const cmp=ref.match(/^([<>]=?)\s*=?\s*(-?\d+(?:\.\d+)?)/);
  if(cmp){
    const limit=Number(cmp[2]);
    if(cmp[1]==="<" && value>=limit) return "high";
    if(cmp[1]==="<=" && value>limit) return "high";
    if(cmp[1]===">" && value<=limit) return "low";
    if(cmp[1]===">=" && value<limit) return "low";
    return "normal";
  }
  if(o.reference_high!==null && o.reference_high!==undefined && value>Number(o.reference_high)) return "high";
  if(o.reference_low!==null && o.reference_low!==undefined && value<Number(o.reference_low)) return "low";
  if(o.reference_high===null && o.reference_low===null) return "neutral";
  return "normal";
}
function flagLabel(o){ const f=flag(o); return f==="high"?t("highFlag"):f==="low"?t("lowFlag"):f==="normal"?t("normal"):t("recorded"); }
function isAbnormal(o){ const f=flag(o); return f==="high" || f==="low"; }
function normalizedName(v){ return String(v||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]+/g," ").trim(); }
function patientLooksCompatible(detected, profile){
  if(!detected || !profile?.name) return true;
  const a=new Set(normalizedName(detected).split(/\s+/).filter(x=>x.length>1));
  const b=new Set(normalizedName(profile.name).split(/\s+/).filter(x=>x.length>1));
  const common=[...a].filter(x=>b.has(x));
  return common.length>=Math.min(2, Math.max(1, b.size));
}
function detectedDobMatches(detected, profileDob){
  if(!detected || !profileDob) return true;
  const m=String(detected).match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  return !m || `${m[3]}-${m[2]}-${m[1]}`===profileDob;
}
function initials(p){ return (p?.initials || p?.name?.split(/\s+/).map(x=>x[0]).slice(0,2).join("") || "—").toUpperCase(); }
function fmtDate(v){ if(!v) return "—"; try { return new Intl.DateTimeFormat(state.language==="es"?"es-MX":"en-US",{year:"numeric",month:"short",day:"numeric"}).format(new Date(v+"T12:00:00")); } catch { return v; } }
function toast(msg){ const el=$("#toast"); el.textContent=msg; el.classList.remove("hidden"); clearTimeout(window.__toast); window.__toast=setTimeout(()=>el.classList.add("hidden"),2400); }
async function api(url, options={}){
  const res=await fetch(url, options); let body={}; try{body=await res.json();}catch{}
  if(!res.ok){ const err=new Error(body.error||`HTTP ${res.status}`); err.code=body.error; err.body=body; throw err; }
  return body;
}
function setState(next){ state=next.state || next; render(); }

function renderNav(){
  const items=[
    ["dashboard","⌂","dashboard"],["records","▤","records"],["results","≡","results"],["measurements","♥","measurements"],["trends","↗","trends"],["library","▣","library"]
  ];
  if(state.advancedMode){ items.push(["references","+","references"],["profiles","◎","profiles"]); }
  $("#nav").innerHTML=items.map(([id,icon,label])=>`<button data-section="${id}" class="${section===id?'active':''}"><span>${icon}</span>${e(t(label))}</button>`).join("");
  document.querySelectorAll("[data-section]").forEach(btn=>btn.onclick=()=>{ section=btn.dataset.section; closeNav(); render(); });
}
function renderHeader(){
  document.documentElement.lang=state.language;
  document.documentElement.dataset.textSize=state.textSize||"large";
  const brandName=$("#brandName"); if(brandName) brandName.textContent=t("appName");
  const brandMark=$("#brandMark"); if(brandMark) brandMark.textContent=state.language==="en"?"CR":"RC";
  $("#brandTag").textContent=t("byCodeCafe");
  document.title=`${t("appName")} — ${t("byCodeCafe")}`;
  $("#modeChip").textContent=state.advancedMode?t("advanced"):t("simple");
  const p=activePatient();
  $("#profileBadge").textContent=initials(p);
  $("#profileName").textContent=p?.name || t("noPatient");
  $("#profileSub").textContent=p ? t("local") : t("noPatients");
  $("#patientSelect").innerHTML=state.patients.length ? state.patients.map(x=>`<option value="${x.id}" ${x.id===state.activePatientId?'selected':''}>${e(x.name)}</option>`).join("") : `<option value="">${e(t("noPatient"))}</option>`;
  $("#langBtn").textContent=state.language==="es"?"EN":"ES";
  $("#pageTitle").textContent=t(section);
  $("#pageSubtitle").textContent=t("subtitle");
  $("#importBtn").disabled=!p;
  $("#bulkImportBtn").disabled=!p;
  const versionEl=document.querySelector(".app-version"); if(versionEl) versionEl.textContent=`Python + Flask Desktop · ${state.version||"v0.6"}`;
  document.querySelectorAll("[data-i18n]").forEach(el=>el.textContent=t(el.dataset.i18n));
}
function render(){
  if(!state.advancedMode && ["references","profiles"].includes(section)) section="dashboard";
  renderNav(); renderHeader();
  const renderers={dashboard:renderDashboard,records:renderRecords,results:renderResults,measurements:renderMeasurements,trends:renderTrends,library:renderLibrary,references:renderReferences,profiles:renderProfiles,settings:renderSettings};
  $("#content").innerHTML=renderers[section]();
  wireSection();
}

function emptyStart(){ return `<div class="panel empty-start"><div class="empty-icon">◎</div><h3>${e(t("addPatient"))}</h3><p>${e(t("noPatients"))}</p><button class="primary" id="emptyAddProfile">＋ ${e(t("addPatient"))}</button></div>`; }
function renderDashboard(){
  const p=activePatient(); if(!p) return emptyStart();
  const d=docs(), o=obs(), flagged=o.filter(isAbnormal), review=d.filter(x=>x.status==="review"), recentD=d.slice(0,5), recentO=o.slice(0,5);
  return `<div class="welcome"><div><span>${e(t("patientHistory").toUpperCase())}</span><h2>${e(t("welcome"))}</h2><p>${e(t("welcomeSub"))}</p></div><div class="offline-seal">✓<b>${e(t("local"))}</b><small>SQLite + PDF filesystem</small></div></div>
  <div class="stats">
    ${stat("▣","blue",t("reports"),d.length)}${stat("≡","green",t("observations"),o.length)}${stat("!","amber",t("flagged"),flagged.length)}${stat("?","violet",t("review"),review.length)}
  </div>
  <div class="dash-grid">
    <div class="panel quick"><div class="panel-head"><div><h3>${e(t("quick"))}</h3><p>${e(p.name)}</p></div></div>
      <button data-go="library"><span class="blue">▣</span><div><b>${e(t("openLibrary"))}</b><small>${e(t("libraryHelp"))}</small></div>›</button>
      <button data-go="measurements"><span class="amber">♥</span><div><b>${e(t("dailyReadings"))}</b><small>${e(t("dailyReadingsSub"))}</small></div>›</button>
      <button data-go="trends"><span class="green">↗</span><div><b>${e(t("viewTrends"))}</b><small>${e(t("trendPick"))}</small></div>›</button>
      <button data-go="records"><span class="violet">▤</span><div><b>${e(t("viewRecords"))}</b><small>${e(t("original"))}</small></div>›</button>
      ${state.advancedMode?`<button id="dashAddResult"><span class="amber">＋</span><div><b>${e(t("addResult"))}</b><small>${e(t("advancedOnly"))}</small></div>›</button>`:""}
    </div>
    <div class="panel recent-card"><div class="panel-head"><div><h3>${e(t("recentResults"))}</h3><p>${e(t("patientHistory"))}</p></div></div>
      ${recentO.length?recentO.map(resultLine).join(""):`<div class="empty compact-empty">${e(t("emptyObs"))}</div>`}
    </div>
  </div>
  <div class="panel recent"><div class="panel-head"><div><h3>${e(t("latest"))}</h3><p>${e(t("original"))}</p></div><button class="link" data-go="library">${e(t("openLibrary"))}</button></div>
    ${recentD.length?documentsTable(recentD):`<div class="empty">${e(t("emptyDocs"))}</div>`}
  </div>`;
}
function stat(icon,color,label,n){ return `<div class="stat"><div class="stat-icon ${color}">${icon}</div><div><p>${e(label)}</p><h2>${n}</h2></div></div>`; }
function resultLine(o){ const f=flag(o); return `<div class="result-line"><div><b>${e(o.test_name)}</b><small>${e(fmtDate(o.date))} · ${e(o.lab||"—")}</small></div><span class="result-value ${f}">${e(o.value)} ${e(o.unit||"")} · ${e(flagLabel(o))}</span></div>`; }
function documentsTable(list){ return `<div class="table-wrap"><table class="clickable-table"><thead><tr><th>${e(t("date"))}</th><th>${e(t("study"))}</th><th>${e(t("lab"))}</th><th>${e(t("file"))}</th><th>${e(t("status"))}</th></tr></thead><tbody>${list.map(d=>`<tr data-open-pdf="${d.id}"><td>${e(fmtDate(d.report_date))}</td><td><b>${e(d.study_type||"—")}</b><small>${e(d.specimen||"—")}</small></td><td>${e(d.lab||"—")}</td><td>${e(d.file_name)}</td><td><em class="badge ${d.status}">${e(d.status==="review"?t("statusReview"):t("statusConfirmed"))}</em></td></tr>`).join("")}</tbody></table></div>`; }
function renderRecords(){ const p=activePatient(); if(!p) return emptyStart(); const d=docs(); return `<div class="panel list-page"><div class="panel-head"><div><h3>${e(t("records"))}</h3><p>${e(p.name)} · ${d.length} ${e(t("reports"))}</p></div><div class="panel-head-actions"><button class="subtle-button" id="recordsBulk">▤ ${e(t("bulkPdf"))}</button><button class="primary" id="recordsImport">＋ ${e(t("newPdf"))}</button></div></div>${d.length?documentsTable(d):`<div class="empty">${e(t("emptyDocs"))}</div>`}</div>`; }
function canonicalName(o){
  const value=state.language==="en"?(o.canonical_name_en||o.canonical_name_es):(o.canonical_name_es||o.canonical_name_en);
  return value||o.test_name||o.raw_test_name||"—";
}
function canonicalValue(o){
  const value=o.normalized_value_numeric;
  if(value===null || value===undefined || value==="") return null;
  return Number(value);
}
function referenceLink(o){
  const url=o.reference_url||"https://medlineplus.gov/lab-tests/";
  return `<a class="medical-link" href="${e(url)}" target="_blank" rel="noopener noreferrer" title="${e(t("authoritative"))}">ⓘ ${e(t("sourceInfo"))}</a>`;
}
function resultsByDate(list){
  const groups=new Map();
  list.forEach(o=>{ const date=o.date||""; if(!groups.has(date)) groups.set(date,[]); groups.get(date).push(o); });
  const dates=[...groups.keys()].sort((a,b)=>b.localeCompare(a));
  return `<div class="date-groups">${dates.map((date,index)=>{
    const rows=groups.get(date); const abnormal=rows.filter(isAbnormal).length;
    const labs=[...new Set(rows.map(x=>x.lab).filter(Boolean))];
    const reports=[...new Set(rows.map(x=>x.document_id).filter(Boolean))].length;
    return `<details class="date-group" ${index===0?'open':''}><summary><div class="date-summary-main"><span class="date-chevron">›</span><div><b>${e(fmtDate(date))}</b><small>${rows.length} ${e(t("resultsOnDate"))}${reports?` · ${reports} PDF`:' '}${labs.length?` · ${e(labs.join(" / "))}`:""}</small></div></div><div class="date-summary-stats">${abnormal?`<span class="date-abnormal">! ${abnormal}</span>`:`<span class="date-normal">✓</span>`}</div></summary>${observationsTable(rows,false)}</details>`;
  }).join("")}</div>`;
}
function renderResults(){ const p=activePatient(); if(!p) return emptyStart(); const o=obs(); return `<div class="panel list-page results-page"><div class="panel-head"><div><h3>${e(t("results"))}</h3><p>${e(p.name)} · ${o.length} ${e(t("observations"))}</p></div><div class="results-head-actions">${o.length?`<button class="subtle-button" id="collapseDates">${e(t("collapseAll"))}</button><button class="subtle-button" id="expandLatest">${e(t("expandLatest"))}</button>`:""}${state.advancedMode?`<button class="primary" id="resultsAdd">＋ ${e(t("addResult"))}</button>`:`<span class="mode-chip">${e(t("simple"))}</span>`}</div></div>${o.length?resultsByDate(o):`<div class="empty">${e(t("emptyObs"))}</div>`}</div>`; }
function observationsTable(list,showDate=true){ return `<div class="table-wrap"><table class="results-table"><thead><tr>${showDate?`<th>${e(t("date"))}</th>`:""}<th>${e(t("test"))}</th><th>${e(t("value"))}</th><th>${e(t("range"))}</th><th>${e(t("lab"))}</th><th>${e(t("authoritative"))}</th>${state.advancedMode?'<th></th>':''}</tr></thead><tbody>${list.map(o=>{ const f=flag(o); const fallback=(o.reference_low??"")+(o.reference_low!==null||o.reference_high!==null?" – ":"")+(o.reference_high??""); const range=o.reference_text||fallback||"—"; const detail=[o.panel,o.method,o.source_page?`p. ${o.source_page}`:""].filter(Boolean).join(" · "); const cname=canonicalName(o); const raw=o.raw_test_name&&o.raw_test_name!==cname?o.raw_test_name:""; const normalized=canonicalValue(o); const originalNum=o.value_numeric===null||o.value_numeric===undefined?null:Number(o.value_numeric); const changed=normalized!==null && (o.normalization_status==="converted" || (o.canonical_unit&&o.unit&&o.canonical_unit!==o.unit)); return `<tr>${showDate?`<td>${e(fmtDate(o.date))}</td>`:""}<td><b>${e(cname)}</b>${raw?`<small>${e(raw)}</small>`:""}<small>${e(detail||o.notes||"")}</small>${o.mapping_status==="review"?`<em class="mapping-badge review">${e(t("mappingReview"))}</em>`:""}</td><td><span class="status-text ${f}">${e(o.value)} ${e(o.unit||"")} · ${e(flagLabel(o))}</span>${changed?`<small class="normalized-line">${e(t("normalizedValue"))}: ${e(normalized.toFixed(Math.abs(normalized)>=100?1:Math.abs(normalized)>=10?2:3).replace(/\.0+$/,""))} ${e(o.canonical_unit||"")}</small>`:""}${state.advancedMode&&o.unit_ucum?`<small>UCUM: ${e(o.unit_ucum)}</small>`:""}</td><td>${e(range)}</td><td>${e(o.lab||"—")}</td><td>${referenceLink(o)}</td>${state.advancedMode?`<td><button class="delete-result" data-delete-result="${o.id}">×</button></td>`:""}</tr>`; }).join("")}</tbody></table></div>`; }
function measurementContextLabel(value){
  const labels={fasting:"fasting",before_meal:"beforeMeal",after_meal_1h:"afterMeal1",after_meal_2h:"afterMeal2",bedtime:"bedtime",random:"random",other:"other"};
  return labels[value]?t(labels[value]):(value||"—");
}
function fmtDateTime(v){
  if(!v) return "—";
  try{ return new Intl.DateTimeFormat(state.language==="es"?"es-MX":"en-US",{year:"numeric",month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"}).format(new Date(v)); }catch{return v;}
}
function measurementInfoLink(kind){
  const urls={
    blood_pressure:"https://medlineplus.gov/ency/article/007490.htm",
    glucose:"https://medlineplus.gov/bloodglucose.html",
    weight:"https://medlineplus.gov/weightcontrol.html"
  };
  const url=urls[kind]||"https://medlineplus.gov/";
  return `<a class="medical-link" href="${url}" target="_blank" rel="noopener noreferrer">ⓘ ${e(t("sourceInfo"))}</a>`;
}
function measurementSummary(m){
  if(!m) return "—";
  if(m.kind==="blood_pressure") return `${Number(m.systolic).toFixed(0)}/${Number(m.diastolic).toFixed(0)} mmHg${m.pulse?` · ${Number(m.pulse).toFixed(0)} bpm`:""}`;
  if(m.kind==="glucose") return `${Number(m.glucose_value).toFixed(m.glucose_unit==="mmol/L"?1:0)} ${m.glucose_unit||"mg/dL"}`;
  return `${Number(m.weight_value).toFixed(1)} ${m.weight_unit||"kg"}`;
}
function measurementRows(list){
  return `<div class="table-wrap"><table class="measurement-table"><thead><tr><th>${e(t("measuredAt"))}</th><th>${e(t("value"))}</th><th>${e(t("glucoseContext"))}</th><th>${e(t("device"))}</th><th>${e(t("notes"))}</th><th>${e(t("authoritative"))}</th>${state.advancedMode?"<th></th>":""}</tr></thead><tbody>${list.map(m=>{
    const value=m.kind==="blood_pressure"
      ?`<b>${e(Number(m.systolic).toFixed(0))}/${e(Number(m.diastolic).toFixed(0))} mmHg</b>${m.pulse?`<small>${e(t("pulse"))}: ${e(Number(m.pulse).toFixed(0))} bpm</small>`:""}`
      :m.kind==="glucose"
        ?`<b>${e(Number(m.glucose_value).toFixed(m.glucose_unit==="mmol/L"?1:0))} ${e(m.glucose_unit||"mg/dL")}</b>${m.glucose_unit==="mmol/L"&&m.glucose_mg_dl?`<small>${e(t("normalizedMgDl"))}: ${e(Number(m.glucose_mg_dl).toFixed(0))} mg/dL</small>`:""}`
        :`<b>${e(Number(m.weight_value).toFixed(1))} ${e(m.weight_unit||"kg")}</b>${m.weight_unit==="lb"&&m.weight_kg?`<small>${e(t("normalizedKg"))}: ${e(Number(m.weight_kg).toFixed(1))} kg</small>`:""}`;
    return `<tr><td>${e(fmtDateTime(m.measured_at))}<small>${e(m.source_type||t("manual"))}</small></td><td>${value}</td><td>${e(m.kind==="glucose"?measurementContextLabel(m.context):"—")}</td><td>${e(m.device_label||"—")}</td><td>${e(m.notes||"—")}</td><td>${measurementInfoLink(m.kind)}</td>${state.advancedMode?`<td><button class="delete-result" data-delete-measurement="${m.id}">×</button></td>`:""}</tr>`;
  }).join("")}</tbody></table></div>`;
}
function measurementGroups(list){
  const groups=new Map(); list.forEach(m=>{const day=String(m.measured_at||"").slice(0,10);if(!groups.has(day))groups.set(day,[]);groups.get(day).push(m);});
  return `<div class="date-groups">${[...groups.keys()].sort((a,b)=>b.localeCompare(a)).map((day,i)=>`<details class="date-group measurement-group" ${i===0?"open":""}><summary><div class="date-summary-main"><span class="date-chevron">›</span><div><b>${e(fmtDate(day))}</b><small>${groups.get(day).length} ${e(t("dailyCount"))}</small></div></div></summary>${measurementRows(groups.get(day))}</details>`).join("")}</div>`;
}
function bpTrendSvg(list){
  const rows=[...list].sort((a,b)=>a.measured_at.localeCompare(b.measured_at)).slice(-20); if(rows.length<2)return `<div class="empty compact-empty">${e(t("noTrend"))}</div>`;
  const W=720,H=220,L=52,R=24,T=24,B=45, values=rows.flatMap(x=>[Number(x.systolic),Number(x.diastolic)]); let min=Math.min(...values),max=Math.max(...values); const span=Math.max(10,max-min); min-=span*.15;max+=span*.15; const x=i=>L+(i/(rows.length-1))*(W-L-R), y=v=>T+(max-v)/(max-min)*(H-T-B);
  const sys=rows.map((m,i)=>`${x(i)},${y(Number(m.systolic))}`).join(" "), dia=rows.map((m,i)=>`${x(i)},${y(Number(m.diastolic))}`).join(" ");
  const dates=rows.map((m,i)=>i===0||i===rows.length-1?`<text class="chart-label" text-anchor="middle" x="${x(i)}" y="${H-14}">${e(String(m.measured_at).slice(5,10))}</text>`:"").join("");
  return `<div class="chart-shell mini-chart"><svg viewBox="0 0 ${W} ${H}"><polyline class="bp-systolic" fill="none" points="${sys}"/><polyline class="bp-diastolic" fill="none" points="${dia}"/>${rows.map((m,i)=>`<circle class="bp-systolic-dot" cx="${x(i)}" cy="${y(Number(m.systolic))}" r="4"/><circle class="bp-diastolic-dot" cx="${x(i)}" cy="${y(Number(m.diastolic))}" r="4"/>`).join("")}${dates}</svg></div>`;
}
function glucoseTrendSvg(list){
  const rows=[...list].sort((a,b)=>a.measured_at.localeCompare(b.measured_at)).slice(-20); if(rows.length<2)return `<div class="empty compact-empty">${e(t("noTrend"))}</div>`;
  const W=720,H=220,L=52,R=24,T=24,B=45, vals=rows.map(x=>Number(x.glucose_mg_dl||x.glucose_value)); let min=Math.min(...vals),max=Math.max(...vals); const span=Math.max(10,max-min); min-=span*.15;max+=span*.15; const x=i=>L+(i/(rows.length-1))*(W-L-R), y=v=>T+(max-v)/(max-min)*(H-T-B); const points=rows.map((m,i)=>`${x(i)},${y(Number(m.glucose_mg_dl||m.glucose_value))}`).join(" ");
  return `<div class="chart-shell mini-chart"><svg viewBox="0 0 ${W} ${H}"><polyline class="glucose-line" fill="none" points="${points}"/>${rows.map((m,i)=>`<circle class="glucose-dot" cx="${x(i)}" cy="${y(Number(m.glucose_mg_dl||m.glucose_value))}" r="4"/>`).join("")}<text class="chart-label" x="8" y="18">mg/dL</text></svg></div>`;
}
function weightTrendSvg(list){
  const rows=[...list].sort((a,b)=>a.measured_at.localeCompare(b.measured_at)).slice(-20); if(rows.length<2)return `<div class="empty compact-empty">${e(t("noTrend"))}</div>`;
  const W=720,H=220,L=52,R=24,T=24,B=45, vals=rows.map(x=>Number(x.weight_kg||x.weight_value)); let min=Math.min(...vals),max=Math.max(...vals); const span=Math.max(1,max-min); min-=span*.15;max+=span*.15; const x=i=>L+(i/(rows.length-1))*(W-L-R), y=v=>T+(max-v)/(max-min)*(H-T-B); const points=rows.map((m,i)=>`${x(i)},${y(Number(m.weight_kg||m.weight_value))}`).join(" ");
  return `<div class="chart-shell mini-chart"><svg viewBox="0 0 ${W} ${H}"><polyline class="weight-line" fill="none" points="${points}"/>${rows.map((m,i)=>`<circle class="weight-dot" cx="${x(i)}" cy="${y(Number(m.weight_kg||m.weight_value))}" r="4"/>`).join("")}<text class="chart-label" x="8" y="18">kg</text></svg></div>`;
}
function renderMeasurements(){
  const p=activePatient(); if(!p)return emptyStart(); const all=measures(), bp=all.filter(m=>m.kind==="blood_pressure"), gl=all.filter(m=>m.kind==="glucose"), wt=all.filter(m=>m.kind==="weight");
  const latestBp=bp[0], latestGl=gl[0], latestWt=wt[0];
  return `<div class="measurement-hero"><div><small>${e(p.name.toUpperCase())}</small><h2>${e(t("dailyReadings"))}</h2><p>${e(t("dailyReadingsSub"))}</p></div><div class="hero-actions"><button class="primary" id="addBp">＋ ${e(t("addBloodPressure"))}</button><button class="primary" id="addGlucose">＋ ${e(t("addGlucose"))}</button><button class="primary" id="addWeight">＋ ${e(t("addWeight"))}</button></div></div>
  <div class="measurement-latest"><div class="panel reading-card"><span>${e(t("bloodPressure"))}</span><h2>${e(measurementSummary(latestBp))}</h2><small>${e(latestBp?fmtDateTime(latestBp.measured_at):t("noMeasurements"))}</small>${measurementInfoLink("blood_pressure")}</div><div class="panel reading-card"><span>${e(t("glucoseReading"))}</span><h2>${e(measurementSummary(latestGl))}</h2><small>${e(latestGl?fmtDateTime(latestGl.measured_at):t("noMeasurements"))}</small>${measurementInfoLink("glucose")}</div><div class="panel reading-card"><span>${e(t("weightReading"))}</span><h2>${e(measurementSummary(latestWt))}</h2><small>${e(latestWt?fmtDateTime(latestWt.measured_at):t("noMeasurements"))}</small>${measurementInfoLink("weight")}</div></div>
  <div class="measurement-charts"><div class="panel"><div class="panel-head"><div><h3>${e(t("bloodPressure"))}</h3><p>${bp.length} ${e(t("dailyCount"))}</p></div></div>${bpTrendSvg(bp)}</div><div class="panel"><div class="panel-head"><div><h3>${e(t("glucoseReading"))}</h3><p>${gl.length} ${e(t("dailyCount"))}</p></div></div>${glucoseTrendSvg(gl)}</div><div class="panel weight-chart-panel"><div class="panel-head"><div><h3>${e(t("weightReading"))}</h3><p>${wt.length} ${e(t("dailyCount"))}</p></div></div>${weightTrendSvg(wt)}</div></div>
  <div class="panel list-page measurement-history"><div class="panel-head"><div><h3>${e(t("dailyReadings"))}</h3><p>${all.length} ${e(t("dailyCount"))}</p></div></div>${all.length?measurementGroups(all):`<div class="empty">${e(t("noMeasurements"))}</div>`}</div>
  ${state.advancedMode?`<div class="warning-note scan-note">${e(t("scanPlanned"))}</div>`:""}`;
}
function renderTrends(){
  const p=activePatient(); if(!p) return emptyStart();
  const numericObs=obs().filter(x=>canonicalValue(x)!==null);
  const keys=[...new Set(numericObs.map(x=>x.canonical_key||x.test_name))].sort((a,b)=>{
    const oa=numericObs.find(x=>(x.canonical_key||x.test_name)===a), ob=numericObs.find(x=>(x.canonical_key||x.test_name)===b);
    return canonicalName(oa).localeCompare(canonicalName(ob));
  });
  const selected=window.__trend && keys.includes(window.__trend)?window.__trend:(keys[0]||""); window.__trend=selected;
  const list=numericObs.filter(x=>(x.canonical_key||x.test_name)===selected).sort((a,b)=>a.date.localeCompare(b.date));
  const selectedObs=list[0];
  return `<div class="trend-hero"><div><small>${e(t("patientHistory").toUpperCase())}</small><h2>${e(t("trends"))}</h2><p>${e(t("trendPick"))}</p></div><select id="trendSelect"><option value="">${e(t("test"))}</option>${keys.map(k=>{const o=numericObs.find(x=>(x.canonical_key||x.test_name)===k);return `<option value="${e(k)}" ${k===selected?'selected':''}>${e(canonicalName(o))}</option>`}).join("")}</select></div>
  ${selectedObs?`<div class="trend-meta"><b>${e(canonicalName(selectedObs))}</b><span>${e(t("normalizedUnit"))}: ${e(selectedObs.canonical_unit||selectedObs.unit||"—")}</span>${referenceLink(selectedObs)}</div>`:""}
  <div class="panel trend-panel">${selected?(list.length>=2?trendSvg(list):`<div class="empty trend-empty">${e(t("noTrend"))}</div>`):`<div class="empty trend-empty">${e(t("trendPick"))}</div>`}</div>
  ${selected&&list.length?`<div class="panel trend-table">${observationsTable([...list].reverse())}</div>`:""}`;
}
function trendSvg(list){
  const W=900,H=330,padL=70,padR=35,padT=35,padB=65; const vals=list.map(x=>canonicalValue(x)).filter(x=>x!==null); let min=Math.min(...vals),max=Math.max(...vals); if(min===max){min-=1;max+=1;} const span=max-min; min-=span*.12; max+=span*.12;
  const x=i=>padL+(i/(list.length-1))*(W-padL-padR); const y=v=>padT+(max-v)/(max-min)*(H-padT-padB);
  const points=list.map((o,i)=>`${x(i)},${y(canonicalValue(o))}`).join(" ");
  const grid=[0,.25,.5,.75,1].map(r=>{ const yy=padT+r*(H-padT-padB); const val=max-r*(max-min); return `<line class="axis-line" x1="${padL}" y1="${yy}" x2="${W-padR}" y2="${yy}"/><text class="chart-label" x="10" y="${yy+4}">${e(val.toFixed(2))}</text>`; }).join("");
  const unit=list[0]?.canonical_unit||list[0]?.unit||"";
  const dots=list.map((o,i)=>`<circle class="trend-dot ${flag(o)}" cx="${x(i)}" cy="${y(canonicalValue(o))}" r="7"/><text class="chart-value" text-anchor="middle" x="${x(i)}" y="${y(canonicalValue(o))-14}">${e(canonicalValue(o).toFixed(2))} ${e(unit)}</text><text class="chart-label" text-anchor="middle" x="${x(i)}" y="${H-25}">${e(o.date)}</text>`).join("");
  return `<div class="chart-shell"><svg viewBox="0 0 ${W} ${H}" role="img">${grid}<polyline fill="none" class="trend-line" points="${points}"/>${dots}</svg></div>`;
}
function renderLibrary(){ const p=activePatient(); if(!p) return emptyStart(); let list=docs(); if(filters.q){ const q=filters.q.toLowerCase(); list=list.filter(d=>[d.file_name,d.lab,d.study_type,d.specimen,d.notes].some(v=>String(v||"").toLowerCase().includes(q))); } if(filters.lab) list=list.filter(d=>d.lab===filters.lab); if(filters.study) list=list.filter(d=>d.study_type===filters.study); if(filters.from) list=list.filter(d=>!d.report_date||d.report_date>=filters.from); if(filters.to) list=list.filter(d=>!d.report_date||d.report_date<=filters.to);
  const labs=[...new Set(docs().map(d=>d.lab).filter(Boolean))].sort(); const studies=[...new Set(docs().map(d=>d.study_type).filter(Boolean))].sort();
  return `<div class="library-hero"><div><small>${e(p.name.toUpperCase())}</small><h2>${e(t("libraryTitle"))}</h2><p>${e(t("libraryHelp"))}</p></div><div class="hero-actions"><button class="subtle-button hero-secondary" id="libraryBulk">▤ ${e(t("bulkPdf"))}</button><button class="primary" id="libraryImport">＋ ${e(t("newPdf"))}</button></div></div>
    <div class="panel filters"><div class="search wide-search">⌕<input id="filterQ" placeholder="${e(t("search"))}" value="${e(filters.q)}"></div>
    <label><span>${e(t("filterLab"))}</span><select id="filterLab"><option value="">${e(t("all"))}</option>${labs.map(v=>`<option ${v===filters.lab?'selected':''}>${e(v)}</option>`).join("")}</select></label>
    <label><span>${e(t("filterStudy"))}</span><select id="filterStudy"><option value="">${e(t("all"))}</option>${studies.map(v=>`<option ${v===filters.study?'selected':''}>${e(v)}</option>`).join("")}</select></label>
    <label><span>${e(t("from"))}</span><input id="filterFrom" type="date" value="${e(filters.from)}"></label><label><span>${e(t("to"))}</span><input id="filterTo" type="date" value="${e(filters.to)}"></label><button id="clearFilters">${e(t("clear"))}</button></div>
    <div class="pdf-grid">${list.length?list.map(pdfCard).join(""):`<div class="panel empty library-empty">${e(t("emptyDocs"))}</div>`}</div>`;
}
function pdfCard(d){ return `<button class="pdf-card" data-open-pdf="${d.id}"><span class="pdf-icon">PDF</span><span class="pdf-info"><b>${e(d.study_type||d.file_name)}</b><span>${e(fmtDate(d.report_date))} · ${e(d.lab||"—")}</span><small>${e(d.file_name)}</small></span><span class="pdf-arrow">›</span></button>`; }
function renderReferences(){
  const tests=state.clinicalTests||[], unresolved=state.unresolvedAliases||[];
  const pending=unresolved.length?`<div class="panel dictionary-pending"><div class="panel-head"><div><h3>${e(t("unresolved"))}</h3><p>${e(t("dictionaryHelp"))}</p></div><span class="mode-chip">${unresolved.length}</span></div>${unresolved.map(a=>`<div class="alias-map-row"><div><b>${e(a.alias_raw)}</b><small>${e(a.lab_scope||"Todos")} · ${e(a.specimen_scope||"—")} · ${e(a.unit_scope||"—")}</small></div><select data-alias-target="${a.id}"><option value="">${e(t("mapTo"))}…</option>${tests.filter(x=>x.status==="seed").map(x=>`<option value="${x.id}">${e(state.language==="en"?x.name_en:x.name_es)} · ${e(x.canonical_unit||"—")}</option>`).join("")}</select><button class="subtle-button" data-map-alias="${a.id}">${e(t("apply"))}</button></div>`).join("")}</div>`:"";
  return `<div class="reference-hero"><div><small>LOINC-ready · UCUM · NLM</small><h2>${e(t("clinicalDictionary"))}</h2><p>${e(t("dictionaryHelp"))}</p></div><div class="reference-lock">${tests.length}</div></div>${pending}<div class="panel dictionary-list"><div class="table-wrap"><table><thead><tr><th>${e(t("test"))}</th><th>${e(t("specimen"))}</th><th>${e(t("normalizedUnit"))}</th><th>${e(t("aliases"))}</th><th>${e(t("authoritative"))}</th></tr></thead><tbody>${tests.map(x=>`<tr><td><b>${e(state.language==="en"?x.name_en:x.name_es)}</b><small>${e(x.canonical_key)}</small>${x.status==="provisional"?`<em class="mapping-badge review">${e(t("mappingReview"))}</em>`:""}</td><td>${e(x.specimen||"—")}</td><td>${e(x.canonical_unit||"—")}${x.ucum_code?`<small>UCUM: ${e(x.ucum_code)}</small>`:""}${x.loinc_code?`<small>LOINC: ${e(x.loinc_code)}</small>`:""}</td><td>${e(x.alias_count||0)}</td><td><a class="medical-link" href="${e(x.reference_url||"https://medlineplus.gov/lab-tests/")}" target="_blank" rel="noopener noreferrer">ⓘ ${e(x.reference_label||t("sourceInfo"))}</a></td></tr>`).join("")}</tbody></table></div></div>`;
}
function renderProfiles(){ return `<div class="panel list-page"><div class="panel-head"><div><h3>${e(t("manageProfiles"))}</h3><p>${e(t("noPatients"))}</p></div><button class="primary" id="profilesAdd">＋ ${e(t("addPatient"))}</button></div><div class="profile-grid">${state.patients.map(patientCard).join("")}</div></div>`; }
function patientCard(p){ const active=p.id===state.activePatientId; return `<div class="patient-card ${active?'active-patient':''}"><span>${e(initials(p))}</span><div><h3>${e(p.name)}</h3><p>${e(p.dob?fmtDate(p.dob):"—")}</p><small>${e(p.notes||"")}</small></div><div class="patient-actions">${active?`<button disabled>${e(t("active"))}</button>`:`<button data-select-profile="${p.id}">${e(t("select"))}</button>`}<button data-edit-profile="${p.id}">${e(t("edit"))}</button><button class="danger-link" data-delete-profile="${p.id}">${e(t("delete"))}</button></div></div>`; }
function renderSettings(){ const about=state.about||{}; return `<div class="settings-hero"><div><small>${e(t("appName").toUpperCase())} · ${e(t("byCodeCafe"))}</small><h2>${e(t("settingsTitle"))}</h2><p>${e(t("settingsText"))}</p></div></div><div class="settings-grid">
  <div class="panel setting-card"><h3>${e(t("language"))}</h3><p>Español / English</p><div class="segmented"><button id="setEs" class="${state.language==='es'?'selected':''}">Español</button><button id="setEn" class="${state.language==='en'?'selected':''}">English</button></div></div>
  <div class="panel setting-card"><h3>${e(t("interfaceMode"))}</h3><p>${e(t("settingsText"))}</p><div class="mode-options"><button id="setSimple" class="mode-option ${!state.advancedMode?'selected':''}"><b>${e(t("simple"))}</b><small>${e(t("simpleExplanation"))}</small></button><button id="setAdvanced" class="mode-option ${state.advancedMode?'selected':''}"><b>${e(t("advanced"))}</b><small>${e(t("advancedExplanation"))}</small></button></div></div>
  <div class="panel setting-card"><h3>${e(t("textSize"))}</h3><p>${e(t("textSizeHelp"))}</p><div class="segmented text-size-options"><button id="textNormal" class="${state.textSize==='normal'?'selected':''}">${e(t("textNormal"))}</button><button id="textLarge" class="${(state.textSize||'large')==='large'?'selected':''}">${e(t("textLarge"))}</button><button id="textXLarge" class="${state.textSize==='xlarge'?'selected':''}">${e(t("textXLarge"))}</button></div></div>
  <div class="panel setting-card"><h3>${e(t("backup"))}</h3><p>${e(t("backupNote"))}</p><div class="backup-buttons"><a class="subtle-button" href="/api/backup/metadata">${e(t("exportMeta"))}</a><a class="subtle-button" href="/api/backup/full">${e(t("exportFull"))}</a></div></div>
  <div class="panel setting-card"><h3>${e(t("cloud"))}</h3><p>${e(t("sourceTrace"))}</p><div class="planned-row"><span>Encrypted cloud backup</span><em>${e(t("planned"))}</em></div><div class="planned-row"><span>Multi-device sync API</span><em>${e(t("planned"))}</em></div><div class="planned-row"><span>iOS / Android client</span><em>${e(t("planned"))}</em></div>${state.desktopMode&&state.advancedMode?`<div class="desktop-browser-option"><p>${e(t("browserModeHelp"))}</p><button class="subtle-button" id="openBrowserMode">↗ ${e(t("browserMode"))}</button></div>`:""}</div>
  <div class="panel setting-card about-card"><div class="about-heading"><div class="brand-mark">${state.language==="en"?"CR":"RC"}</div><div><h3>${e(t("about"))}</h3><b>${e((state.language==="en"?(about.product_en||"Clinical Records"):(about.product||"Registros Clínicos")))}</b></div></div><p>${e(t("projectPurpose"))}</p><dl class="about-list"><div><dt>${e(t("developedBy"))}</dt><dd>${e(about.author||"Jaime Sánchez Sáenz")}</dd></div><div><dt>CodeCafe</dt><dd>${e(about.brand||"CodeCafe.io")}</dd></div><div><dt>Contacto / Contact</dt><dd>${e(about.contact||"contacto@codecafe.io")}</dd></div><div><dt>${e(t("versionLabel"))}</dt><dd>${e(state.version||"0.6.5")}</dd></div><div><dt>${e(t("copyrightLabel"))}</dt><dd>${e(about.copyright||"© 2026 Jaime Sánchez Sáenz")}</dd></div></dl></div>
  </div>`; }

function wireSection(){
  document.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>{section=b.dataset.go;render();});
  document.querySelectorAll("[data-open-pdf]").forEach(b=>b.onclick=()=>openPdf(Number(b.dataset.openPdf)));
  $("#emptyAddProfile") && ($("#emptyAddProfile").onclick=()=>openProfileModal());
  ["#recordsImport","#libraryImport"].forEach(s=>$(s)&&($(s).onclick=openImportModal));
  ["#recordsBulk","#libraryBulk"].forEach(s=>$(s)&&($(s).onclick=openBulkImportModal));
  ["#resultsAdd","#dashAddResult"].forEach(s=>$(s)&&($(s).onclick=openResultModal));
  $("#addBp") && ($("#addBp").onclick=()=>openMeasurementModal("blood_pressure"));
  $("#addGlucose") && ($("#addGlucose").onclick=()=>openMeasurementModal("glucose"));
  $("#addWeight") && ($("#addWeight").onclick=()=>openMeasurementModal("weight"));
  if($("#collapseDates")) $("#collapseDates").onclick=()=>document.querySelectorAll(".date-group").forEach(x=>x.open=false);
  if($("#expandLatest")) $("#expandLatest").onclick=()=>{ const groups=[...document.querySelectorAll(".date-group")]; groups.forEach((x,i)=>x.open=i===0); groups[0]?.scrollIntoView({behavior:"smooth",block:"start"}); };
  $("#profilesAdd") && ($("#profilesAdd").onclick=()=>openProfileModal());
  document.querySelectorAll("[data-select-profile]").forEach(b=>b.onclick=()=>selectPatient(Number(b.dataset.selectProfile)));
  document.querySelectorAll("[data-edit-profile]").forEach(b=>b.onclick=()=>openProfileModal(state.patients.find(p=>p.id===Number(b.dataset.editProfile))));
  document.querySelectorAll("[data-delete-profile]").forEach(b=>b.onclick=()=>deleteProfile(Number(b.dataset.deleteProfile)));
  document.querySelectorAll("[data-delete-result]").forEach(b=>b.onclick=()=>deleteResult(Number(b.dataset.deleteResult)));
  document.querySelectorAll("[data-delete-measurement]").forEach(b=>b.onclick=()=>deleteMeasurement(Number(b.dataset.deleteMeasurement)));
  document.querySelectorAll("[data-map-alias]").forEach(b=>b.onclick=async()=>{
    const aliasId=Number(b.dataset.mapAlias); const sel=document.querySelector(`[data-alias-target="${aliasId}"]`);
    if(!sel?.value) return;
    try{ setState(await api(`/api/dictionary/aliases/${aliasId}/map`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({clinicalTestId:Number(sel.value)})})); toast(t("mappingConfirmed")); }
    catch(err){ alert(err.message); }
  });
  if($("#trendSelect")) $("#trendSelect").onchange=ev=>{window.__trend=ev.target.value;render();};
  const fq=$("#filterQ"); if(fq) fq.oninput=ev=>{filters.q=ev.target.value;renderLibraryOnly();};
  [["#filterLab","lab"],["#filterStudy","study"],["#filterFrom","from"],["#filterTo","to"]].forEach(([sel,key])=>{if($(sel)) $(sel).onchange=ev=>{filters[key]=ev.target.value;render();};});
  if($("#clearFilters")) $("#clearFilters").onclick=()=>{filters={q:"",lab:"",study:"",from:"",to:""};render();};
  if($("#setEs")) $("#setEs").onclick=()=>saveSettings({language:"es"});
  if($("#setEn")) $("#setEn").onclick=()=>saveSettings({language:"en"});
  if($("#setSimple")) $("#setSimple").onclick=()=>saveSettings({advancedMode:false});
  if($("#setAdvanced")) $("#setAdvanced").onclick=()=>saveSettings({advancedMode:true});
  if($("#textNormal")) $("#textNormal").onclick=()=>saveSettings({textSize:"normal"});
  if($("#textLarge")) $("#textLarge").onclick=()=>saveSettings({textSize:"large"});
  if($("#textXLarge")) $("#textXLarge").onclick=()=>saveSettings({textSize:"xlarge"});
  if($("#openBrowserMode")) $("#openBrowserMode").onclick=openInBrowser;
}
function renderLibraryOnly(){ clearTimeout(window.__filterTimer); window.__filterTimer=setTimeout(render,100); }

function modal(html){ $("#modalRoot").innerHTML=`<div class="modal-backdrop" id="modalBackdrop">${html}</div>`; $("#modalBackdrop").onclick=ev=>{if(ev.target.id==="modalBackdrop") closeModal();}; document.querySelectorAll("[data-close-modal]").forEach(b=>b.onclick=closeModal); }
function closeModal(){ $("#modalRoot").innerHTML=""; }
function openProfileModal(p=null){
  modal(`<div class="modal profile-modal"><div class="modal-head"><div><small>${e(t("profiles").toUpperCase())}</small><h2>${e(p?t("edit"):t("addPatient"))}</h2></div><button data-close-modal>×</button></div><form id="profileForm"><div class="form-grid">
  <label class="field wide"><span>${e(t("profileName"))} *</span><input name="name" required value="${e(p?.name||"")}"></label><label class="field"><span>${e(t("initials"))}</span><input name="initials" maxlength="8" value="${e(p?.initials||"")}"></label><label class="field"><span>${e(t("birthDate"))}</span><input name="dob" type="date" value="${e(p?.dob||"")}"></label><label class="field wide"><span>${e(t("notes"))}</span><textarea name="notes" rows="4">${e(p?.notes||"")}</textarea></label></div><div class="modal-actions"><button type="button" data-close-modal>${e(t("cancel"))}</button><button class="primary" type="submit">${e(t("save"))}</button></div></form></div>`);
  $("#profileForm").onsubmit=async ev=>{ev.preventDefault(); const data=Object.fromEntries(new FormData(ev.target)); try{const next=await api(p?`/api/profiles/${p.id}`:"/api/profiles",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});setState(next);closeModal();toast(t("profileStored"));}catch(err){alert(err.message);}};
}
function openImportModal(){
  const p=activePatient(); if(!p) return openProfileModal();
  modal(`<div class="modal import-modal"><div class="modal-head"><div><small>PDF</small><h2>${e(t("importTitle"))}</h2></div><button data-close-modal>×</button></div><div class="info-banner">${e(t("manualFirst"))}</div><form id="importForm" enctype="multipart/form-data"><div class="form-grid">
    <label class="field wide"><span>${e(t("selectPdf"))} *</span><input id="pdfInput" type="file" name="file" accept="application/pdf,.pdf" required></label>
    <label class="field"><span>${e(t("date"))}</span><input id="importDate" type="date" name="report_date"></label>
    <label class="field"><span>${e(t("lab"))}</span><input id="importLab" name="lab"></label>
    <label class="field wide"><span>${e(t("study"))}</span><input id="importStudy" name="study_type"></label>
    <label class="field wide"><span>${e(t("specimen"))}</span><input id="importSpecimen" name="specimen"></label>
    <label class="field wide"><span>${e(t("notes"))}</span><textarea name="notes" rows="3"></textarea></label>
  </div>
  <div id="analysisBox" class="analysis-box hidden"></div>
  <label id="importResultsChoice" class="import-results-choice hidden"><input id="importResults" type="checkbox" checked> <span>${e(t("importDetected"))}</span></label>
  <div id="importError" class="error-box hidden"></div>
  <div class="modal-actions"><button type="button" data-close-modal>${e(t("cancel"))}</button><button id="importSave" class="primary" type="submit">${e(t("save"))}</button></div></form></div>`);

  let analyzed=null;
  const input=$("#pdfInput"), box=$("#analysisBox"), error=$("#importError"), save=$("#importSave");
  function fillField(id,value){ if(value!==undefined && value!==null && String(value).trim()) $(id).value=String(value).trim(); }
  function renderAnalysis(parsed){
    analyzed=parsed; const m=parsed.metadata||{}, rows=parsed.observations||[], warnings=[...(parsed.warnings||[])];
    if((m.patient_name && !patientLooksCompatible(m.patient_name,p)) || !detectedDobMatches(m.dob,p.dob)) warnings.unshift(t("patientMismatch"));
    fillField("#importDate",m.report_date); fillField("#importLab",m.lab); fillField("#importStudy",m.study_type); fillField("#importSpecimen",m.specimen);
    const meta=[
      [t("detectedPatient"),m.patient_name||"—"], [t("detectedOrder"),m.order_number||"—"],
      [t("branch"),m.branch||"—"], [t("provider"),m.provider_legal||"—"], [t("pages"),parsed.page_count||"—"]
    ];
    const preview=rows.slice(0,60).map(r=>`<tr><td>${e(r.test_name)}</td><td><b>${e(r.value_text||(r.value_numeric??""))}</b> ${e(r.unit||"")}</td><td>${e(r.reference_text||"—")}</td><td>${e(r.panel||"—")}</td><td>${e(r.source_page||"—")}</td></tr>`).join("");
    box.classList.remove("hidden");
    box.innerHTML=`<div class="analysis-head"><div><b>${e(parsed.ok?t("extractionReady"):t("extractionFailed"))}</b><span>${rows.length} ${e(t("resultsDetected"))} · ${Math.round((parsed.confidence||0)*100)}%</span></div><span class="confidence-badge">${e(parsed.engine||"PDF")}</span></div>
      <div class="detected-grid">${meta.map(([k,v])=>`<div><span>${e(k)}</span><b>${e(v)}</b></div>`).join("")}</div>
      ${m.address?`<div class="detected-address">${e(m.address)}${m.location?` · ${e(m.location)}`:""}</div>`:""}
      ${warnings.length?`<div class="warning-banner"><b>${e(t("parserWarnings"))}</b>${warnings.map(w=>`<span>${e(w)}</span>`).join("")}</div>`:""}
      ${rows.length?`<div class="extract-table-wrap"><table class="extract-table"><thead><tr><th>${e(t("test"))}</th><th>${e(t("value"))}</th><th>${e(t("range"))}</th><th>${e(t("study"))}</th><th>p.</th></tr></thead><tbody>${preview}</tbody></table>${rows.length>60?`<div class="more-results">+ ${rows.length-60} ${e(t("resultsDetected"))}</div>`:""}</div>`:""}`;
    $("#importResultsChoice").classList.toggle("hidden",!rows.length);
  }
  input.onchange=async()=>{
    analyzed=null; error.classList.add("hidden"); $("#importResultsChoice").classList.add("hidden");
    const file=input.files?.[0]; if(!file){ box.classList.add("hidden"); return; }
    if(!file.name.toLowerCase().endsWith(".pdf")){ error.textContent=t("pdfOnly"); error.classList.remove("hidden"); return; }
    box.classList.remove("hidden"); box.innerHTML=`<div class="analysis-loading"><span class="spinner"></span>${e(t("analyzing"))}</div>`; save.disabled=true;
    const fd=new FormData(); fd.append("file",file);
    try{ renderAnalysis(await api("/api/documents/analyze",{method:"POST",body:fd})); }
    catch(err){ box.innerHTML=`<div class="warning-banner"><b>${e(t("extractionFailed"))}</b><span>${e(err.message)}</span></div>`; }
    finally{ save.disabled=false; }
  };
  $("#importForm").onsubmit=async ev=>{
    ev.preventDefault(); const form=new FormData(ev.target); form.set("patient_id",p.id); form.set("import_results",$("#importResults").checked?"1":"0"); error.classList.add("hidden"); save.disabled=true;
    try{ const next=await api("/api/documents",{method:"POST",body:form}); setState(next); closeModal(); toast(`${t("pdfStored")}${next.importedResults?` · ${next.importedResults} ${t("resultsDetected")}`:""}`); }
    catch(err){ error.textContent=err.code==="duplicate"?t("duplicate"):err.code==="pdf_only"||err.code==="invalid_pdf"?t("pdfOnly"):err.code==="server_error"?t("importFailed"):err.message; error.classList.remove("hidden"); save.disabled=false; }
  };
}

function openBulkImportModal(){
  const p=activePatient(); if(!p) return openProfileModal();
  modal(`<div class="modal bulk-import-modal"><div class="modal-head"><div><small>PDF · BULK</small><h2>${e(t("bulkTitle"))}</h2></div><button data-close-modal>×</button></div>
    <div class="info-banner">${e(t("bulkHelp"))}</div>
    <div class="bulk-picker-row">
      <button class="primary" id="bulkFolderBtn">▤ ${e(t("selectFolder"))}</button>
      <label class="subtle-button bulk-file-label">＋ ${e(t("selectMultiple"))}<input id="bulkFilesInput" type="file" accept="application/pdf,.pdf" multiple hidden></label>
      <label class="bulk-recursive"><input id="bulkRecursive" type="checkbox"> ${e(t("includeSubfolders"))}</label>
    </div>
    <div id="bulkFolderPath" class="bulk-folder-path hidden"></div>
    <div id="bulkProgress" class="analysis-loading hidden"><span class="spinner"></span><span>${e(t("bulkAnalyzing"))}</span></div>
    <div id="bulkReview" class="bulk-review hidden"></div>
    <div id="bulkError" class="error-box hidden"></div>
    <div class="modal-actions"><button type="button" data-close-modal>${e(t("cancel"))}</button><button id="bulkImportSave" class="primary" type="button" disabled>${e(t("bulkImportSelected"))}</button></div></div>`);

  let items=[];
  let mode="";
  let currentFolder="";
  const review=$("#bulkReview"), progress=$("#bulkProgress"), err=$("#bulkError"), save=$("#bulkImportSave"), folderPath=$("#bulkFolderPath");
  const setError=msg=>{ err.textContent=msg; err.classList.remove("hidden"); };
  const clearError=()=>err.classList.add("hidden");
  const bulkCompatible=item=>{ const m=(item.parsed||{}).metadata||{}; return (!(m.patient_name)&&!m.dob) || (patientLooksCompatible(m.patient_name,p)&&detectedDobMatches(m.dob,p.dob)); };
  const rowStatus=item=>{
    if(item.duplicate) return `<span class="badge review">${e(t("bulkDuplicate"))}</span>`;
    if(item.error) return `<span class="badge review">${e(t("bulkAnalysisFailed"))}</span>`;
    const parsed=item.parsed||{}, m=parsed.metadata||{};
    const mismatch=!bulkCompatible(item);
    const warnings=(parsed.warnings||[]).length + (mismatch?1:0);
    return warnings?`<span class="badge review">${warnings} ${e(t("review"))}</span>`:`<span class="badge confirmed">✓</span>`;
  };
  function renderBulkReview(){
    const selected=items.filter(x=>x.selected&&!x.duplicate&&!x.error).length;
    save.disabled=selected===0;
    if(!items.length){ review.classList.remove("hidden"); review.innerHTML=`<div class="empty">${e(t("bulkNoPdfs"))}</div>`; return; }
    review.classList.remove("hidden");
    review.innerHTML=`<div class="bulk-review-head"><div><b>${e(t("bulkReady"))}</b><span>${items.length} PDF · ${selected} ${e(t("bulkSelected"))}</span></div><label><input id="bulkImportResults" type="checkbox" checked> ${e(t("importDetected"))}</label></div>
      <div class="bulk-table-wrap"><table class="bulk-table"><thead><tr><th></th><th>${e(t("file"))}</th><th>${e(t("date"))}</th><th>${e(t("lab"))}</th><th>${e(t("study"))}</th><th>${e(t("bulkResults"))}</th><th>${e(t("status"))}</th></tr></thead><tbody>${items.map((item,i)=>{
        const parsed=item.parsed||{}, m=parsed.metadata||{}, count=(parsed.observations||[]).length;
        const disabled=item.duplicate||item.error;
        return `<tr class="${disabled?'bulk-disabled':''}"><td><input type="checkbox" data-bulk-check="${i}" ${item.selected&&!disabled?'checked':''} ${disabled?'disabled':''}></td><td><b>${e(item.fileName||"PDF")}</b><small>${e(parsed.engine||"")}${parsed.confidence?` · ${Math.round(parsed.confidence*100)}%`:""}</small></td><td>${e(fmtDate(m.report_date))}</td><td>${e(m.lab||"—")}</td><td>${e(m.study_type||"—")}</td><td><b>${count}</b></td><td>${rowStatus(item)}</td></tr>`;
      }).join("")}</tbody></table></div>`;
    document.querySelectorAll("[data-bulk-check]").forEach(ch=>ch.onchange=()=>{items[Number(ch.dataset.bulkCheck)].selected=ch.checked;renderBulkReview();});
  }
  async function analyzeLocalFolder(folder){
    clearError(); mode="folder"; currentFolder=folder; progress.classList.remove("hidden"); review.classList.add("hidden"); save.disabled=true;
    folderPath.textContent=folder; folderPath.classList.remove("hidden");
    try{
      const result=await api("/api/documents/bulk/analyze-local",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({folder,recursive:$("#bulkRecursive").checked})});
      items=(result.items||[]).map(x=>({...x,selected:!x.duplicate&&!x.error&&bulkCompatible(x)}));
      renderBulkReview();
    }catch(ex){setError(ex.message||t("bulkAnalysisFailed"));}
    finally{progress.classList.add("hidden");}
  }
  $("#bulkRecursive").onchange=()=>{ if(mode==="folder"&&currentFolder) analyzeLocalFolder(currentFolder); };
  $("#bulkFolderBtn").onclick=async()=>{
    clearError();
    if(!window.pywebview?.api?.select_pdf_folder){ setError(t("bulkFolderOnly")); return; }
    try{
      const picked=await window.pywebview.api.select_pdf_folder();
      if(!picked?.ok){setError(picked?.error||t("bulkFolderOnly"));return;}
      if(picked.cancelled||!picked.folder)return;
      await analyzeLocalFolder(picked.folder);
    }catch(ex){setError(ex.message||t("bulkFolderOnly"));}
  };
  $("#bulkFilesInput").onchange=async ev=>{
    clearError(); mode="files"; folderPath.classList.add("hidden"); items=[]; review.classList.add("hidden"); save.disabled=true;
    const files=[...(ev.target.files||[])].filter(f=>f.name.toLowerCase().endsWith(".pdf"));
    if(!files.length){setError(t("bulkNoPdfs"));return;}
    progress.classList.remove("hidden");
    const progressText=progress.querySelector("span:last-child");
    for(let i=0;i<files.length;i++){
      const file=files[i]; progressText.textContent=`${t("analyzing")} ${i+1}/${files.length} · ${file.name}`;
      const fd=new FormData(); fd.append("file",file);
      try{
        const parsed=await api("/api/documents/analyze",{method:"POST",body:fd});
        const duplicate=state.documents.some(d=>d.sha256===parsed.sha256);
        const item={fileName:file.name,file,parsed,duplicate,selected:false}; item.selected=!duplicate&&bulkCompatible(item); items.push(item);
      }catch(ex){items.push({fileName:file.name,file,error:ex.code||"analysis_failed",selected:false});}
    }
    progress.classList.add("hidden"); renderBulkReview();
  };
  save.onclick=async()=>{
    clearError(); const chosen=items.filter(x=>x.selected&&!x.duplicate&&!x.error);
    if(!chosen.length){setError(t("bulkSelectAtLeastOne"));return;}
    const importResults=$("#bulkImportResults")?.checked!==false;
    save.disabled=true; progress.classList.remove("hidden");
    const progressText=progress.querySelector("span:last-child");
    try{
      let importedDocs=0, importedResults=0, lastState=null;
      if(mode==="folder"){
        progressText.textContent=`${t("bulkImportSelected")} · ${chosen.length}`;
        const result=await api("/api/documents/bulk/import-local",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({patientId:p.id,paths:chosen.map(x=>x.path),importResults})});
        importedDocs=result.importedDocuments||0; importedResults=result.importedResults||0; lastState=result.state;
      }else{
        for(let i=0;i<chosen.length;i++){
          const item=chosen[i], parsed=item.parsed||{}, m=parsed.metadata||{};
          progressText.textContent=`${t("bulkImportSelected")} ${i+1}/${chosen.length} · ${item.fileName}`;
          const fd=new FormData(); fd.append("file",item.file); fd.set("patient_id",p.id); fd.set("import_results",importResults?"1":"0");
          if(m.report_date)fd.set("report_date",m.report_date); if(m.lab)fd.set("lab",m.lab); if(m.study_type)fd.set("study_type",m.study_type); if(m.specimen)fd.set("specimen",m.specimen);
          try{const result=await api("/api/documents",{method:"POST",body:fd}); importedDocs++; importedResults+=result.importedResults||0; lastState=result.state;}
          catch(ex){if(ex.code!=="duplicate") throw ex;}
        }
      }
      if(lastState) state=lastState;
      closeModal(); render(); toast(`${importedDocs} ${t("bulkImported")} · ${importedResults} ${t("resultsDetected")}`);
    }catch(ex){progress.classList.add("hidden");save.disabled=false;setError(ex.message||t("importFailed"));}
  };
}

function openResultModal(){ const p=activePatient(); if(!p) return; const d=docs(); modal(`<div class="modal result-modal"><div class="modal-head"><div><small>${e(t("advanced").toUpperCase())}</small><h2>${e(t("resultTitle"))}</h2></div><button data-close-modal>×</button></div><form id="resultForm"><div class="form-grid">
  <label class="field"><span>${e(t("test"))} *</span><input name="testName" required></label><label class="field"><span>${e(t("value"))} *</span><input name="value" required></label><label class="field"><span>${e(t("unit"))}</span><input name="unit"></label><label class="field"><span>${e(t("date"))} *</span><input name="date" type="date" required value="${today()}"></label><label class="field"><span>${e(t("low"))}</span><input name="referenceLow" type="number" step="any"></label><label class="field"><span>${e(t("high"))}</span><input name="referenceHigh" type="number" step="any"></label><label class="field"><span>${e(t("lab"))}</span><input name="lab"></label><label class="field"><span>${e(t("associatedPdf"))}</span><select name="documentId"><option value="">${e(t("none"))}</option>${d.map(x=>`<option value="${x.id}">${e(x.report_date||"")} · ${e(x.study_type||x.file_name)}</option>`).join("")}</select></label><label class="field wide"><span>${e(t("notes"))}</span><textarea name="notes" rows="3"></textarea></label></div><div class="modal-actions"><button type="button" data-close-modal>${e(t("cancel"))}</button><button class="primary" type="submit">${e(t("save"))}</button></div></form></div>`);
  $("#resultForm").onsubmit=async ev=>{ev.preventDefault(); const data=Object.fromEntries(new FormData(ev.target)); data.patientId=p.id; try{const next=await api("/api/observations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});setState(next);closeModal();toast(t("resultStored"));}catch(err){alert(err.message);}};
}
function openMeasurementModal(kind){
  const p=activePatient(); if(!p)return;
  const isBp=kind==="blood_pressure", isGlucose=kind==="glucose", isWeight=kind==="weight";
  const title=isBp?t("addBloodPressure"):isGlucose?t("addGlucose"):t("addWeight");
  const measurementFields=isBp
    ?`<label class="field"><span>${e(t("systolic"))} *</span><input name="systolic" inputmode="decimal" type="number" step="1" required></label><label class="field"><span>${e(t("diastolic"))} *</span><input name="diastolic" inputmode="decimal" type="number" step="1" required></label><label class="field"><span>${e(t("pulse"))}</span><input name="pulse" inputmode="decimal" type="number" step="1"></label>`
    :isGlucose
      ?`<label class="field"><span>${e(t("glucoseReading"))} *</span><input name="glucoseValue" inputmode="decimal" type="number" step="any" required></label><label class="field"><span>${e(t("glucoseUnit"))}</span><select name="glucoseUnit"><option value="mg/dL">mg/dL</option><option value="mmol/L">mmol/L</option></select></label><label class="field"><span>${e(t("glucoseContext"))}</span><select name="context"><option value="random">${e(t("random"))}</option><option value="fasting">${e(t("fasting"))}</option><option value="before_meal">${e(t("beforeMeal"))}</option><option value="after_meal_1h">${e(t("afterMeal1"))}</option><option value="after_meal_2h">${e(t("afterMeal2"))}</option><option value="bedtime">${e(t("bedtime"))}</option><option value="other">${e(t("other"))}</option></select></label>`
      :`<label class="field"><span>${e(t("weightReading"))} *</span><input name="weightValue" inputmode="decimal" type="number" min="0" step="0.1" required></label><label class="field"><span>${e(t("weightUnit"))}</span><select name="weightUnit"><option value="kg">kg</option><option value="lb">lb</option></select></label>`;
  modal(`<div class="modal result-modal"><div class="modal-head"><div><small>${e(t("dailyReadings").toUpperCase())}</small><h2>${e(title)}</h2></div><button data-close-modal>×</button></div><form id="measurementForm"><div class="form-grid">
    <label class="field"><span>${e(t("measuredAt"))} *</span><input name="measuredAt" type="datetime-local" required value="${e(nowLocalInput())}"></label>
    ${measurementFields}
    <label class="field"><span>${e(t("device"))}</span><input name="deviceLabel" placeholder="Omron / Accu-Chek / Báscula / …"></label><label class="field wide"><span>${e(t("notes"))}</span><textarea name="notes" rows="3"></textarea></label>
  </div><div class="modal-actions"><button type="button" data-close-modal>${e(t("cancel"))}</button><button class="primary" type="submit">${e(t("save"))}</button></div></form></div>`);
  $("#measurementForm").onsubmit=async ev=>{ev.preventDefault(); const data=Object.fromEntries(new FormData(ev.target)); data.patientId=p.id; data.kind=kind; data.sourceType="manual"; try{setState(await api("/api/measurements",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)}));closeModal();toast(t("measurementStored"));}catch(err){alert(err.message);}};
}
async function openPdf(id){
  const d=state.documents.find(x=>x.id===id); if(!d)return;
  modal(`<div class="pdf-modal"><div class="pdf-toolbar"><button data-close-modal>← ${e(t("close"))}</button><div class="pdf-title"><b>${e(d.study_type||d.file_name)}</b><small>${e(d.file_name)}</small></div><div class="toolbar-actions"><span id="pdfPageCount" class="pdf-page-count"></span>${d.status==="review"?`<button id="confirmPdf">✓ ${e(t("confirm"))}</button>`:""}${state.advancedMode?`<a class="button-like" href="/pdf/${d.id}" target="_blank" rel="noopener noreferrer">↗ ${e(t("externalPdf"))}</a><button id="deletePdf" class="danger-button">${e(t("deletePdf"))}</button>`:""}</div></div><div class="pdf-layout"><aside class="pdf-meta"><div class="meta-block"><span>${e(t("date"))}</span><b>${e(fmtDate(d.report_date))}</b></div><div class="meta-block"><span>${e(t("lab"))}</span><b>${e(d.lab||"—")}</b></div>${d.branch?`<div class="meta-block"><span>${e(t("branch"))}</span><b>${e(d.branch)}</b></div>`:""}${d.order_number?`<div class="meta-block"><span>${e(t("detectedOrder"))}</span><b>${e(d.order_number)}</b></div>`:""}${d.patient_name_detected?`<div class="meta-block"><span>${e(t("detectedPatient"))}</span><b>${e(d.patient_name_detected)}</b></div>`:""}<div class="meta-block"><span>${e(t("study"))}</span><b>${e(d.study_type||"—")}</b></div><div class="meta-block"><span>${e(t("specimen"))}</span><b>${e(d.specimen||"—")}</b></div><div class="meta-block"><span>${e(t("status"))}</span><b>${e(d.status==="review"?t("statusReview"):t("statusConfirmed"))}</b></div><div class="meta-block"><span>${e(t("hash"))}</span><code>${e(d.sha256)}</code></div><div class="meta-block"><span>${e(t("notes"))}</span><p>${e(d.notes||"—")}</p></div></aside><div class="pdf-viewer"><div id="pdfPages" class="pdf-pages"><div class="pdf-loading">${e(t("pdfLoading"))}</div></div></div></div></div>`);
  try{
    const info=await api(`/api/documents/${d.id}/pdf-info`);
    const count=Math.max(1,Number(info.pageCount)||Number(d.page_count)||1);
    const counter=$("#pdfPageCount"); if(counter) counter.textContent=`${count} ${t("pdfPages")}`;
    const holder=$("#pdfPages");
    if(holder){
      holder.innerHTML=Array.from({length:count},(_,i)=>`<figure class="pdf-page"><figcaption>${e(t("pdfPage"))} ${i+1} / ${count}</figcaption><img loading="${i===0?'eager':'lazy'}" src="/pdf-page/${d.id}/${i+1}" alt="${e(t("pdfPage"))} ${i+1}"></figure>`).join("");
    }
  }catch(err){
    const holder=$("#pdfPages"); if(holder) holder.innerHTML=`<div class="error-box">${e(err.message||"PDF")}</div>`;
  }
  $("#confirmPdf") && ($("#confirmPdf").onclick=async()=>{setState(await api(`/api/documents/${d.id}/confirm`,{method:"POST"}));closeModal();toast(t("stored"));});
  $("#deletePdf") && ($("#deletePdf").onclick=async()=>{if(!confirm(t("confirmDelete")))return;try{setState(await api(`/api/documents/${d.id}`,{method:"DELETE"}));closeModal();}catch(err){alert(err.code==="document_has_results"?t("documentHasResults"):err.message);}});
}
function openDoctor(){ const p=activePatient(); if(!p)return; const d=docs().slice(0,8), abnormal=obs().filter(isAbnormal).slice(0,10), recentM=measures().slice(0,8); modal(`<div class="doctor-modal"><div class="doctor-head"><div><small>${e(t("doctorTitle").toUpperCase())}</small><h1>${e(p.name)}</h1><p>${e(t("doctorSub"))}</p></div><div class="doctor-actions"><button id="doctorPrint">⎙</button><button data-close-modal>×</button></div></div><div class="doctor-grid"><section class="doctor-section"><h2>${e(t("latest"))}</h2>${d.length?d.map(x=>`<button class="doctor-row" data-open-pdf="${x.id}"><div><b>${e(x.study_type||x.file_name)}</b><span>${e(x.lab||"—")}</span></div><strong>${e(fmtDate(x.report_date))}</strong><em>›</em></button>`).join(""):`<div class="empty">${e(t("emptyDocs"))}</div>`}</section><section class="doctor-section"><h2>${e(t("abnormal"))}</h2>${abnormal.length?abnormal.map(o=>`<div class="doctor-result"><div><b>${e(o.test_name)}</b><span>${e(fmtDate(o.date))} · ${e(o.lab||"—")}</span></div><strong class="${flag(o)}">${e(o.value)} ${e(o.unit||"")} · ${e(flagLabel(o))}</strong></div>`).join(""):`<div class="empty">${e(t("noAbnormal"))}</div>`}</section><section class="doctor-section doctor-readings"><h2>${e(t("dailyReadings"))}</h2>${recentM.length?recentM.map(m=>`<div class="doctor-result"><div><b>${e(m.kind==="blood_pressure"?t("bloodPressure"):m.kind==="glucose"?t("glucoseReading"):t("weightReading"))}</b><span>${e(fmtDateTime(m.measured_at))}${m.kind==="glucose"&&m.context?` · ${e(measurementContextLabel(m.context))}`:""}</span></div><strong>${e(measurementSummary(m))}</strong></div>`).join(""):`<div class="empty">${e(t("noMeasurements"))}</div>`}</section></div><footer>${e(t("medicalDisclaimer"))}</footer></div>`);
  $("#doctorPrint").onclick=()=>window.print(); document.querySelectorAll("[data-open-pdf]").forEach(b=>b.onclick=()=>openPdf(Number(b.dataset.openPdf)));
}
async function saveSettings(payload){ setState(await api("/api/settings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)})); toast(t("settingsUpdated")); }
async function selectPatient(id){ setState(await api(`/api/profiles/${id}/select`,{method:"POST"})); }
async function deleteProfile(id){ if(!confirm(t("confirmDelete")))return; try{setState(await api(`/api/profiles/${id}`,{method:"DELETE"}));}catch(err){alert(err.code==="profile_has_records"?t("cannotDelete"):err.message);} }
async function deleteResult(id){ if(!confirm(t("confirmDelete")))return; setState(await api(`/api/observations/${id}`,{method:"DELETE"})); }
async function deleteMeasurement(id){ if(!confirm(t("confirmDelete")))return; setState(await api(`/api/measurements/${id}`,{method:"DELETE"})); }
async function openInBrowser(){
  try{
    if(window.pywebview?.api?.open_in_browser){ await window.pywebview.api.open_in_browser(); return; }
    window.open(location.href,"_blank","noopener");
  }catch(err){ alert(err.message||String(err)); }
}
async function closeApplication(){
  if(!confirm(t("closeAppConfirm"))) return;
  const button=$("#shutdownBtn"); if(button) button.disabled=true;
  try{
    if(window.pywebview?.api?.close_app){
      await window.pywebview.api.close_app();
      return;
    }
    await api("/api/shutdown",{method:"POST"});
    document.body.innerHTML=`<main class="closed-app"><div><div class="brand-mark">${state.language==="en"?"CR":"RC"}</div><h1>${e(t("appName"))}</h1><small>by CodeCafe</small><p>${e(t("appClosed"))}</p></div></main>`;
  }catch(err){ if(button) button.disabled=false; alert(err.message); }
}
function openNav(){ $("#sidebar").classList.add("open"); $("#mobileOverlay").classList.add("open"); }
function closeNav(){ $("#sidebar").classList.remove("open"); $("#mobileOverlay").classList.remove("open"); }

$("#menuBtn").onclick=openNav; $("#closeNav").onclick=closeNav; $("#mobileOverlay").onclick=closeNav;
$("#langBtn").onclick=()=>saveSettings({language:state.language==="es"?"en":"es"});
$("#patientSelect").onchange=ev=>ev.target.value&&selectPatient(Number(ev.target.value));
$("#doctorBtn").onclick=openDoctor; $("#importBtn").onclick=openImportModal; $("#bulkImportBtn").onclick=openBulkImportModal; $("#shutdownBtn").onclick=closeApplication;
render();
