import psycopg2

conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_Uyq5DTodwxL9@ep-odd-surf-adfn168s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    messages JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""")
conn.commit()
cur.close()
conn.close()
print("Table 'conversations' created successfully!")
