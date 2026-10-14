-- Sarob uchun FAQAT O'QISH huquqli foydalanuvchi (nigoh bazasi)
\set ON_ERROR_STOP on
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sarob_ro') THEN
    CREATE ROLE sarob_ro LOGIN PASSWORD '<SAROB_RO_PAROLI>';
  ELSE
    ALTER ROLE sarob_ro LOGIN PASSWORD '<SAROB_RO_PAROLI>';
  END IF;
END $$;
ALTER ROLE sarob_ro SET default_transaction_read_only = on;   -- yozish taqiqlanadi
ALTER ROLE sarob_ro SET statement_timeout = '20s';            -- og'ir so'rovlar to'xtatiladi
ALTER ROLE sarob_ro CONNECTION LIMIT 5;
GRANT CONNECT ON DATABASE nigoh TO sarob_ro;
GRANT USAGE ON SCHEMA public TO sarob_ro;
-- Faqat maxfiy bo'lmagan jadval va ustunlarga SELECT
DO $$ DECLARE t record; cols text; BEGIN
  FOR t IN SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public' AND table_type IN ('BASE TABLE', 'VIEW') LOOP
    IF t.table_name ~* '(admin|session|token|secret|credential|password|auth|user)' THEN CONTINUE; END IF;
    SELECT string_agg(quote_ident(column_name), ',') INTO cols FROM information_schema.columns
     WHERE table_schema = 'public' AND table_name = t.table_name
       AND column_name !~* '(pass|pwd|secret|token|hash|salt|key|credential|username|login|stream_url|rtsp_url|_enc$)';
    IF cols IS NOT NULL THEN
      EXECUTE format('GRANT SELECT (%s) ON public.%I TO sarob_ro', cols, t.table_name);
    END IF;
  END LOOP;
END $$;
-- Natija: sarob_ro ko'ra oladigan jadvallar va ustunlar soni
SELECT table_name AS jadval, count(*) AS ustunlar FROM information_schema.column_privileges
 WHERE grantee = 'sarob_ro' AND privilege_type = 'SELECT' GROUP BY 1 ORDER BY 1;
