import streamlit as st
import sqlite3
import hashlib

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users 
        (username TEXT PRIMARY KEY, password TEXT)
    ''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def add_userdata(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users(username,password) VALUES (?,?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username =? AND password =?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

# --- UI LOGIC ---
def main():
    init_db()
    st.title("StudySimplifier ✨")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login Section")

        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(username, check_hashes(password, hashed_pswd))
            
            if result:
                st.success(f"Welcome back, {username}! 👋")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                # Redirect to main features here
                st.info("You can now access the Study Tools in the sidebar!")
            else:
                st.error("Invalid Username or Password. Please try again.")

    elif choice == "Register":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Register"):
            if new_user and new_password:
                hashed_new_password = make_hashes(new_password)
                if add_userdata(new_user, hashed_new_password):
                    st.success("Account created successfully! 🎉")
                    st.info("Go to Login Menu to login")
                else:
                    st.warning("Username already exists. Try a different one.")
            else:
                st.error("Please fill in both fields.")

if __name__ == '__main__':
    main()
