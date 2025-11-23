const API_URL = "http://localhost:5000/api/identify"; 

const $ = (q, ctx=document) => ctx.querySelector(q);
const $$ = (q, ctx=document) => Array.from(ctx.querySelectorAll(q));
const el = (tag, cls) => { const x = document.createElement(tag); if(cls) x.className = cls; return x; };

const toasts = (() => {
  let container = document.createElement("div");
  container.id = "toasts";
  container.className = "toasts";
  document.body.appendChild(container);
  return container;
})();

function toast(msg, type="ok", timeout=3200){
  const t = el("div", `toast ${type}`);
  t.textContent = msg;
  toasts.appendChild(t);
  setTimeout(()=>{ t.style.opacity=0; setTimeout(()=>t.remove(), 300); }, timeout);
}

function enableTilt(){
  const tiltElems = document.querySelectorAll("[data-tilt]");
  tiltElems.forEach(card=>{
    if(card._tiltAttached) return;
    card._tiltAttached = true;
    card.addEventListener("mousemove", (e)=>{
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      const tiltX = (y - 0.5) * -6;
      const tiltY = (x - 0.5) *  6;
      card.style.transform = `perspective(900px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
    });
    card.addEventListener("mouseleave", ()=> card.style.transform = "");
  });
}
enableTilt();

$("#themeToggle").addEventListener("click", ()=> document.body.classList.toggle("light"));

const fileInput = $("#fileInput");
const dropzone = $("#dropzone");
const dzClick = $("#dzClick");
const results = $("#results");

dzClick.addEventListener("click", ()=> fileInput.click());

["dragenter","dragover"].forEach(evt=> dropzone.addEventListener(evt, (e)=>{
  e.preventDefault(); e.stopPropagation(); dropzone.classList.add("dragover");
}));
["dragleave","drop"].forEach(evt=> dropzone.addEventListener(evt, (e)=>{
  e.preventDefault(); e.stopPropagation(); dropzone.classList.remove("dragover");
}));
dropzone.addEventListener("drop", (e)=>{
  const files = [...e.dataTransfer.files].filter(f=> /^image\//.test(f.type));
  if(!files.length){ toast("No images detected.", "err"); return; }
  handleFiles(files);
});
fileInput.addEventListener("change", ()=> {
  if(!fileInput.files?.length) return;
  handleFiles([...fileInput.files]);
});

const openCameraBtn = $("#openCamera");
const cameraCard = $("#cameraCard");
const video = $("#cameraVideo");
const canvas = $("#cameraCanvas");
const captureBtn = $("#captureBtn");
const closeCameraBtn = $("#closeCamera");

let cameraStream = null;

async function openCamera(){
  try{
    const constraints = { video: { facingMode: { ideal: "environment" } } , audio: false };
    cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = cameraStream;
    video.classList.remove("hidden");
    cameraCard.classList.remove("hidden");
    enableTilt();
  }catch(err){
    console.error("Camera error:", err);
    toast("Could not access camera. Check permissions or try a different browser.", "err");
  }
}

function stopCamera(){
  if(!cameraStream) return;
  cameraStream.getTracks().forEach(t => t.stop());
  cameraStream = null;
  video.srcObject = null;
  cameraCard.classList.add("hidden");
}

openCameraBtn.addEventListener("click", openCamera);
closeCameraBtn.addEventListener("click", stopCamera);

captureBtn.addEventListener("click", async ()=>{
  if(!cameraStream){
    toast("Camera not active.", "err");
    return;
  }
  const w = video.videoWidth;
  const h = video.videoHeight;
  if(!w || !h){
    toast("Could not capture frame — try again.", "err");
    return;
  }
  canvas.width = w; canvas.height = h;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, w, h);

  canvas.toBlob(async (blob) => {
    if(!blob){ toast("Capture failed.", "err"); return; }
    const file = new File([blob], `camera_${Date.now()}.jpg`, { type: "image/jpeg" });
    handleFiles([file]);
  }, "image/jpeg", 0.92);
});

async function handleFiles(files){
  // Clear previous results and hide the image
  $("#sustainability-score").textContent = "Detecting...";
  $("#items-list").innerHTML = "<li>Loading items...</li>";
  $("#greener-alternatives-list").innerHTML = "<li>Loading greener alternatives...</li>";
  $("#temp-reg-suggestions-list").innerHTML = "<li>Loading temperature regulation suggestions...</li>";
  const originalImage = $("#original-image");
  originalImage.src = "";
  originalImage.style.display = "none";

  if (files.length > 0) {
    const reader = new FileReader();
    reader.onload = (e) => {
      originalImage.src = e.target.result;
      originalImage.style.display = "block";
    };
    reader.readAsDataURL(files[0]); // Display the first image if multiple are uploaded
  }

  try{
    const form = new FormData();
    files.forEach(f => form.append("images", f, f.name));

    const res = await fetch(API_URL, { method:"POST", body: form });
    if(!res.ok){
      const txt = await res.text();
      throw new Error(`Server error ${res.status}: ${txt}`);
    }
    const data = await res.json();
    if(!data.results) throw new Error("Malformed server response.");

    fillCardResult(data.results[0]);

    toast(`Analyzed ${data.results.length} image(s).`, "ok");
  }catch(err){
    console.error(err);
    toast(err.message || "Request failed.", "err");
    // Clear loading messages on error
    $("#sustainability-score").textContent = "Error";
    $("#items-list").innerHTML = "<li>Error loading items.</li>";
    $("#greener-alternatives-list").innerHTML = "<li>Error loading greener alternatives.</li>";
    $("#temp-reg-suggestions-list").innerHTML = "<li>Error loading temperature regulation suggestions.</li>";
  }
}

function fillCardResult(result){
  const sustainabilityScore = $("#sustainability-score");
  const itemsList = $("#items-list");
  const greenerAlternativesList = $("#greener-alternatives-list");
  const tempRegSuggestionsList = $("#temp-reg-suggestions-list");

  if(result.error){
    sustainabilityScore.textContent = "Error";
    itemsList.innerHTML = `<li>${result.error}</li>`;
    return;
  }

  sustainabilityScore.textContent = result.sustainability_score || "Not available";
  
  itemsList.innerHTML = "";
  if(result.items && result.items.length > 0){
    result.items.forEach(item => {
      const li = el("li");
      li.innerHTML = `<strong>${item.name}:</strong> ${item.description}`;
      itemsList.appendChild(li);
    });
  } else {
    itemsList.innerHTML = "<li>No items detected.</li>";
  }

  greenerAlternativesList.innerHTML = "";
  if(result.greener_alternatives && result.greener_alternatives.length > 0){
    result.greener_alternatives.forEach(alt => {
      const li = el("li");
      li.innerHTML = `<strong>${alt.name}:</strong> ${alt.alternative}`;
      greenerAlternativesList.appendChild(li);
    });
  } else {
    greenerAlternativesList.innerHTML = "<li>No greener alternatives suggested.</li>";
  }

  tempRegSuggestionsList.innerHTML = "";
  if(result.temperature_regulation_suggestions && result.temperature_regulation_suggestions.length > 0){
    result.temperature_regulation_suggestions.forEach(suggestion => {
      const li = el("li");
      li.textContent = suggestion;
      tempRegSuggestionsList.appendChild(li);
    });
  } else {
    tempRegSuggestionsList.innerHTML = "<li>No temperature regulation suggestions available.</li>";
  }
}