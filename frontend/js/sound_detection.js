// DOM 요소
const chatMessages = document.querySelector(".chat-messages");
const sessionIdInput = document.getElementById("session-id");
const finalSpan = document.getElementById("final-span");
const interimSpan = document.getElementById("interim-span");
const submitBtn = document.getElementById("submit-btn");

// 음성 인식 상태
let finalTranscript = "";
let isStopped = false;
let recognition = null;

// AI 말풍선을 채팅창에 추가
function addAIBubble(text) {
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble ai";
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 사용자 말풍선을 채팅창에 추가
function addUserBubble(text) {
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble user";
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// STT 텍스트 초기화
function clearTranscript() {
    finalTranscript = "";
    if (finalSpan) finalSpan.textContent = "";
    if (interimSpan) interimSpan.textContent = "";
}

// 면접 시작 → 첫 질문 받아오기
async function startInterview() {
    // localStorage에서 값 읽기
    const jobRole = localStorage.getItem("job_role") ?? "백엔드";
    const techStack = JSON.parse(localStorage.getItem("tech_stack") ?? '["Python"]');
    const experienceYears = parseInt(localStorage.getItem("experience_years") ?? "0");

try {
    const res = await fetch("/api/v1/interview/start", {
        method: "POST",
        headers: { "Content-Type": "application/json",
             "Authorization": `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
            job_role: jobRole,
            tech_stack: techStack,
            experience_years: experienceYears})
        });
    if (!res.ok) {
        addAIBubble("면접을 시작할 수 없습니다. 페이지를 새로고침 해주세요.");
        return;
    } 
    const data = await res.json();
    sessionIdInput.value = data.session_id;
    addAIBubble(data.intro_message);
    addAIBubble(data.question);
    
    } catch (e) {
    addAIBubble("서버에 연결할 수 없습니다. 네트워크를 확인해주세요.");
    }
}

// 완료 버튼 → 답변 제출 후 꼬리질문 받기
if (submitBtn) {
    submitBtn.addEventListener("click", async () => {
        if (!finalTranscript.trim()) return;

        try {
        const answerText = finalTranscript;
        addUserBubble(answerText);
        clearTranscript();

        const res = await fetch("/api/v1/interview/answer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionIdInput.value,
                answer_content: answerText,
            })
        });
        if (!res.ok) {
            addAIBubble("답변 제출에 실패했습니다. 다시 시도해주세요.");
            return;
        }
        const data = await res.json();

        if (data.is_finished) {
            addAIBubble("면접이 종료되었습니다. 수고하셨습니다!");
            isStopped = true;
            if (recognition) {recognition.stop();}
        } else {
            addAIBubble(data.follow_up_question);
        }
    } catch (e) {
        addAIBubble("서버에 연결할 수 없습니다. 네트워크를 확인해주세요.")
    }
    });
}

// 음성 인식 설정
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    if (interimSpan) interimSpan.textContent = "이 브라우저는 음성 인식을 지원하지 않습니다. (Chrome 권장)";
} else {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "ko-KR";

    recognition.onresult = function(event) {
        let interimTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }

        if (finalSpan) finalSpan.textContent = finalTranscript;
        if (interimSpan) interimSpan.textContent = interimTranscript;
    };

    recognition.onerror = function(event) {
        if (interimSpan){
            interimSpan.textContent = "오류: " + event.error;
            isStopped = true;}
    };

    recognition.onend = function() {
        if (!isStopped){
            recognition.start();}
    };

    recognition.start();
}

startInterview();
