// MediaPipe 자세/시선 분석 모듈
// FaceLandmarker(시선) + PoseLandmarker(자세) 로 면접 중 태도를 측정한다.
// isRecording === true 일 때만 카운터에 반영한다.

const WASM_CDN =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm";

// ── 카운터 (세션 전체 누적, 리셋하지 않음) ──
let totalFrames = 0;
let eyeFrames = 0;
let postureFrames = 0;

// ── 임계값 (디버그 패널에서 실시간 조절 가능) ──
let EYE_THRESHOLD = 0.11;
let SHOULDER_Y_THRESHOLD = 0.04;
let HEAD_X_THRESHOLD = 0.03;
let HEAD_TILT_THRESHOLD = 0.05;

// ── 실측값 (디버그 패널 표시용) ──
let debugValues = {
  eyeLeftOffset: 0, eyeRightOffset: 0,
  shoulderDiff: 0, headOffsetX: 0, earDiff: 0,
  eyeOk: false, shoulderOk: false, headXOk: false, tiltOk: false,
  leftEarVis: 0, rightEarVis: 0,
};

// ── DOM 요소 ──
let eyeMeterFill = null;
let postureMeterFill = null;
let eyeRateSpan = null;
let postureRateSpan = null;

// ── MediaPipe 인스턴스 ──
let faceLandmarker = null;
let poseLandmarker = null;
let analysisRunning = false;
let showLandmarks = false;
let landmarkCanvas = null;
let landmarkCtx = null;

// ── 전역 결과 함수 (sound_detection.js에서 호출) ──
function getMediaPipeResults() {
  if (totalFrames === 0) {
    return { eye_contact: 0, posture_safety_rate: 0 };
  }
  return {
    eye_contact: Math.round((eyeFrames / totalFrames) * 100),
    posture_safety_rate: Math.round((postureFrames / totalFrames) * 100),
  };
}

// ── 랜드마크 그리기 ──
// object-fit: contain 보정 — video와 canvas 표시 영역을 일치시킨다
function getContainTransform(video, canvas) {
  const vw = video.videoWidth, vh = video.videoHeight;
  const cw = canvas.clientWidth, ch = canvas.clientHeight;
  const videoRatio = vw / vh;
  const canvasRatio = cw / ch;
  let scale, offsetX = 0, offsetY = 0;
  if (videoRatio > canvasRatio) {
    // 비디오가 더 넓음 → 상하 여백
    scale = cw / vw;
    offsetY = (ch - vh * scale) / 2;
  } else {
    // 비디오가 더 높음 → 좌우 여백
    scale = ch / vh;
    offsetX = (cw - vw * scale) / 2;
  }
  return { scale, offsetX, offsetY };
}

function drawLandmarks(faceLandmarks, poseLandmarksList, video) {
  if (!landmarkCanvas || !landmarkCtx) return;
  const cw = landmarkCanvas.width;
  const ch = landmarkCanvas.height;
  landmarkCtx.clearRect(0, 0, cw, ch);

  const { scale, offsetX, offsetY } = getContainTransform(video, landmarkCanvas);
  const vw = video.videoWidth, vh = video.videoHeight;

  // 정규화 좌표(0~1) → canvas 픽셀 좌표 변환
  const tx = (nx) => nx * vw * scale + offsetX;
  const ty = (ny) => ny * vh * scale + offsetY;

  // scaleX(-1) 보정: canvas도 뒤집혀 있으므로 텍스트를 다시 뒤집어야 함
  function drawLabel(text, x, y) {
    landmarkCtx.save();
    landmarkCtx.scale(-1, 1);
    landmarkCtx.fillText(text, -x - landmarkCtx.measureText(text).width, y);
    landmarkCtx.restore();
  }

  // Face Mesh — 주요 포인트만 (홍채, 눈 꼬리)
  if (faceLandmarks) {
    const facePoints = [468, 473, 33, 133, 263, 362];
    landmarkCtx.fillStyle = "#00ff00";
    for (const idx of facePoints) {
      const p = faceLandmarks[idx];
      if (p) {
        landmarkCtx.beginPath();
        landmarkCtx.arc(tx(p.x), ty(p.y), 3, 0, Math.PI * 2);
        landmarkCtx.fill();
      }
    }
    // 얼굴 윤곽 전체 (작은 점)
    landmarkCtx.fillStyle = "rgba(0,255,0,0.3)";
    for (let i = 0; i < faceLandmarks.length; i++) {
      if (facePoints.includes(i)) continue;
      const p = faceLandmarks[i];
      landmarkCtx.beginPath();
      landmarkCtx.arc(tx(p.x), ty(p.y), 1, 0, Math.PI * 2);
      landmarkCtx.fill();
    }
  }

  // Pose — 주요 포인트 (어깨, 코, 귀)
  if (poseLandmarksList) {
    const poseColors = { 0: "#ff0000", 7: "#ffaa00", 8: "#ffaa00", 11: "#00aaff", 12: "#00aaff" };
    const labels = { 0: "코", 7: "좌귀", 8: "우귀", 11: "좌어깨", 12: "우어깨" };
    for (const [idx, color] of Object.entries(poseColors)) {
      const p = poseLandmarksList[parseInt(idx)];
      if (p && p.visibility > 0.3) {
        const px = tx(p.x), py = ty(p.y);
        landmarkCtx.fillStyle = color;
        landmarkCtx.beginPath();
        landmarkCtx.arc(px, py, 5, 0, Math.PI * 2);
        landmarkCtx.fill();
        landmarkCtx.fillStyle = "#fff";
        landmarkCtx.font = "12px sans-serif";
        drawLabel(labels[idx], px - 7, py - 8);
      }
    }
    // 어깨 연결선
    const ls = poseLandmarksList[11], rs = poseLandmarksList[12];
    if (ls && rs && ls.visibility > 0.3 && rs.visibility > 0.3) {
      landmarkCtx.strokeStyle = "#00aaff";
      landmarkCtx.lineWidth = 2;
      landmarkCtx.beginPath();
      landmarkCtx.moveTo(tx(ls.x), ty(ls.y));
      landmarkCtx.lineTo(tx(rs.x), ty(rs.y));
      landmarkCtx.stroke();
    }
  }
}

// ── 시선 판정 ──
function isLookingStraight(faceLandmarks) {
  // 홍채 중심: 좌 468, 우 473
  // 좌측 눈 꼬리: 33(내측), 133(외측)
  // 우측 눈 꼬리: 362(내측), 263(외측)
  const leftIris = faceLandmarks[468];
  const rightIris = faceLandmarks[473];
  const leftInner = faceLandmarks[133];
  const leftOuter = faceLandmarks[33];
  const rightInner = faceLandmarks[362];
  const rightOuter = faceLandmarks[263];

  // 좌측 눈: 홍채가 눈 중앙에 있는지
  const leftEyeWidth = Math.abs(leftOuter.x - leftInner.x);
  const leftEyeCenter = (leftOuter.x + leftInner.x) / 2;
  const leftOffset = Math.abs(leftIris.x - leftEyeCenter);
  const leftRatio = leftOffset / leftEyeWidth;
  const leftOk = leftRatio < EYE_THRESHOLD;

  // 우측 눈
  const rightEyeWidth = Math.abs(rightOuter.x - rightInner.x);
  const rightEyeCenter = (rightOuter.x + rightInner.x) / 2;
  const rightOffset = Math.abs(rightIris.x - rightEyeCenter);
  const rightRatio = rightOffset / rightEyeWidth;
  const rightOk = rightRatio < EYE_THRESHOLD;

  debugValues.eyeLeftOffset = leftRatio;
  debugValues.eyeRightOffset = rightRatio;
  debugValues.eyeOk = leftOk && rightOk;

  return leftOk && rightOk;
}

// ── 자세 판정 ──
function isPostureStable(poseLandmarks) {
  const leftShoulder = poseLandmarks[11];
  const rightShoulder = poseLandmarks[12];
  const nose = poseLandmarks[0];

  // 어깨가 감지되지 않으면 판정 불가 → false (안정으로 치지 않음)
  if (!leftShoulder || !rightShoulder || !nose) return false;
  if (leftShoulder.visibility < 0.5 || rightShoulder.visibility < 0.5) return false;

  // 어깨 기울기: y좌표 차이
  const shoulderDiff = Math.abs(leftShoulder.y - rightShoulder.y);
  const shoulderOk = shoulderDiff < SHOULDER_Y_THRESHOLD;

  // 머리 좌우 이탈: 코의 x가 양 어깨 중앙 근처인지
  const shoulderCenterX = (leftShoulder.x + rightShoulder.x) / 2;
  const headOffsetX = Math.abs(nose.x - shoulderCenterX);
  const headXOk = headOffsetX < HEAD_X_THRESHOLD;

  // 고개 기울기: 좌귀(7), 우귀(8)로 판정
  const leftEar = poseLandmarks[7];
  const rightEar = poseLandmarks[8];
  let tiltOk = true;
  let earDiffVal = 0;
  if (leftEar && rightEar) {
    debugValues.leftEarVis = leftEar.visibility;
    debugValues.rightEarVis = rightEar.visibility;
    const bothVisible = leftEar.visibility > 0.3 && rightEar.visibility > 0.3;
    if (bothVisible) {
      earDiffVal = Math.abs(leftEar.y - rightEar.y);
      tiltOk = earDiffVal < HEAD_TILT_THRESHOLD;
    } else {
      tiltOk = false;
    }
  }

  debugValues.shoulderDiff = shoulderDiff;
  debugValues.headOffsetX = headOffsetX;
  debugValues.earDiff = earDiffVal;
  debugValues.shoulderOk = shoulderOk;
  debugValues.headXOk = headXOk;
  debugValues.tiltOk = tiltOk;

  return shoulderOk && headXOk && tiltOk;
}

// ── UI 업데이트 (1초 간격) ──
function updateUI() {
  if (totalFrames === 0) return;
  const eyeRate = Math.round((eyeFrames / totalFrames) * 100);
  const postureRate = Math.round((postureFrames / totalFrames) * 100);

  if (eyeMeterFill) eyeMeterFill.style.width = eyeRate + "%";
  if (postureMeterFill) postureMeterFill.style.width = postureRate + "%";
  if (eyeRateSpan) eyeRateSpan.textContent = eyeRate + "%";
  if (postureRateSpan) postureRateSpan.textContent = postureRate + "%";
}

// ── 분석 루프 ──
function analyzeFrame(video) {
  if (!analysisRunning) return;

  const now = performance.now();

  // Face 분석
  let faceLookingStraight = false;
  let curFaceLandmarks = null;
  if (faceLandmarker) {
    try {
      const faceResult = faceLandmarker.detectForVideo(video, now);
      if (faceResult.faceLandmarks && faceResult.faceLandmarks.length > 0) {
        curFaceLandmarks = faceResult.faceLandmarks[0];
        faceLookingStraight = isLookingStraight(curFaceLandmarks);
      }
    } catch (_) { /* 프레임 스킵 */ }
  }

  // Pose 분석
  let poseStable = false;
  let curPoseLandmarks = null;
  if (poseLandmarker) {
    try {
      const poseResult = poseLandmarker.detectForVideo(video, now);
      if (poseResult.landmarks && poseResult.landmarks.length > 0) {
        curPoseLandmarks = poseResult.landmarks[0];
        poseStable = isPostureStable(curPoseLandmarks);
      }
    } catch (_) { /* 프레임 스킵 */ }
  }

  // 랜드마크 그리기
  if (showLandmarks && landmarkCanvas) {
    landmarkCanvas.width = landmarkCanvas.clientWidth;
    landmarkCanvas.height = landmarkCanvas.clientHeight;
    drawLandmarks(curFaceLandmarks, curPoseLandmarks, video);
  }

  // isRecording일 때만 카운터 반영
  if (typeof isRecording !== "undefined" && isRecording) {
    totalFrames++;
    if (faceLookingStraight) eyeFrames++;
    if (poseStable) postureFrames++;
    updateUI();
  }

  // 다음 프레임 예약
  video.requestVideoFrameCallback(() => analyzeFrame(video));
}

// ── 초기화 ──
async function initMediaPipeAnalysis() {
  const video = document.getElementById("webcam");
  if (!video) {
    console.warn("[mediapipe] webcam 요소 없음 — 분석 건너뜀");
    return;
  }

  // DOM 요소 캐싱
  landmarkCanvas = document.getElementById("landmark-canvas");
  if (landmarkCanvas) landmarkCtx = landmarkCanvas.getContext("2d");
  const meters = document.querySelectorAll(".attitude-meter-fill");
  eyeMeterFill = meters[0] || null;
  postureMeterFill = meters[1] || null;
  eyeRateSpan = document.getElementById("eye-rate");
  postureRateSpan = document.getElementById("posture-rate");

  // vision_bundle.mjs 에서 노출되는 전역 객체
  const vision = await window.FilesetResolver.forVisionTasks(WASM_CDN);

  // FaceLandmarker 생성
  try {
    faceLandmarker = await window.FaceLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numFaces: 1,
    });
    console.log("[mediapipe] FaceLandmarker 로드 완료");
  } catch (e) {
    console.error("[mediapipe] FaceLandmarker 로드 실패:", e);
  }

  // PoseLandmarker 생성
  try {
    poseLandmarker = await window.PoseLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numPoses: 1,
    });
    console.log("[mediapipe] PoseLandmarker 로드 완료");
  } catch (e) {
    console.error("[mediapipe] PoseLandmarker 로드 실패:", e);
  }

  // 비디오가 재생 중일 때 분석 루프 시작
  function startLoop() {
    if (analysisRunning) return;
    analysisRunning = true;
    video.requestVideoFrameCallback(() => analyzeFrame(video));
    console.log("[mediapipe] 분석 루프 시작");
  }

  if (video.readyState >= 2) {
    startLoop();
  } else {
    video.addEventListener("loadeddata", startLoop, { once: true });
  }

}

// ── 디버그 패널 ──
function createDebugPanel() {
  const panel = document.createElement("div");
  panel.id = "mp-debug";
  panel.innerHTML = `
    <div id="dbg-handle" style="font-weight:700;padding:10px 0 8px;font-size:13px;cursor:grab;user-select:none;border-bottom:1px solid #444;margin-bottom:8px;">⠿ MediaPipe Debug <span style="float:right;font-size:10px;color:#888;">드래그로 이동</span></div>
    <div class="dbg-section">
      <div class="dbg-title">시선 (EYE_THRESHOLD) 기본: 0.11</div>
      <div class="dbg-hint">높으면 관대 (시선 이탈 허용) / 낮으면 엄격</div>
      <input type="range" min="0.05" max="0.50" step="0.01" value="${EYE_THRESHOLD}" id="dbg-eye">
      <span id="dbg-eye-val">${EYE_THRESHOLD}</span>
      <div class="dbg-live">좌: <span id="dbg-eyeL">-</span> 우: <span id="dbg-eyeR">-</span> <span id="dbg-eyeOk"></span></div>
    </div>
    <div class="dbg-section">
      <div class="dbg-title">어깨 기울기 (SHOULDER_Y) 기본: 0.04</div>
      <div class="dbg-hint">높으면 관대 (기울기 허용) / 낮으면 엄격</div>
      <input type="range" min="0.01" max="0.15" step="0.005" value="${SHOULDER_Y_THRESHOLD}" id="dbg-shoulder">
      <span id="dbg-shoulder-val">${SHOULDER_Y_THRESHOLD}</span>
      <div class="dbg-live">실측: <span id="dbg-shoulderV">-</span> <span id="dbg-shoulderOk"></span></div>
    </div>
    <div class="dbg-section">
      <div class="dbg-title">머리 좌우 (HEAD_X) 기본: 0.03</div>
      <div class="dbg-hint">높으면 관대 (좌우 이탈 허용) / 낮으면 엄격</div>
      <input type="range" min="0.02" max="0.20" step="0.005" value="${HEAD_X_THRESHOLD}" id="dbg-headx">
      <span id="dbg-headx-val">${HEAD_X_THRESHOLD}</span>
      <div class="dbg-live">실측: <span id="dbg-headxV">-</span> <span id="dbg-headxOk"></span></div>
    </div>
    <div class="dbg-section">
      <div class="dbg-title">고개 기울기 (HEAD_TILT) 기본: 0.05</div>
      <div class="dbg-hint">높으면 관대 (고개 꺾기 허용) / 낮으면 엄격</div>
      <input type="range" min="0.02" max="0.25" step="0.005" value="${HEAD_TILT_THRESHOLD}" id="dbg-tilt">
      <span id="dbg-tilt-val">${HEAD_TILT_THRESHOLD}</span>
      <div class="dbg-live">귀 차이: <span id="dbg-tiltV">-</span> 귀vis: <span id="dbg-earVis">-</span> <span id="dbg-tiltOk"></span></div>
    </div>
    <button id="dbg-landmark" style="width:100%;padding:6px;margin-top:8px;border:1px solid #666;background:#333;color:#fff;border-radius:4px;cursor:pointer;font-size:11px;">랜드마크 표시: OFF</button>
    <button id="dbg-copy" style="width:100%;padding:6px;margin-top:4px;border:1px solid #666;background:#333;color:#fff;border-radius:4px;cursor:pointer;font-size:11px;">현재 임계값 복사</button>
    <div id="dbg-copied" style="color:#2ed573;text-align:center;margin-top:4px;display:none;">복사됨!</div>
  `;
  panel.style.cssText = "position:fixed;top:60px;left:50%;transform:translateX(-50%);width:280px;background:rgba(0,0,0,0.9);color:#fff;padding:0 12px 12px;border-radius:8px;font-size:11px;z-index:9999;font-family:monospace;cursor:default;display:none;";

  const style = document.createElement("style");
  style.textContent = `
    #mp-debug .dbg-section { margin-bottom:8px; }
    #mp-debug .dbg-title { color:#aaa;margin-bottom:2px; }
    #mp-debug input[type=range] { width:180px;vertical-align:middle; }
    #mp-debug .dbg-hint { color:#ff9;font-size:10px;margin-bottom:3px; }
    #mp-debug .dbg-live { color:#8f8;margin-top:2px; }
    #mp-debug .pass { color:#2ed573; }
    #mp-debug .fail { color:#ff4757; }
  `;
  document.head.appendChild(style);
  document.body.appendChild(panel);

  // 슬라이더 이벤트
  document.getElementById("dbg-eye").addEventListener("input", e => {
    EYE_THRESHOLD = parseFloat(e.target.value);
    document.getElementById("dbg-eye-val").textContent = EYE_THRESHOLD.toFixed(2);
  });
  document.getElementById("dbg-shoulder").addEventListener("input", e => {
    SHOULDER_Y_THRESHOLD = parseFloat(e.target.value);
    document.getElementById("dbg-shoulder-val").textContent = SHOULDER_Y_THRESHOLD.toFixed(3);
  });
  document.getElementById("dbg-headx").addEventListener("input", e => {
    HEAD_X_THRESHOLD = parseFloat(e.target.value);
    document.getElementById("dbg-headx-val").textContent = HEAD_X_THRESHOLD.toFixed(3);
  });
  document.getElementById("dbg-tilt").addEventListener("input", e => {
    HEAD_TILT_THRESHOLD = parseFloat(e.target.value);
    document.getElementById("dbg-tilt-val").textContent = HEAD_TILT_THRESHOLD.toFixed(3);
  });

  // 드래그 이동
  const handle = document.getElementById("dbg-handle");
  let isDragging = false, dragX = 0, dragY = 0;
  handle.addEventListener("mousedown", (e) => {
    isDragging = true;
    dragX = e.clientX - panel.offsetLeft;
    dragY = e.clientY - panel.offsetTop;
    handle.style.cursor = "grabbing";
    panel.style.transform = "none";
  });
  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    panel.style.left = (e.clientX - dragX) + "px";
    panel.style.top = (e.clientY - dragY) + "px";
  });
  document.addEventListener("mouseup", () => {
    isDragging = false;
    handle.style.cursor = "grab";
  });

  // 랜드마크 토글
  document.getElementById("dbg-landmark").addEventListener("click", () => {
    showLandmarks = !showLandmarks;
    const btn = document.getElementById("dbg-landmark");
    const canvas = document.getElementById("landmark-canvas");
    btn.textContent = "랜드마크 표시: " + (showLandmarks ? "ON" : "OFF");
    btn.style.background = showLandmarks ? "#2ed573" : "#333";
    btn.style.color = showLandmarks ? "#000" : "#fff";
    if (canvas) {
      canvas.style.display = showLandmarks ? "block" : "none";
      if (!showLandmarks && landmarkCtx) landmarkCtx.clearRect(0, 0, canvas.width, canvas.height);
    }
  });

  // 복사 버튼
  document.getElementById("dbg-copy").addEventListener("click", () => {
    const text = [
      `EYE_THRESHOLD = ${EYE_THRESHOLD};`,
      `SHOULDER_Y_THRESHOLD = ${SHOULDER_Y_THRESHOLD};`,
      `HEAD_X_THRESHOLD = ${HEAD_X_THRESHOLD};`,
      `HEAD_TILT_THRESHOLD = ${HEAD_TILT_THRESHOLD};`,
    ].join("\n");
    navigator.clipboard.writeText(text).then(() => {
      const msg = document.getElementById("dbg-copied");
      msg.style.display = "block";
      setTimeout(() => msg.style.display = "none", 1500);
    });
  });

  // 실측값 업데이트 (200ms 간격)
  setInterval(() => {
    const d = debugValues;
    const ok = (v) => v ? '<span class="pass">OK</span>' : '<span class="fail">NG</span>';
    document.getElementById("dbg-eyeL").textContent = d.eyeLeftOffset.toFixed(3);
    document.getElementById("dbg-eyeR").textContent = d.eyeRightOffset.toFixed(3);
    document.getElementById("dbg-eyeOk").innerHTML = ok(d.eyeOk);
    document.getElementById("dbg-shoulderV").textContent = d.shoulderDiff.toFixed(4);
    document.getElementById("dbg-shoulderOk").innerHTML = ok(d.shoulderOk);
    document.getElementById("dbg-headxV").textContent = d.headOffsetX.toFixed(4);
    document.getElementById("dbg-headxOk").innerHTML = ok(d.headXOk);
    document.getElementById("dbg-tiltV").textContent = d.earDiff.toFixed(4);
    document.getElementById("dbg-earVis").textContent = `L:${d.leftEarVis.toFixed(2)} R:${d.rightEarVis.toFixed(2)}`;
    document.getElementById("dbg-tiltOk").innerHTML = ok(d.tiltOk);
  }, 200);
}

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", () => {
  createDebugPanel();

  // 이스터에그: Ctrl+Shift+D로 디버그 패널 토글
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.shiftKey && e.code === "KeyD") {
      e.preventDefault();
      const p = document.getElementById("mp-debug");
      if (p) p.style.display = p.style.display === "none" ? "block" : "none";
    }
  });

  // vision_bundle.mjs 로드 대기 후 초기화
  const waitForVision = setInterval(() => {
    if (window.FilesetResolver && window.FaceLandmarker && window.PoseLandmarker) {
      clearInterval(waitForVision);
      initMediaPipeAnalysis();
    }
  }, 200);

  // 10초 타임아웃 — CDN 로드 실패 시 조용히 포기
  setTimeout(() => clearInterval(waitForVision), 10000);
});
