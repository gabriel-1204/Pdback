const video = document.getElementById("webcam");
const stream = await navigator.mediaDevices.getUserMedia({ video: true });
video.srcObject = stream;

const eyeRate = totalFrames > 0
  ? (eyeFrames / totalFrames * 100)
  : 0;
// attitude-meter-fill의 width와 텍스트 업데이트