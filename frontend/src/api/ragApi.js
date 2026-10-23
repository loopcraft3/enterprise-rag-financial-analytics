import api from "./api";

export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload", formData);

  return response.data;
}


export async function sendMessage(question, conversationId=null) {
  const response = await api.post("/chat", {
    conversation_id: conversationId,
    question,
  });

  return response.data;
}



export async function getDocuments() {
  const response = await api.get("/documents");

  return response.data;
}

export async function deleteDocument(filename) {
  const response = await api.delete(`/documents/${filename}`);

  return response.data;
}