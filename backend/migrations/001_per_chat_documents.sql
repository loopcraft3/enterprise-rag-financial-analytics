-- Hisaab: private documents for every chat.
--
-- Run this ONCE in the Supabase SQL Editor, BEFORE you deploy the new backend.
-- It is safe to run twice.
--
-- What it does:
--   1. Adds session_id to documents (one id per browser visit / chat).
--   2. Replaces "one file name in the whole database" with "one file name per chat",
--      so two visitors can upload files with the same name.
--   3. Adds an index so old documents can be found quickly and cleaned up.
--
-- Documents uploaded before this change get session_id = NULL. No chat can see them,
-- and the backend deletes them (with their PDFs in Storage) at the next upload or
-- keep-alive call, because they are older than DOCUMENT_TTL_HOURS.

alter table public.documents
  add column if not exists session_id text;

-- Drop the old unique rule on filename alone (whatever its name is).
do $$
declare
  c text;
begin
  for c in
    select con.conname
    from pg_constraint con
    where con.conrelid = 'public.documents'::regclass
      and con.contype = 'u'
      and (
        select array_agg(a.attname::text)
        from pg_attribute a
        where a.attrelid = con.conrelid
          and a.attnum = any (con.conkey)
      ) = array['filename']
  loop
    execute format('alter table public.documents drop constraint %I', c);
  end loop;
end
$$;

-- The backend uses: ON CONFLICT (session_id, filename)
create unique index if not exists documents_session_filename_key
  on public.documents (session_id, filename);

create index if not exists documents_created_at_idx
  on public.documents (created_at);
