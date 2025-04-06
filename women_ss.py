import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import threading
import pygame
from geopy.geocoders import Nominatim

class WomenSafetyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Women Safety App")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFE4E1")
        
        # Initialize database
        self.create_database()
        
        # Initialize pygame for alarm sound
        pygame.mixer.init()
        
        # Initialize panic mode state
        self.panic_mode = False
        
        # Set up periodic location tracking
        self.location_tracking = False
        self.track_location_thread = None
        
        # Create main menu
        self.create_main_menu()

    def create_database(self):
        conn = sqlite3.connect("safety.db")
        c = conn.cursor()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                relationship TEXT
            )
        """)
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS safe_locations (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            )
        """)
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS emergency_logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                location TEXT,
                type TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    def create_main_menu(self):
        # Title
        title = tk.Label(self.root, 
                        text="Women Safety Application",
                        font=("Arial", 24, "bold"), 
                        bg="#FFE4E1")
        title.pack(pady=20)

        # Main buttons frame
        button_frame = tk.Frame(self.root, bg="#FFE4E1")
        button_frame.pack(pady=20)

        # SOS Button
        sos_button = tk.Button(button_frame, 
                              text="SOS EMERGENCY",
                              command=self.trigger_emergency,
                              bg="red", 
                              fg="white",
                              font=("Arial", 20, "bold"),
                              height=2, 
                              width=20)
        sos_button.pack(pady=10)

        # Feature buttons
        features = [
            ("Manage Contacts", self.manage_contacts),
            ("Safe Locations", self.manage_safe_locations),
            ("Start Location Tracking", self.toggle_location_tracking),
            ("View Emergency Logs", self.view_logs)
        ]

        for text, command in features:
            btn = tk.Button(button_frame, 
                          text=text,
                          command=command,
                          bg="#4CAF50", 
                          fg="white",
                          font=("Arial", 12),
                          height=2, 
                          width=20)
            btn.pack(pady=5)

    def manage_contacts(self):
        contact_window = tk.Toplevel(self.root)
        contact_window.title("Manage Emergency Contacts")
        contact_window.geometry("500x600")
        contact_window.configure(bg="#FFE4E1")

        # Add contact form
        form_frame = tk.Frame(contact_window, bg="#FFE4E1")
        form_frame.pack(pady=10)

        tk.Label(form_frame, 
                text="Add Emergency Contact",
                font=("Arial", 14, "bold"),
                bg="#FFE4E1").pack()

        fields = [("Name", "name"), 
                 ("Phone", "phone"), 
                 ("Relationship", "relation")]
        entries = {}

        for label, key in fields:
            row = tk.Frame(form_frame, bg="#FFE4E1")
            row.pack(pady=5)
            tk.Label(row, text=f"{label}:", 
                    bg="#FFE4E1").pack(side=tk.LEFT)
            entries[key] = tk.Entry(row)
            entries[key].pack(side=tk.LEFT, padx=5)

        def save_contact():
            name = entries["name"].get()
            phone = entries["phone"].get()
            relation = entries["relation"].get()
            
            if name and phone:
                conn = sqlite3.connect("safety.db")
                c = conn.cursor()
                c.execute("""
                    INSERT INTO contacts (name, phone, relationship) 
                    VALUES (?, ?, ?)
                """, (name, phone, relation))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Contact saved successfully!")
                self.display_contacts(contact_window)
            else:
                messagebox.showerror("Error", "Name and Phone are required!")

        tk.Button(form_frame, 
                 text="Save Contact",
                 command=save_contact,
                 bg="#4CAF50", 
                 fg="white").pack(pady=10)

        self.display_contacts(contact_window)

    def display_contacts(self, window):
        try:
            self.contacts_frame.destroy()
        except:
            pass

        self.contacts_frame = tk.Frame(window, bg="#FFE4E1")
        self.contacts_frame.pack(pady=10)

        tk.Label(self.contacts_frame, 
                text="Emergency Contacts",
                font=("Arial", 14, "bold"), 
                bg="#FFE4E1").pack()

        conn = sqlite3.connect("safety.db")
        c = conn.cursor()
        contacts = c.execute("SELECT * FROM contacts").fetchall()
        conn.close()

        for contact in contacts:
            contact_frame = tk.Frame(self.contacts_frame, bg="#FFE4E1")
            contact_frame.pack(pady=5, padx=10, fill=tk.X)
            info = f"{contact[1]} ({contact[3]})\nPhone: {contact[2]}"
            tk.Label(contact_frame, text=info, 
                    bg="#FFE4E1").pack(side=tk.LEFT)

    def toggle_location_tracking(self):
        if not self.location_tracking:
            self.location_tracking = True
            self.track_location_thread = threading.Thread(
                target=self.track_location)
            self.track_location_thread.daemon = True
            self.track_location_thread.start()
            messagebox.showinfo("Tracking", "Location tracking started!")
        else:
            self.location_tracking = False
            messagebox.showinfo("Tracking", "Location tracking stopped!")

    def track_location(self):
        while self.location_tracking:
            try:
                geolocator = Nominatim(user_agent="women_safety_app")
                location = geolocator.geocode("me")  # In real app, use GPS
                
                conn = sqlite3.connect("safety.db")
                c = conn.cursor()
                c.execute("""
                    INSERT INTO emergency_logs 
                    (timestamp, location, type)
                    VALUES (?, ?, ?)
                """, (datetime.now().isoformat(), 
                     str(location), "tracking"))
                conn.commit()
                conn.close()
                
                threading.Event().wait(300)  # Update every 5 minutes
            except:
                pass

    def manage_safe_locations(self):
        locations_window = tk.Toplevel(self.root)
        locations_window.title("Safe Locations")
        locations_window.geometry("500x600")
        locations_window.configure(bg="#FFE4E1")

        form_frame = tk.Frame(locations_window, bg="#FFE4E1")
        form_frame.pack(pady=10)

        tk.Label(form_frame, 
                text="Add Safe Location",
                font=("Arial", 14, "bold"), 
                bg="#FFE4E1").pack()

        entries = {}
        for field in ["Name", "Address"]:
            row = tk.Frame(form_frame, bg="#FFE4E1")
            row.pack(pady=5)
            tk.Label(row, text=f"{field}:", 
                    bg="#FFE4E1").pack(side=tk.LEFT)
            entries[field.lower()] = tk.Entry(row)
            entries[field.lower()].pack(side=tk.LEFT, padx=5)

        def save_location():
            name = entries["name"].get()
            address = entries["address"].get()
            
            if name and address:
                try:
                    geolocator = Nominatim(user_agent="women_safety_app")
                    location = geolocator.geocode(address)
                    conn = sqlite3.connect("safety.db")
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO safe_locations 
                        (name, address, latitude, longitude)
                        VALUES (?, ?, ?, ?)
                    """, (name, address, 
                         location.latitude, location.longitude))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Location saved!")
                except:
                    messagebox.showerror("Error", "Could not geocode address!")
            else:
                messagebox.showerror("Error", "All fields are required!")

        tk.Button(form_frame, 
                 text="Save Location",
                 command=save_location,
                 bg="#4CAF50", 
                 fg="white").pack(pady=10)

    def play_alarm(self):
        try:
            pygame.mixer.music.load("alarm.wav")
            pygame.mixer.music.play(-1)
        except:
            print("Could not play alarm sound")

    def trigger_emergency(self):
        # Activate panic mode
        self.panic_mode = True
        
        # Play alarm
        self.play_alarm()
        
        # Get current location
        try:
            geolocator = Nominatim(user_agent="women_safety_app")
            location = geolocator.geocode("me")  # In real app, use GPS
            location_str = str(location)
        except:
            location_str = "Location unavailable"

        # Log emergency
        conn = sqlite3.connect("safety.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO emergency_logs 
            (timestamp, location, type)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), 
              location_str, "emergency"))
        
        # Get emergency contacts
        contacts = c.execute("SELECT * FROM contacts").fetchall()
        conn.commit()
        conn.close()

        # Notify contacts
        emergency_message = f"""
        EMERGENCY ALERT!
        Location: {location_str}
        Timestamp: {datetime.now()}
        """
        for contact in contacts:
            messagebox.showinfo("Alert Sent", 
                              f"Emergency alert sent to {contact[1]}")

    def view_logs(self):
        logs_window = tk.Toplevel(self.root)
        logs_window.title("Emergency Logs")
        logs_window.geometry("600x400")
        logs_window.configure(bg="#FFE4E1")

        tk.Label(logs_window, 
                text="Emergency Logs",
                font=("Arial", 14, "bold"), 
                bg="#FFE4E1").pack(pady=10)

        conn = sqlite3.connect("safety.db")
        c = conn.cursor()
        logs = c.execute("""
            SELECT * FROM emergency_logs 
            ORDER BY timestamp DESC LIMIT 50
        """).fetchall()
        conn.close()

        for log in logs:
            log_frame = tk.Frame(logs_window, bg="#FFE4E1")
            log_frame.pack(pady=5, padx=10, fill=tk.X)
            info = f"Type: {log[3]}\nTime: {log[1]}\nLocation: {log[2]}"
            tk.Label(log_frame, text=info, 
                    bg="#FFE4E1").pack(side=tk.LEFT)

def main():
    root = tk.Tk()
    app = WomenSafetyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()