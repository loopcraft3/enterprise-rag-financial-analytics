// One "session" = one visit to the site = one chat.
//
// Every request carries this id (see api.js). The server stores the PDFs you upload
// under it and only searches inside them, so a new visit, a refresh, or "New chat"
// always starts with no documents, and nobody else can see yours.
// The id lives only in memory on purpose: closing or refreshing the page gives you a fresh one.

function makeId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  // Fallback for very old browsers or plain http
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

let sessionId = makeId();

export const getSessionId = () => sessionId;

export const resetSessionId = () => {
  sessionId = makeId();
  return sessionId;
};

// ---------------------------------------------------------------------------
// Is the free server awake?
//
// The free hosting plan puts the server to sleep after about 15 minutes without
// visitors, and the first request afterwards takes up to a minute. We remember when
// the server last answered, and only show the "waking up" note when it may be asleep.
// ---------------------------------------------------------------------------

const AWAKE_FOR_MS = 14 * 60 * 1000;

let lastReplyAt = 0;

export const markServerAwake = () => {
  lastReplyAt = Date.now();
};

export const serverMaybeAsleep = () => Date.now() - lastReplyAt > AWAKE_FOR_MS;
