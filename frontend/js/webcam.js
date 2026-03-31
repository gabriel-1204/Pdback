// 웹캠 스트림 연결
async function startWebcam() {
    const video = document.getElementById("webcam");
    if (!video) return null;

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        return stream;
    } catch (err) {
        console.error("[webcam] 카메라 접근 실패:", err);
        return null;
    }
}

// 페이지 로드 시 자동 시작
document.addEventListener("DOMContentLoaded", async () => {
    const result = await navigator.permissions.query({ name: 'camera' });
    if (result.state === 'granted') {
        startWebcam();
    }
});
