// 웹캠 스트림 관리
const webcamState = {
    stream: null,
    videoEl: null,
};

async function startWebcam() {
    const placeholder = document.querySelector(".webcam-placeholder");

    // 이미 <video> 태그가 있으면 재사용, 없으면 생성
    let videoEl = document.getElementById("webcam-video");
    if (!videoEl) {
        videoEl = document.createElement("video");
        videoEl.id = "webcam-video";
        videoEl.autoplay = true;
        videoEl.playsInline = true;
        videoEl.muted = true;
        videoEl.style.cssText = "width:100%;height:100%;object-fit:cover;border-radius:8px;";

        if (placeholder) {
            placeholder.replaceWith(videoEl);
        } else {
            document.querySelector(".webcam-area")?.appendChild(videoEl);
        }
    }
    webcamState.videoEl = videoEl;

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
            audio: false,
        });

        videoEl.srcObject = stream;
        webcamState.stream = stream;
        setWebcamStatus(true);
        return stream;
    } catch (err) {
        console.error("[webcam] 카메라 접근 실패:", err);
        setWebcamStatus(false, err);
        return null;
    }
}

function stopWebcam() {
    if (webcamState.stream) {
        webcamState.stream.getTracks().forEach((track) => track.stop());
        webcamState.stream = null;
    }
    if (webcamState.videoEl) {
        webcamState.videoEl.srcObject = null;
    }
    setWebcamStatus(false);
}

function setWebcamStatus(isOn, err) {
    const dot = document.querySelector(".webcam-status .status-dot.green");
    const label = document.querySelector(".webcam-status .status-label");

    if (!dot || !label) return;

    if (isOn) {
        dot.style.backgroundColor = "#4caf50";
        label.textContent = "카메라 ON";
    } else {
        dot.style.backgroundColor = "#f44336";
        label.textContent = err?.name === "NotAllowedError" ? "카메라 권한 없음" : "카메라 OFF";
    }
}

// 페이지 로드 시 자동 시작
document.addEventListener("DOMContentLoaded", () => {
    startWebcam();
});
