import streamlit as st
import cv2
import numpy as np
import os
from PIL import Image
import face_recognition

from database import init_db, get_connection, get_user_force_out
from face_utils import get_face_encoding, encode_to_blob, decode_blob, compare_faces, detect_face, crop_face
from attendance import mark_attendance

REGISTERED_FACES_DIR = "registered_faces"
PHOTOS_DIR = "photos"
os.makedirs(REGISTERED_FACES_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)

init_db()

st.title("Face Attendance System")

if "menu" not in st.session_state:
    st.session_state.menu = "Register User"

st.sidebar.markdown("### Navigation")

if st.sidebar.button("Register User"):
    st.session_state.menu = "Register User"
if st.sidebar.button("View Registered Users"):
    st.session_state.menu = "View Registered Users"
if st.sidebar.button("Take Attendance"):
    st.session_state.menu = "Take Attendance"
if st.sidebar.button("Real-time Attendance"):
    st.session_state.menu = "Real-time Attendance"
if st.sidebar.button("View Entries"):
    st.session_state.menu = "View Entries"

menu = st.session_state.menu

if menu == "Register User":
    st.header("Register New User")

    name = st.text_input("Name")
    roll = st.text_input("Roll Number")

    picture = st.camera_input("Take Photo")

    if picture is not None:
        bytes_data = picture.getvalue()
        np_img = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_location, encoding = detect_face(rgb)

        if encoding is not None:
            top, right, bottom, left = face_location
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
            st.image(img, caption="Face Detected", channels="BGR")

    if st.button("Register"):
        if picture is None:
            st.error("Take photo first")
        elif encoding is None:
            st.error("Face not detected")
        else:
            cropped_face = crop_face(rgb, face_location)

            photo_filename = f"{roll}.jpg"
            photo_path = os.path.join(REGISTERED_FACES_DIR, photo_filename)
            cv2.imwrite(photo_path, cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR))

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users(name,roll,encoding,photo,force_out) VALUES(?,?,?,?,?)",
                (name, roll, encode_to_blob(encoding), photo_path, 0)
            )

            conn.commit()
            conn.close()

            st.success("User Registered")

elif menu == "View Registered Users":
    st.header("Registered Users")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, roll, photo FROM users")
    users = cursor.fetchall()

    conn.close()

    if not users:
        st.info("No registered users")
    else:
        cols = st.columns(4)
        for i, user in enumerate(users):
            with cols[i % 4]:
                if user[2] and os.path.exists(user[2]):
                    st.image(user[2], caption=f"{user[0]} ({user[1]})", use_container_width=True)
                else:
                    st.warning(f"{user[0]} ({user[1]}) - No photo")

elif menu == "Take Attendance":
    st.header("Scan Face")

    picture = st.camera_input("Camera")

    if picture is not None:
        bytes_data = picture.getvalue()
        np_img = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_location, encoding = detect_face(rgb)

        if encoding is None:
            st.error("No face detected")
        else:
            top, right, bottom, left = face_location
            img_with_box = img.copy()
            cv2.rectangle(img_with_box, (left, top), (right, bottom), (0, 255, 0), 2)
            st.image(img_with_box, caption="Face Detected", channels="BGR")

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

                cropped_face = crop_face(rgb, face_location)
                photo_path = os.path.join(PHOTOS_DIR, f"{name}.jpg")
                cv2.imwrite(photo_path, cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR))

                status, time = mark_attendance(user_id, photo_path)

                st.success(f"{name} - {status}")
                st.write(time)
            else:
                st.error("User not recognized")

elif menu == "Real-time Attendance":
    st.header("Real-time Face Attendance")
    
    FRAME_WINDOW = st.image([])
    
    run = st.toggle("Start Camera", value=False)
    
    if run:
        cap = cv2.VideoCapture(0)
        
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
        
        attended_today = set()
        
        while run:
            ret, frame = cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            center_x = w // 2
            cv2.line(frame, (center_x, 0), (center_x, h), (255, 255, 0), 2)
            cv2.putText(frame, "IN", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "OUT", (w - 80, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locs = face_recognition.face_locations(rgb)
            face_encodings = face_recognition.face_encodings(rgb, face_locs)
            
            for (top, right, bottom, left), face_enc in zip(face_locs, face_encodings):
                face_center = (left + right) // 2
                
                if face_center < center_x:
                    default_status = "IN"
                    default_color = (0, 255, 0)
                else:
                    default_status = "OUT"
                    default_color = (0, 0, 255)
                
                cv2.rectangle(frame, (left, top), (right, bottom), default_color, 2)
                
                match = compare_faces(known_encodings, face_enc)
                
                if match is not None:
                    name = names[match]
                    user_id = user_ids[match]
                    
                    force_out = get_user_force_out(user_id)
                    
                    if force_out == 1:
                        status_label = "OUT"
                        box_color = (0, 0, 255)
                    else:
                        status_label = default_status
                        box_color = default_color
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
                    
                    cv2.putText(frame, f"{name} ({status_label})", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)
                    
                    if user_id not in attended_today:
                        attended_today.add(user_id)
                        cropped_face = crop_face(rgb, (top, right, bottom, left))
                        photo_path = os.path.join(PHOTOS_DIR, f"{name}_rt.jpg")
                        cv2.imwrite(photo_path, cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR))
                        status, time = mark_attendance(user_id, photo_path, status_label)
                        if status:
                            st.toast(f"{name} - {status} at {time}", icon="✅")
                else:
                    cv2.putText(frame, f"Unknown ({default_status})", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, default_color, 2)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame)
            
        cap.release()

elif menu == "View Entries":
    st.header("Attendance Entries")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT a.id, u.name, u.roll, a.timestamp, a.status, a.photo
    FROM attendance a
    JOIN users u ON a.user_id = u.id
    ORDER BY a.timestamp DESC
    """)
    entries = cursor.fetchall()
    
    conn.close()
    
    if not entries:
        st.info("No attendance entries")
    else:
        for entry in entries:
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                st.write(f"**{entry[1]}**")
                st.caption(entry[2])
            with col2:
                st.write(entry[3])
            with col3:
                if entry[4] == "IN":
                    st.success("IN")
                else:
                    st.error("OUT")
            with col4:
                if entry[5] and os.path.exists(entry[5]):
                    st.image(entry[5], width=50)
            st.divider()
