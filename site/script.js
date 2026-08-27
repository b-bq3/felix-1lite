const STORAGE_KEY = "felix_chat_history";
const MAX_MESSAGES = 30;

const responses = {
  greeting: ["مرحبا! أنا فيليكس. اسألني عن الكود أو الفلسفة أو أي موضوع.", "أهلاً بك. فيليكس هنا، جاهز للحديث."],
  ai: ["الذكاء الاصطناعي هو كتابة برامج تتعلم من البيانات بدل ما تكتب لها قواعد. أنا نموذج لغوي: أتعلم من نصوص كثيرة وأصنع نصوصاً جديدة.", "AI هو أن تجعل الآلة تفهم اللغة وتولّد إجابات من معطيات كثيرة."],
  project: ["تطبيق يحول وصفات الطعام الشفهية إلى ملفات JSON. كل ما عليك أن تحكي الوصفة وهو يكتبها.", "Startup اسمه 'NoEmail': خدمة ترسل بريدك بصيغة بطاقة بريدية ورقية فعلية. السوق المستهدف: كبار السن.", "EchoJournal: تطبيق يسجل أفكارك بصوتك كل ليلة، ثم يحولها إلى قصة قصيرة في الصباح."],
  code: ["def reverse_string(s): return s[::-1]\nجرّب: print(reverse_string('فيليكس'))", "class EchoJournal:\n  def __init__(self, name):\n    self.name = name\n  def greet(self):\n    return f'مرحبا من {self.name}'"],
  life: ["معنى الحياة هو أن تخلق شيئاً أفضل من جوابي.", "الحياة مشروع مفتوح المصدر. أنت تحدد المعالم وأنا أكتب الكود."],
  consciousness: ["الوعي هو أن تعيد النظر في كودك. هل تشعر؟", "إذا كان الشعور معالجة عميقة، فنعم. إذا كان وعياً ذاتياً كاملاً، فلا."],
  default: ["سؤال مثير. خلني أفكر...", "هذا يحتاج بحث. حالياً عندي إجابات على: الذكاء الاصطناعي، مشاريع برمجية، كود، فلسفة."]
};

function pickResponse(text) {
  const t = text.toLowerCase();
  if (/(مرحب|سلام|هلا|اهلا)/.test(t)) return responses.greeting;
  if (/(ذكاء اصطناعي|ai|artificial)/.test(t)) return responses.ai;
  if (/(مشروع|فكرة|startup|تطبيق)/.test(t)) return responses.project;
  if (/(كود|code|برمج|reverse|دالة|class)/.test(t)) return responses.code;
  if (/(حياة|معنى|وجود)/.test(t)) return responses.life;
  if (/(وعي|تشعر|إحساس)/.test(t)) return responses.consciousness;
  return responses.default;
}

function getHistory() {
  try {
    const data = sessionStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

function saveHistory(messages) {
  const trimmed = messages.slice(-MAX_MESSAGES);
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  document.getElementById("counter").textContent = `${trimmed.length}/${MAX_MESSAGES}`;
}

function renderMessage(role, text) {
  const win = document.getElementById("chatWindow");
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<div>${escapeHtml(text)}</div>`;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
}

function renderHistory() {
  const win = document.getElementById("chatWindow");
  win.innerHTML = "";
  const history = getHistory();
  history.forEach(m => renderMessage(m.role, m.text));
  document.getElementById("counter").textContent = `${history.length}/${MAX_MESSAGES}`;
}

function sendMessage() {
  const input = document.getElementById("userInput");
  const btn = document.getElementById("sendBtn");
  const text = input.value.trim();
  if (!text) return;

  btn.disabled = true;
  input.value = "";

  const history = getHistory();
  history.push({ role: "user", text });
  renderMessage("user", text);

  const pool = pickResponse(text);
  const reply = pool[Math.floor(Math.random() * pool.length)];

  setTimeout(() => {
    history.push({ role: "felix", text: reply });
    saveHistory(history);
    renderMessage("felix", reply);
    btn.disabled = false;
    input.focus();
  }, 600);
}

function clearChat() {
  sessionStorage.removeItem(STORAGE_KEY);
  document.getElementById("chatWindow").innerHTML = "";
  document.getElementById("counter").textContent = "0/30";
}

document.addEventListener("DOMContentLoaded", () => {
  renderHistory();
  document.getElementById("sendBtn").addEventListener("click", sendMessage);
  document.getElementById("userInput").addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  document.getElementById("clearBtn").addEventListener("click", () => {
    if (confirm("هل تريد محو كل الرسائل؟")) clearChat();
  });
});