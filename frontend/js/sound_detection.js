// 로그인 체크
if (!localStorage.getItem('access_token')) {
    alert('로그인이 필요합니다.');
    window.location.href = '/login';
}

// DOM 요소
const chatMessages = document.querySelector(".chat-messages");
const sessionIdInput = document.getElementById("session-id");
const finalSpan = document.getElementById("final-span");
const interimSpan = document.getElementById("interim-span");
const toggleBtn = document.getElementById("toggle-btn");
const nextSessionBtn = document.getElementById("next-session-btn");
const sttDot = document.getElementById("stt-dot");
const sttLabel = document.getElementById("stt-label");

// 음성 인식 상태
let finalTranscript = "";
let isRecording = false;
let isFinished = false;
let isSubmitting = false;
let recognition = null;
let questionNumber = 0;
let followUpCount = 0;

// 답변 타이머 (isRecording일 때만 누적)
let timerSeconds = 0;
let timerInterval = null;
const timerBadge = document.querySelector(".timer-badge");

function updateTimerDisplay() {
    const m = String(Math.floor(timerSeconds / 60)).padStart(2, "0");
    const s = String(timerSeconds % 60).padStart(2, "0");
    if (timerBadge) timerBadge.textContent = `⏱ ${m}:${s}`;
}

function startTimer() {
    if (timerInterval) return;
    timerInterval = setInterval(() => {
        timerSeconds++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}
const MAX_QUESTIONS = 5;
const questionCounter = document.querySelector(".chat-header span");

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

// 질문 카운트 업데이트
function updateQuestionCount() {
    questionNumber++;
    if (questionCounter) questionCounter.textContent = `질문 ${questionNumber}/${MAX_QUESTIONS}`;
}

// 마이크 상태 UI 업데이트
function updateMicUI(recording) {
    if (sttDot) {
        sttDot.className = recording ? "status-dot red" : "status-dot";
    }
    if (sttLabel) {
        sttLabel.textContent = recording ? "녹음 중" : "마이크 OFF";
    }
    if (toggleBtn) {
        toggleBtn.textContent = recording ? "답변 완료" : "답변 시작";
        toggleBtn.className = recording ? "btn-danger" : "btn-primary";
    }
}

// 답변 제출
async function submitAnswer() {
    if (!finalTranscript.trim() || isSubmitting) return;
    isSubmitting = true;

    try {
        const answerText = finalTranscript;
        addUserBubble(answerText);
        clearTranscript();

        if (toggleBtn) toggleBtn.disabled = true;

        const bodyData = {
            session_id: sessionIdInput.value,
            answer_content: answerText,
        };
        // 마지막 질문일 때 MediaPipe 태도 분석 데이터 포함
        if (questionNumber >= MAX_QUESTIONS && typeof getMediaPipeResults === "function") {
            const mp = getMediaPipeResults();
            bodyData.eye_contact = mp.eye_contact;
            bodyData.posture_safety_rate = mp.posture_safety_rate;
        }

        const res = await authFetch("/api/v1/interview/answer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bodyData)
        });
        if (!res) return;

        if (!res.ok) {
            addAIBubble("답변 제출에 실패했습니다. 다시 시도해주세요.");
            if (toggleBtn) toggleBtn.disabled = false;
            return;
        }

        const data = await res.json();

if (data.is_finished) {
    isFinished = true;
    if (toggleBtn) toggleBtn.disabled = true;
    stopTimer();

    const modal = document.getElementById("session-modal");
    const modalTitle = document.getElementById("session-modal-title");
    const modalDesc = document.getElementById("session-modal-desc");

    addAIBubble("면접이 종료되었습니다. 수고하셨습니다!");
    if (modalTitle) modalTitle.textContent = "면접 종료!";
    if (modalDesc) modalDesc.textContent = "수고하셨습니다!";
    if (nextSessionBtn) nextSessionBtn.textContent = "히스토리로 이동";
    const feedbackBtn = document.getElementById("feedback-btn");
    if (feedbackBtn) feedbackBtn.style.display = "block";
    if (modal) modal.style.display = "flex";
    if (nextSessionBtn) nextSessionBtn.disabled = false;
} else {
            addAIBubble(data.follow_up_question);
            followUpCount++;
            updateQuestionCount();
            if (toggleBtn) toggleBtn.disabled = false;
        }
    } catch (e) {
        addAIBubble("서버에 연결할 수 없습니다. 네트워크를 확인해주세요.");
        if (toggleBtn) toggleBtn.disabled = false;
    } finally {
        isSubmitting = false;
        clearTranscript();
    }
}

// 녹음 시작/중지 토글
function toggleRecording() {
    if (isFinished || isSubmitting) return;
    
    if (!recognition) {
        addAIBubble("이 브라우저는 음성 인식을 지원하지 않습니다. Chrome을 사용해주세요.");
        return;
    }

    if (!isRecording) {
        // OFF → ON: 녹음 시작
        clearTranscript();
        recognition.start();
        isRecording = true;
        updateMicUI(true);
        startTimer();

    } else {
        // ON → OFF: 녹음 중지 + 답변 제출
        // interim 텍스트가 final로 확정되기 전에 멈출 수 있으므로 합산
        if (interimSpan && interimSpan.textContent.trim()) {
            finalTranscript += interimSpan.textContent;
            interimSpan.textContent = "";
        }
        recognition.stop();
        isRecording = false;
        updateMicUI(false);
        stopTimer();
        submitAnswer();
    }
}

// 토글 버튼 클릭 이벤트
if (toggleBtn) {
    toggleBtn.addEventListener("click", toggleRecording);
}

// 버튼 이벤트 등록부
if (nextSessionBtn) {
    nextSessionBtn.addEventListener("click", async function () {
        nextSessionBtn.disabled = true;
        nextSessionBtn.textContent = "피드백 저장 중...";

        try {
            await authFetch("/api/v1/feedback/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionIdInput.value })
            });
        } catch (e) {
            // 피드백 저장 실패해도 이동은 진행
        }

        window.location.href = '/history';
    });
}


// 피드백 버튼 이벤트
const feedbackBtn = document.getElementById("feedback-btn");
if (feedbackBtn) {
    feedbackBtn.addEventListener("click", async function () {
        feedbackBtn.disabled = true;
        feedbackBtn.textContent = "피드백 생성 중...";

        try {
            const res = await authFetch("/api/v1/feedback/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionIdInput.value })
            });
            if (res && !res.ok && res.status !== 409) {
                alert("피드백 생성에 실패했습니다. 히스토리에서 다시 시도해주세요.");
            }
        } catch (e) {
            alert("피드백 생성 중 오류가 발생했습니다.");
        }

        window.location.href = `/feedback?id=${sessionIdInput.value}`;
    });
}

// 스페이스바 단축키
document.addEventListener("keydown", function(e) {
    if (e.code === "Space" && e.target === document.body) {
        e.preventDefault();
        toggleRecording();
    }
});

// 면접 시작 → 첫 질문 받아오기
async function startInterview() {
    const jobRole = localStorage.getItem("job_role") ?? "백엔드";
    let techStack;
    try {
        techStack = JSON.parse(localStorage.getItem("tech_stack") ?? '["Python"]');
    } catch {
        techStack = ["Python"];
    }
    const experienceYears = parseInt(localStorage.getItem("experience_years") ?? "0");

    try {
        const res = await authFetch("/api/v1/interview/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                job_role: jobRole,
                tech_stack: techStack,
                experience_years: experienceYears
            })
        });
        if (!res) return;

        if (!res.ok) {
            addAIBubble("면접을 시작할 수 없습니다. 페이지를 새로고침 해주세요.");
            return;
        }

        const data = await res.json();
        if (sessionIdInput) sessionIdInput.value = data.session_id;
        addAIBubble(data.intro_message);
        addAIBubble(data.question);
        updateQuestionCount();

        // 첫 질문 받은 후 버튼 활성화
        if (toggleBtn) toggleBtn.disabled = false;
    } catch (e) {
        console.error("startInterview 에러:", e);
        addAIBubble("서버에 연결할 수 없습니다. 네트워크를 확인해주세요.");
    }
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
        if (!isRecording) return;
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
        // 복구 가능한 에러는 무시
        if (["no-speech", "network", "aborted"].includes(event.error)) return;
        // 치명적 에러 (마이크 권한 거부 등)
        isRecording = false;
        updateMicUI(false);
        if (interimSpan) interimSpan.textContent = "마이크 오류: " + event.error;
    };

    recognition.onend = function() {
        // 녹음 중에 브라우저가 자동 종료한 경우 재시작
        if (isRecording) recognition.start();
    };
}

startInterview();
