# pg-port: align psycopg2's JSON handling with MariaDB semantics.
#
# On MariaDB, JSON docfields are LONGTEXT — frappe and mes_euidos receive strings
# and json.loads() them at each call site. psycopg2 auto-deserializes json/
# jsonb columns instead, so those same call sites explode (e.g. frappe's
# validate_link_filters json.loads()-ing an already-parsed list). Registering
# an identity loader makes PG hand back raw strings exactly like MariaDB.
#
# Imported from mes_euidos/__init__.py; harmless when psycopg2 is absent
# (MariaDB-only benches).


def align_pg_json_with_mariadb():
	try:
		from psycopg2.extras import register_default_json, register_default_jsonb
	except ImportError:
		return

	register_default_json(loads=lambda value: value)
	register_default_jsonb(loads=lambda value: value)


align_pg_json_with_mariadb()
