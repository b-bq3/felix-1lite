import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.2/dist/transformers.min.js';

env.allowLocalModels = false;
env.useBrowserCache = true;

const STORAGE_KEY = "felix_chat_history";
const MAX_MESSAGES = 30;
const MODEL_ID = "Xenova/distilgpt2";

let generator = null;

const statusEl = document.getElementById("status");
const statusText = document.getElementById("statusText");
const chatWindow = document.getElementById("chatWindow");
const inputRow = document.getElementById("inputRow");
const controls = document.getElementById("controls");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const counter = document.getElementById("counter");

async function loadModel() {
  try {
    statusText.textContent = "جاري تحميل DistilGPT-2 من HuggingFace Hub... (~82 MB)";
    generator = await pipeline('text-generation', MODEL_ID, { dtype: 'q8' });
    statusEl.classList.remove("loading");
    statusEl.classList.add("ready");
    statusText.innerHTML = "✅ النموذج جاهز! اكتب أي شيء بالإنجليزية";
    chatWindow.style.display = "block";
    inputRow.style.display = "flex";
    controls.style.display = "flex";
    renderHistory();
    userInput.focus();
  } catch (e) {
    statusText.innerHTML = "❌ خطأ في التحميل: " + e.message + ". تحقق من اتصال الإنترنت.";
    console.error(e);
  }
}

function getHistory() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveHistory(messages) {
  const trimmed = messages.slice(-MAX_MESSAGES);
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  counter.textContent = `${trimmed.length}/${MAX_MESSAGES}`;
}

function renderMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<div>${escapeHtml(text)}</div>`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>");
}

function renderHistory() {
  chatWindow.innerHTML = "";
  getHistory().forEach(m => renderMessage(m.role, m.text));
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || !generator) return;

  sendBtn.disabled = true;
  userInput.value = "";

  const history = getHistory();
  history.push({ role: "user", text });
  renderMessage("user", text);
  saveHistory(history);

  const thinking = document.createElement("div");
  thinking.className = "msg felix";
  thinking.innerHTML = `<div class="thinking">يفكّر...</div>`;
  chatWindow.appendChild(thinking);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const prompt = buildPrompt(text, history);
    const out = await generator(prompt, {
      max_new_tokens: 60,
      temperature: 0.9,
      do_sample: true,
      top_k: 50,
      repetition_penalty: 1.3,
      return_full_text: false
    });
    let reply = out[0].generated_text.trim();
    reply = reply.split(/\n/)[0];
    if (reply.length > 300) reply = reply.slice(0, 300) + "...";

    thinking.querySelector(".thinking").textContent = reply;
    history.push({ role: "felix", text: reply });
    saveHistory(history);
  } catch (e) {
    thinking.querySelector(".thinking").textContent = "خطأ: " + e.message;
    console.error(e);
  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
}

function buildPrompt(text, history) {
  const recent = history.slice(-6);
  let prompt = "";
  recent.forEach(m => {
    if (m.role === "user") prompt += `User: ${m.text}\n`;
    else prompt += `Bot: ${m.text}\n`;
  });
  prompt += `User: ${text}\nBot:`;
  return prompt;
}

function clearChat() {
  if (!confirm("محوك كل الرسائل؟")) return;
  sessionStorage.removeItem(STORAGE_KEY);
  chatWindow.innerHTML = "";
  counter.textContent = "0/30";
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
clearBtn.addEventListener("click", clearChat);

loadModel();