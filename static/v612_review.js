/* CodeCafe Registros Clínicos v0.6.12
 * Review-time OCR correction layer.
 * Loaded after app.js so the stable v0.6.11 UI remains the base.
 */

Object.assign(copy.es, {
  ocrCorrectionNotice:"Los resultados detectados por OCR no son definitivos. Si algún valor, unidad, analito o rango fue leído incorrectamente, podrás corregirlo durante la revisión y también después desde Modo avanzado.",
  reviewResults:"Revisar resultados capturados",
  reviewResultsHelp:"Compara estos datos con el PDF original. Puedes corregirlos antes de confirmar el reporte.",
  saveCorrections:"Guardar correcciones",
  correctionsStored:"Correcciones guardadas",
  corrected:"Corregido manualmente",
  ocrOriginal:"OCR original",
  editResult:"Editar resultado",
  confirmAndSave:"Guardar correcciones y confirmar",
  noReviewResults:"Este PDF no tiene resultados estructurados para revisar."
});
Object.assign(copy.en, {
  ocrCorrectionNotice:"OCR-detected results are not final. If a value, unit, analyte or reference range was read incorrectly, you can correct it during review and later from Advanced mode.",
  reviewResults:"Review captured results",
  reviewResultsHelp:"Compare these values with the original PDF. You can correct them before confirming the report.",
  saveCorrections:"Save corrections",
  correctionsStored:"Corrections saved",
  corrected:"Manually corrected",
  ocrOriginal:"Original OCR",
  editResult:"Edit result",
  confirmAndSave:"Save corrections and confirm",
  noReviewResults:"This PDF has no structured results to review."
});

function v612CorrectionNotice(){
  return `<div class="ocr-correction-notice"><b>OCR</b><span>${e(t("ocrCorrectionNotice"))}</span></div>`;
}

function v612InjectImportNotice(selector){
  const root=document.querySelector(selector);
  if(!root || root.querySelector(".ocr-correction-notice")) return;
  const banner=root.querySelector(".info-banner");
  if(banner) banner.insertAdjacentHTML("afterend",v612CorrectionNotice());
  else root.insertAdjacentHTML("afterbegin",v612CorrectionNotice());
}

const v612OpenImportModalBase=openImportModal;
openImportModal=function(){
  v612OpenImportModalBase();
  v612InjectImportNotice(".import-modal");
};

const v612OpenBulkImportModalBase=openBulkImportModal;
openBulkImportModal=function(){
  v612OpenBulkImportModalBase();
  v612InjectImportNotice(".bulk-import-modal");
};

// app.js wires the persistent header buttons before this layer loads, so rebind
// those two handlers to the enhanced v0.6.12 import functions.
if(document.querySelector("#importBtn")) document.querySelector("#importBtn").onclick=openImportModal;
if(document.querySelector("#bulkImportBtn")) document.querySelector("#bulkImportBtn").onclick=openBulkImportModal;

function v612ValueForInput(o){
  if(o.value_numeric!==null && o.value_numeric!==undefined) return o.value_numeric;
  return o.value_text ?? o.value ?? "";
}

function v612OriginalSummary(original){
  if(!original) return "";
  const range=original.referenceText || [original.referenceLow,original.referenceHigh].filter(v=>v!==null&&v!==undefined&&v!=="").join(" – ");
  const parts=[original.testName, `${original.value??""} ${original.unit||""}`.trim(), range].filter(Boolean);
  return parts.length?`<small class="ocr-original-line"><b>${e(t("ocrOriginal"))}:</b> ${e(parts.join(" · "))}</small>`:"";
}

function v612ReviewRow(o){
  return `<tr class="ocr-review-row" data-review-observation="${o.id}">
    <td><input data-review-field="testName" value="${e(o.test_name||o.raw_test_name||"")}" aria-label="${e(t("test"))}">${o.manual_corrected?`<small class="manual-corrected">✓ ${e(t("corrected"))}</small>`:""}${v612OriginalSummary(o.ocr_original)}</td>
    <td><input class="compact-input" data-review-field="value" value="${e(v612ValueForInput(o))}" aria-label="${e(t("value"))}"></td>
    <td><input class="compact-input" data-review-field="unit" value="${e(o.unit||"")}" aria-label="${e(t("unit"))}"></td>
    <td><div class="range-editor"><input data-review-field="referenceLow" value="${e(o.reference_low??"")}" placeholder="${e(t("low"))}"><span>–</span><input data-review-field="referenceHigh" value="${e(o.reference_high??"")}" placeholder="${e(t("high"))}"></div><input class="range-text-input" data-review-field="referenceText" value="${e(o.reference_text||"")}" placeholder="${e(t("range"))}"></td>
    <td>${e(o.source_page||"—")}</td>
  </tr>`;
}

async function v612LoadReviewPanel(documentId){
  const host=document.querySelector(".pdf-modal");
  if(!host) return;
  let panel=host.querySelector("#ocrReviewPanel");
  if(!panel){
    const layout=host.querySelector(".pdf-layout");
    if(!layout) return;
    panel=document.createElement("section");
    panel.id="ocrReviewPanel";
    panel.className="ocr-review-panel";
    layout.parentNode.insertBefore(panel,layout);
  }
  panel.innerHTML=`<div class="analysis-loading"><span class="spinner"></span>${e(t("review"))}</div>`;
  try{
    const data=await api(`/api/documents/${documentId}/review-results`);
    const rows=data.observations||[];
    panel.innerHTML=`<div class="ocr-review-heading"><div><small>OCR · ${e(t("statusReview").toUpperCase())}</small><h3>${e(t("reviewResults"))}</h3><p>${e(t("reviewResultsHelp"))}</p></div><button class="subtle-button" id="saveOcrCorrections" ${rows.length?"":"disabled"}>${e(t("saveCorrections"))}</button></div>
      ${rows.length?`<div class="ocr-review-table-wrap"><table class="ocr-review-table"><thead><tr><th>${e(t("test"))}</th><th>${e(t("value"))}</th><th>${e(t("unit"))}</th><th>${e(t("range"))}</th><th>p.</th></tr></thead><tbody>${rows.map(v612ReviewRow).join("")}</tbody></table></div>`:`<div class="empty compact-empty">${e(t("noReviewResults"))}</div>`}`;
    const save=document.querySelector("#saveOcrCorrections");
    if(save) save.onclick=async()=>{await v612SaveReviewCorrections(documentId,true);};
  }catch(err){
    panel.innerHTML=`<div class="error-box">${e(err.message||String(err))}</div>`;
  }
}

function v612ReadReviewRows(){
  return [...document.querySelectorAll("[data-review-observation]")].map(row=>{
    const result={id:Number(row.dataset.reviewObservation)};
    row.querySelectorAll("[data-review-field]").forEach(input=>{ result[input.dataset.reviewField]=input.value; });
    return result;
  });
}

async function v612SaveReviewCorrections(documentId, reload=false){
  const rows=v612ReadReviewRows();
  if(!rows.length) return {changed:0};
  const result=await api(`/api/documents/${documentId}/review-results`,{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({observations:rows})
  });
  setState(result);
  if(result.changed) toast(`${t("correctionsStored")} · ${result.changed}`);
  if(reload) await v612LoadReviewPanel(documentId);
  return result;
}

const v612OpenPdfBase=openPdf;
openPdf=async function(id){
  await v612OpenPdfBase(id);
  const d=state.documents.find(x=>x.id===id);
  if(!d) return;
  if(d.status==="review"){
    await v612LoadReviewPanel(id);
    const confirmButton=document.querySelector("#confirmPdf");
    if(confirmButton){
      confirmButton.textContent=`✓ ${t("confirmAndSave")}`;
      confirmButton.onclick=async()=>{
        confirmButton.disabled=true;
        try{
          await v612SaveReviewCorrections(id,false);
          setState(await api(`/api/documents/${id}/confirm`,{method:"POST"}));
          closeModal();
          toast(t("stored"));
        }catch(err){
          confirmButton.disabled=false;
          alert(err.message||String(err));
        }
      };
    }
  }
};

function v612EnsureAdvancedEditButtons(){
  if(!state.advancedMode) return;
  document.querySelectorAll("[data-delete-result]").forEach(del=>{
    const cell=del.parentElement;
    if(!cell || cell.querySelector("[data-edit-result]")) return;
    const button=document.createElement("button");
    button.className="edit-result-button";
    button.dataset.editResult=del.dataset.deleteResult;
    button.title=t("editResult");
    button.setAttribute("aria-label",t("editResult"));
    button.textContent="✎";
    cell.insertBefore(button,del);
  });
}

function v612OpenEditResultModal(id){
  const o=state.observations.find(x=>x.id===id);
  if(!o || !state.advancedMode) return;
  modal(`<div class="modal result-modal"><div class="modal-head"><div><small>${e(t("advanced").toUpperCase())}</small><h2>${e(t("editResult"))}</h2></div><button data-close-modal>×</button></div><form id="editObservationForm"><div class="form-grid">
    <label class="field wide"><span>${e(t("test"))} *</span><input name="testName" required value="${e(o.test_name||o.raw_test_name||"")}"></label>
    <label class="field"><span>${e(t("value"))} *</span><input name="value" required value="${e(v612ValueForInput(o))}"></label>
    <label class="field"><span>${e(t("unit"))}</span><input name="unit" value="${e(o.unit||"")}"></label>
    <label class="field"><span>${e(t("date"))}</span><input name="date" type="date" value="${e(o.date||"")}"></label>
    <label class="field"><span>${e(t("low"))}</span><input name="referenceLow" type="number" step="any" value="${e(o.reference_low??"")}"></label>
    <label class="field"><span>${e(t("high"))}</span><input name="referenceHigh" type="number" step="any" value="${e(o.reference_high??"")}"></label>
    <label class="field wide"><span>${e(t("range"))}</span><input name="referenceText" value="${e(o.reference_text||"")}"></label>
    <label class="field"><span>${e(t("lab"))}</span><input name="lab" value="${e(o.lab||"")}"></label>
    <label class="field"><span>${e(t("study"))}</span><input name="panel" value="${e(o.panel||"")}"></label>
    <label class="field wide"><span>${e(t("notes"))}</span><textarea name="notes" rows="3">${e(o.notes||"")}</textarea></label>
  </div>${o.raw_test_name?`<div class="ocr-correction-notice"><b>${e(t("ocrOriginal"))}</b><span>${e(o.raw_test_name)}</span></div>`:""}<div class="modal-actions"><button type="button" data-close-modal>${e(t("cancel"))}</button><button class="primary" type="submit">${e(t("save"))}</button></div></form></div>`);
  document.querySelector("#editObservationForm").onsubmit=async ev=>{
    ev.preventDefault();
    const data=Object.fromEntries(new FormData(ev.target));
    try{
      const result=await api(`/api/observations/${id}/edit`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
      setState(result); closeModal(); toast(t("correctionsStored"));
    }catch(err){ alert(err.message||String(err)); }
  };
}

document.addEventListener("click",ev=>{
  const button=ev.target.closest?.("[data-edit-result]");
  if(!button) return;
  ev.preventDefault(); ev.stopPropagation();
  v612OpenEditResultModal(Number(button.dataset.editResult));
});

const v612Observer=new MutationObserver(()=>v612EnsureAdvancedEditButtons());
v612Observer.observe(document.body,{childList:true,subtree:true});
v612EnsureAdvancedEditButtons();
