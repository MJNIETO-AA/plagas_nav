from src.db.connection import get_connection
from src.utils.security import hash_password


def main():
    username = "admin"
    password = "Admin123*"

    conn = get_connection()
    cur = conn.cursor()

    #evitar duplicados
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        print("Ya existe el usuario admin.")

    else:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hash_password(password), "admin")
        )
        conn.commit()
        print("Usuario creado: admin / Admin123*.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()