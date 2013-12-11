DEBUG = True

db_name = "pull"
db_user = "pull"
db_pass = "pull"
#db_host = "yaha.v-find.com"
db_host = "192.168.57.47"
db_host_s = db_host
db_port = "3306"

#COPUS_PATH = '/opt/projects/packages/sougou_corpus'
COPUS_PATH = '/home/gan/download/sogou_copus'

DATABASES = {
    "default": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.mysql",
        # DB name or path to database file if using sqlite3.
        "NAME": db_name,
        # Not used with sqlite3.
        "USER": db_user,
        # Not used with sqlite3.
        "PASSWORD": db_pass,
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": db_host,
        # Set to empty string for default. Not used with sqlite3.
        "PORT": db_port,
    }
}

