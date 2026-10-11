// ─── Cattle Disease Detection Script ───

function previewImage() {
  const fileInput = document.getElementById('fileInput');
  const previewContainer = document.getElementById('previewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const buttonContainer = document.getElementById('buttonContainer');
  const uploadZone = document.getElementById('uploadZone');

  if (!fileInput.files || !fileInput.files[0]) {
    previewContainer.style.display = 'none';
    buttonContainer.style.display = 'none';
    uploadZone.style.display = 'block';
    imagePreview.src = '';
    return;
  }

  const file = fileInput.files[0];
  const reader = new FileReader();

  reader.onload = function(e) {
    imagePreview.src = e.target.result;
    previewContainer.style.display = 'block';
    buttonContainer.style.display = 'block';
    uploadZone.style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
  };

  reader.readAsDataURL(file);
}

// Drag & drop
const uploadZone = document.getElementById('uploadZone');
if (uploadZone) {
  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = 'var(--primary)';
    uploadZone.style.background = 'var(--primary-light)';
  });
  uploadZone.addEventListener('dragleave', () => {
    uploadZone.style.borderColor = '#bfcfe8';
    uploadZone.style.background = 'var(--light-bg)';
  });
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = '#bfcfe8';
    uploadZone.style.background = 'var(--light-bg)';
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      document.getElementById('fileInput').files = files;
      previewImage();
    }
  });
}

function uploadImage() {
  const fileInput = document.getElementById('fileInput');
  if (!fileInput.files || !fileInput.files[0]) {
    alert('Please select an image first!');
    return;
  }

  const btn = document.getElementById('analyzeBtn');
  const btnText = document.getElementById('btnText');
  btn.disabled = true;
  btnText.textContent = '⏳ Analyzing...';

  const resultSection = document.getElementById('resultSection');
  const resultCard = document.getElementById('resultCard');

  // Show loading
  resultSection.style.display = 'block';
  resultCard.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <h3>Analyzing your cattle image...</h3>
      <p>Our AI model is processing the image. Please wait...</p>
    </div>
  `;
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  fetch('/cattle/predict', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    btn.disabled = false;
    btnText.textContent = '🔬 Analyze Image';

    if (data.error) {
      renderError(resultCard, data.error);
    } else {
      renderResult(resultCard, data);
    }
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  })
  .catch(error => {
    btn.disabled = false;
    btnText.textContent = '🔬 Analyze Image';
    renderError(resultCard, 'Network error. Please check your connection and try again.');
    console.error('Error:', error);
  });
}

function getHeaderClass(prediction) {
  const lower = prediction.toLowerCase();
  if (lower.includes('healthy')) return 'healthy';
  if (lower.includes('foot') || lower.includes('lumpy')) return 'disease';
  return 'warning';
}

function getConfidenceClass(conf) {
  if (conf >= 75) return 'high';
  if (conf >= 50) return 'medium';
  return 'low';
}

function renderResult(container, data) {
  const { prediction, confidence, causes, precautions, medications, foodItems } = data;
  const headerClass = getHeaderClass(prediction);
  const confClass = getConfidenceClass(confidence);
  const isHealthy = prediction.toLowerCase().includes('healthy');

  const causeItems = (causes || []).map(c => `
    <li><span class="li-dot cause">!</span><span>${c}</span></li>
  `).join('');

  const precItems = (precautions || []).map(p => `
    <li><span class="li-dot prec">✓</span><span>${p}</span></li>
  `).join('');

  const medItems = (medications || []).map(m => `
    <li><span class="li-dot med">💊</span><span>${m}</span></li>
  `).join('');

  const foodChips = (foodItems || []).map(f => `
    <span class="food-chip">🌿 ${f}</span>
  `).join('');

  container.innerHTML = `
    <div class="result-header ${headerClass}">
      <div class="result-animal-icon">🩺</div>
      <div class="result-header-text">
        <h2>${isHealthy ? '✅ Animal is Healthy' : '⚠️ ' + prediction + ' Detected'}</h2>
        <p>Cattle · CNN Deep Learning Model · ${new Date().toLocaleTimeString()}</p>
      </div>
      <div class="confidence-pill">
        ${confidence}%
        <span>Confidence</span>
      </div>
    </div>

    <div class="confidence-bar-wrap">
      <label>Model Confidence</label>
      <div class="conf-bar-bg">
        <div class="conf-bar-fill ${confClass}" style="width: 0%" id="confBar"></div>
      </div>
      <div class="conf-percent-label">${confidence}%</div>
    </div>

    <div class="result-info-grid">
      <div class="result-info-box">
        <h4>⚠️ Causes</h4>
        <ul>${causeItems}</ul>
      </div>
      <div class="result-info-box">
        <h4>🛡️ Precautions</h4>
        <ul>${precItems}</ul>
      </div>
      <div class="result-info-box">
        <h4>💊 Medications</h4>
        <ul>${medItems}</ul>
      </div>
    </div>

    <div class="food-row">
      <h4>🌿 Recommended Food & Nutrition</h4>
      <div class="food-chips">${foodChips}</div>
    </div>

    <div class="result-actions">
      <button class="btn-again primary" onclick="analyzeAnother()">🔄 Analyze Another Image</button>
      <a href="/" class="btn-again outline">← Back to Home</a>
    </div>
  `;

  // Animate confidence bar
  setTimeout(() => {
    const bar = document.getElementById('confBar');
    if (bar) bar.style.width = confidence + '%';
  }, 100);
}

function renderError(container, message) {
  container.innerHTML = `
    <div class="error-box">
      <div class="error-icon">❌</div>
      <h3>Analysis Failed</h3>
      <p>${message}</p>
      <button class="btn-again primary" onclick="analyzeAnother()" style="margin-top:16px;">Try Again</button>
    </div>
  `;
}

function analyzeAnother() {
  document.getElementById('fileInput').value = '';
  document.getElementById('previewContainer').style.display = 'none';
  document.getElementById('buttonContainer').style.display = 'none';
  document.getElementById('uploadZone').style.display = 'block';
  document.getElementById('resultSection').style.display = 'none';
  document.getElementById('uploadCard').scrollIntoView({ behavior: 'smooth' });
}
