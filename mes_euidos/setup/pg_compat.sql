-- MariaDB compatibility layer for ERPNext on PostgreSQL (euidos pg-port).
--
-- ERPNext raw SQL leans on MySQL/MariaDB builtins that PostgreSQL lacks.
-- Rewriting every call site would make upstream rebases painful; instead the
-- missing builtins are defined here (schema `public`) and installed into every
-- postgres site (hooks: before_install / after_migrate -> setup_pg_compat).
--
-- Design constraints:
-- * frappe's psycopg2 layer passes ALL parameters as strings ("unknown"
--   literals to the PG type resolver), so each name gets ONE overload with
--   timestamp/text args (unknown coerces cleanly; multiple overloads would be
--   ambiguous). date columns coerce date->timestamp implicitly.
-- * Everything is CREATE OR REPLACE / idempotent: re-running is always safe.
-- * MySQL semantics are matched only as far as ERPNext uses them; constructs
--   that differ at the parser level (GROUP_CONCAT ... SEPARATOR, TIMESTAMPDIFF,
--   INTERVAL 5 DAY literals, ON DUPLICATE KEY) are fixed at the call site.

-- IFNULL(a, b): coalesce with MySQL-ish type mixing.
CREATE OR REPLACE FUNCTION ifnull(anycompatible, anycompatible)
RETURNS anycompatible LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT COALESCE($1, $2)';

-- IF(cond, a, b): MySQL conditional. Two overloads: boolean conditions
-- (comparisons) and numeric conditions (MySQL truthiness: non-zero = true).
-- 'IF' is not a reserved word in the PG grammar, so the call form parses.
CREATE OR REPLACE FUNCTION if(boolean, anycompatible, anycompatible)
RETURNS anycompatible LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT CASE WHEN $1 THEN $2 ELSE $3 END';

CREATE OR REPLACE FUNCTION if(numeric, anycompatible, anycompatible)
RETURNS anycompatible LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT CASE WHEN $1 IS NOT NULL AND $1 <> 0 THEN $2 ELSE $3 END';

-- CURDATE(): current date.
CREATE OR REPLACE FUNCTION curdate()
RETURNS date LANGUAGE sql STABLE PARALLEL SAFE
AS 'SELECT CURRENT_DATE';

-- DATEDIFF(a, b): whole days a - b (MySQL ignores time parts).
CREATE OR REPLACE FUNCTION datediff(timestamp, timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT ($1::date - $2::date)';

-- DATE_ADD/DATE_SUB(ts, interval): MySQL returns date for date input, but
-- timestamp is comparison-compatible everywhere ERPNext uses the result.
-- NOTE: pg16+ ships date_add(timestamptz, interval); this overload on plain
-- timestamp wins for date/timestamp/unknown args.
CREATE OR REPLACE FUNCTION date_add(timestamp, interval)
RETURNS timestamp LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT $1 + $2';

CREATE OR REPLACE FUNCTION date_sub(timestamp, interval)
RETURNS timestamp LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT $1 - $2';

-- TO_DAYS(d): days since year 0 (MySQL day-number epoch; the +366 aligns
-- PG's 0001-01-01 origin with MySQL's imaginary year 0).
CREATE OR REPLACE FUNCTION to_days(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT ($1::date - DATE '0001-01-01') + 366 $$;

-- LAST_DAY(d): last day of the month of d.
CREATE OR REPLACE FUNCTION last_day(timestamp)
RETURNS date LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT (date_trunc('month', $1) + INTERVAL '1 month - 1 day')::date $$;

-- Calendar-part extractors MySQL exposes as bare functions.
CREATE OR REPLACE FUNCTION year(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(year FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION month(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(month FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION day(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(day FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION hour(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(hour FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION minute(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(minute FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION second(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT FLOOR(EXTRACT(second FROM $1))::integer $$;

CREATE OR REPLACE FUNCTION quarter(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(quarter FROM $1)::integer $$;

-- WEEK(d): MySQL default mode 0 (Sunday-start, 0..53). ERPNext only buckets
-- rows by week, so ISO week is an accepted, documented deviation.
CREATE OR REPLACE FUNCTION week(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(week FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION monthname(timestamp)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT to_char($1, 'FMMonth') $$;

-- DAYOFWEEK(d): 1 = Sunday ... 7 = Saturday (MySQL ODBC numbering).
CREATE OR REPLACE FUNCTION dayofweek(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(dow FROM $1)::integer + 1 $$;

CREATE OR REPLACE FUNCTION dayofyear(timestamp)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(doy FROM $1)::integer $$;

-- UNIX_TIMESTAMP(ts) / FROM_UNIXTIME(n)
CREATE OR REPLACE FUNCTION unix_timestamp(timestamp)
RETURNS bigint LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT FLOOR(EXTRACT(epoch FROM $1))::bigint $$;

CREATE OR REPLACE FUNCTION from_unixtime(double precision)
RETURNS timestamp LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT to_timestamp($1)::timestamp $$;

-- TRUNCATE(x, d): numeric truncation (PG spells it trunc).
CREATE OR REPLACE FUNCTION truncate(numeric, integer)
RETURNS numeric LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT trunc($1, $2)';

-- INSTR(str, sub)
CREATE OR REPLACE FUNCTION instr(text, text)
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT strpos($1, $2)';

-- GROUP_CONCAT(x): comma separator, NULLs skipped, no inline ORDER/SEPARATOR
-- (call sites using SEPARATOR are rewritten - parser-level syntax).
CREATE OR REPLACE FUNCTION _group_concat_step(text, text)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$ SELECT CASE WHEN $2 IS NULL THEN $1
             WHEN $1 IS NULL THEN $2
             ELSE $1 || ',' || $2 END $$;

CREATE OR REPLACE AGGREGATE group_concat(text) (
  SFUNC = _group_concat_step,
  STYPE = text,
  PARALLEL = SAFE
);

-- TIMEDIFF(a, b): MySQL returns TIME; an interval compares/renders the same
-- everywhere ERPNext consumes it.
CREATE OR REPLACE FUNCTION timediff(timestamp, timestamp)
RETURNS interval LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT $1 - $2';

-- FIELD(x, a, b, ...): 1-based position of x in the list, 0 when absent.
CREATE OR REPLACE FUNCTION field(text, VARIADIC text[])
RETURNS integer LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT COALESCE(array_position($2, $1), 0)';

-- timestamptz overloads: now() yields timestamptz, and PG does not implicitly
-- cast timestamptz->timestamp during function resolution. timestamptz is the
-- datetime category's preferred type, so unknown-literal args land here and
-- typed timestamp columns still hit the exact overloads above — no ambiguity.
CREATE OR REPLACE FUNCTION datediff(timestamptz, timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS 'SELECT ($1::date - $2::date)';

CREATE OR REPLACE FUNCTION date_add(timestamptz, interval)
RETURNS timestamptz LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT $1 + $2';

CREATE OR REPLACE FUNCTION date_sub(timestamptz, interval)
RETURNS timestamptz LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT $1 - $2';

CREATE OR REPLACE FUNCTION timediff(timestamptz, timestamptz)
RETURNS interval LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS 'SELECT $1 - $2';

CREATE OR REPLACE FUNCTION to_days(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT ($1::date - DATE '0001-01-01') + 366 $$;

CREATE OR REPLACE FUNCTION last_day(timestamptz)
RETURNS date LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT (date_trunc('month', $1) + INTERVAL '1 month - 1 day')::date $$;

CREATE OR REPLACE FUNCTION year(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(year FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION month(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(month FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION day(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(day FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION hour(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(hour FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION minute(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(minute FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION week(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(week FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION quarter(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(quarter FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION monthname(timestamptz)
RETURNS text LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT to_char($1, 'FMMonth') $$;

CREATE OR REPLACE FUNCTION dayofweek(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(dow FROM $1)::integer + 1 $$;

CREATE OR REPLACE FUNCTION dayofyear(timestamptz)
RETURNS integer LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT EXTRACT(doy FROM $1)::integer $$;

CREATE OR REPLACE FUNCTION unix_timestamp(timestamptz)
RETURNS bigint LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT FLOOR(EXTRACT(epoch FROM $1))::bigint $$;

-- DATE_FORMAT(ts, fmt): translate MySQL format tokens to to_char() templates.
-- Covers the token set ERPNext uses; unknown %x tokens pass through literally.
CREATE OR REPLACE FUNCTION date_format(ts timestamp, fmt text)
RETURNS text LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE
AS $fn$
DECLARE
  i int := 1;
  n int := length(fmt);
  c text;
  tok text;
  tpl text := '';
  lit text := '';
BEGIN
  WHILE i <= n LOOP
    c := substr(fmt, i, 1);
    IF c = '%' AND i < n THEN
      tok := substr(fmt, i + 1, 1);
      -- flush pending literal, double-quoted so to_char keeps it verbatim
      IF lit <> '' THEN
        tpl := tpl || '"' || replace(lit, '"', '""') || '"';
        lit := '';
      END IF;
      tpl := tpl || CASE tok
        WHEN 'Y' THEN 'YYYY'  WHEN 'y' THEN 'YY'
        WHEN 'm' THEN 'MM'    WHEN 'c' THEN 'FMMM'
        WHEN 'd' THEN 'DD'    WHEN 'e' THEN 'FMDD'
        WHEN 'H' THEN 'HH24'  WHEN 'k' THEN 'FMHH24'
        WHEN 'h' THEN 'HH12'  WHEN 'l' THEN 'FMHH12'
        WHEN 'i' THEN 'MI'
        WHEN 'S' THEN 'SS'    WHEN 's' THEN 'SS'
        WHEN 'p' THEN 'AM'
        WHEN 'M' THEN 'FMMonth' WHEN 'b' THEN 'Mon'
        WHEN 'W' THEN 'FMDay'   WHEN 'a' THEN 'Dy'
        WHEN 'D' THEN 'FMDDth'
        WHEN 'j' THEN 'DDD'
        WHEN 'f' THEN 'US'
        WHEN 'r' THEN 'HH12:MI:SS AM'
        WHEN 'T' THEN 'HH24:MI:SS'
        WHEN 'v' THEN 'IW'    WHEN 'u' THEN 'WW'
        WHEN '%' THEN '"%"'
        ELSE '"%' || tok || '"'
      END;
      i := i + 2;
    ELSE
      lit := lit || c;
      i := i + 1;
    END IF;
  END LOOP;
  IF lit <> '' THEN
    tpl := tpl || '"' || replace(lit, '"', '""') || '"';
  END IF;
  RETURN to_char(ts, tpl);
END
$fn$;
