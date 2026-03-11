import streamlit as st
import cv2
import numpy as np
import os

from database import init_db, get_connection
from face_utils import get_face_encoding, encode_to_blob, decode_blob, compare_faces
from attendance import mark_attendance

init_db()

st.title("Face Attendance System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Register User", "Take Attendance"]
)

if menu == "Register User":
    st.header("Register New User")

    name = st.text_input("Name")
    roll = st.text_input("Roll Number")

    picture = st.camera_input("Take Photo")

    if st.button("Register"):
        if picture is None:
            st.error("Take photo first")
        else:
            bytes_data = picture.getvalue()
            np_img = np.frombuffer(bytes_data, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            encoding = get_face_encoding(rgb)

            if encoding is None:
                st.error("Face not detected")
            else:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO users(name,roll,encoding) VALUES(?,?,?)",
                    (name, roll, encode_to_blob(encoding))
                )

                conn.commit()
                conn.close()

                st.success("User Registered")

elif menu == "Take Attendance":
    st.header("Scan Face")

    picture = st.camera_input("Camera")

    if picture is not None:
        bytes_data = picture.getvalue()
        np_img = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        encoding = get_face_encoding(rgb)

        if encoding is None:
            st.error("No face detected")
        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id,name,encoding FROM users")
            users = cursor.fetchall()

            conn.close()

            known_encodings = []
            user_ids = []
            names = []

            for u in users:
                user_ids.append(u[0])
                names.append(u[1])
                known_encodings.append(decode_blob(u[2]))

            match = compare_faces(known_encodings, encoding)

            if match is not None:
                user_id = user_ids[match]
                name = names[match]

                photo_path = f"photos/{name}.jpg"

                cv2.imwrite(photo_path, img)

                status, time = mark_attendance(user_id, photo_path)

                st.success(f"{name} - {status}")
                st.write(time)
            else:
                st.error("User not recognized")
