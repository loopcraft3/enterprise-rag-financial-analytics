// Chat history, saved ONLY in this browser (localStorage).
//
// Nothing here is sent to the server. We save the questions, the answers and which
// pages they came from, but never the PDFs themselves. So an old chat can be read again,
// and to ask new questions the person uploads the PDF again.
//
// localStorage can be empty, full or blocked (private window), so every call is wrapped
// in try/catch and the app works fine without it.

const KEY = "hisaab-history-v1";
const MAX_CHATS = 30;

function read() {
  try {
    const raw = localStorage.getItem(KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function write(list) {
  // If the browser's storage is full, drop the oldest chat and try again.
  let items = list;
  for (;;) {
    try {
      localStorage.setItem(KEY, JSON.stringify(items));
      return items;
    } catch {
      if (items.length === 0) return items; // storage blocked: nothing more we can do
      items = items.slice(0, -1);
    }
  }
}

// Newest first
export function loadHistory() {
  return read().sort((a, b) => b.updatedAt - a.updatedAt);
}

export function newChatId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function makeTitle(messages) {
  const first = messages.find((m) => m.role === "user");
  const text = (first?.content || "New chat").replace(/\s+/g, " ").trim();
  return text.length > 60 ? text.slice(0, 57) + "…" : text;
}

// Keep only what is needed to show the chat again.
function slim(messages) {
  return messages.map((m) => ({
    role: m.role,
    content: m.content,
    ...(m.sources
      ? { sources: m.sources.map((s) => ({ source: s.source, page: s.page })) }
      : {}),
  }));
}

export function saveChat({ id, messages, files }) {
  if (!id || messages.length === 0) return loadHistory();

  const list = read().filter((c) => c.id !== id);
  const existing = read().find((c) => c.id === id);

  list.push({
    id,
    title: makeTitle(messages),
    createdAt: existing?.createdAt || Date.now(),
    updatedAt: Date.now(),
    files: files || [],
    messages: slim(messages),
  });

  list.sort((a, b) => b.updatedAt - a.updatedAt);
  write(list.slice(0, MAX_CHATS));
  return loadHistory();
}

export function deleteChat(id) {
  write(read().filter((c) => c.id !== id));
  return loadHistory();
}

export function clearHistory() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
  return [];
}
