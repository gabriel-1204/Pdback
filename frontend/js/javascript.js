const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    const status = document.getElementById("interim-span");
    if (status) status.textContent = "이 브라우저는 음성 인식을 지원하지 않습니다. (Chrome 권장)";
} else {
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "ko-KR";

    let final_transcript = "";

    const final_span = document.getElementById("final-span");
    const interim_span = document.getElementById("interim-span");

    recognition.onresult = function(event) {
        let interim_transcript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                final_transcript += event.results[i][0].transcript;
            } else {
                interim_transcript += event.results[i][0].transcript;
            }
        }

        if (final_span) final_span.textContent = final_transcript;
        if (interim_span) interim_span.textContent = interim_transcript;
    };

    recognition.onerror = function(event) {
        if (interim_span) interim_span.textContent = "오류: " + event.error;
    };

    recognition.onend = function() {
        // 인식이 끊기면 자동 재시작
        recognition.start();
    };

    // 페이지 로드 시 자동 시작
    recognition.start();
}
