# Hisaab evaluation

A small, repeatable test: ask questions with known answers about one PDF and check the answer, the page citation, and that questions outside the document are refused.

## Set up
1. Pick a public PDF (for example a company's quarterly filing).
2. Edit `questions.json`. Each question has:
   - `question`: what to ask
   - `expect`: a list of acceptable values (any one must appear in the answer; commas and spaces are ignored)
   - `file` and `page`: the file name and the **1-based page** where the answer is (optional, but needed for the citation check)
   - `answerable`: `false` for questions the PDF cannot answer (the app must refuse)
3. Aim for 20 or more questions: lookups, calculations, and a few out-of-document questions.

## Run
```bash
cd backend && uvicorn main:app          # in one terminal
python eval/run_eval.py --pdf path/to/file.pdf
```
Copy the printed table into the main README, and add the date you ran it.

The script waits about 11 seconds between questions because the backend allows 6 chats per minute.
