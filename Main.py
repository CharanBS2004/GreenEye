import tkinter as tk
from tkinter import filedialog
import requests
import uuid
import os
from ultralytics import YOLO

# --- CONFIGURATION ---
THEME_COLOR = "#2E7D32" 
# Your specific API endpoint
API_URL = "https://aws-us-east-2.langflow.datastax.com/lf/cff46d4e-63cb-4b9d-a9d0-467de19c9ed3/api/v1/run/46a1022c-3153-4a53-ba58-8f428527c60c"
# Using the token from your provided snippet
AUTH_TOKEN = "Bearer AstraCS:KyNFAWiHBUKyCaJBsuxBumCB:52f6f624222f5fb6162c2d88a89e11617be29f5f6d34beed48669bc6e50a5eaa"
ORG_ID = "d0ca315c-f483-444f-917f-a40a0ff9769f"

class PlantDiagnosticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cotton Disease Diagnostic Tool")
        self.root.geometry("600x700")
        self.root.configure(bg="white")

        # UI Header
        self.header = tk.Label(root, text="Green Eye", bg=THEME_COLOR, fg="white", font=("Arial", 18, "bold"), pady=10)
        self.header.pack(fill="x")

        # Upload Button
        self.upload_btn = tk.Button(root, text="Upload Image", command=self.process_image, bg=THEME_COLOR, fg="white", font=("Arial", 12), padx=20, pady=10)
        self.upload_btn.pack(pady=30)

        self.path_label = tk.Label(root, text="No image selected", bg="white", fg="grey")
        self.path_label.pack()

        # Output Area
        self.output_area = tk.Text(root, wrap="word", padx=20, pady=20, font=("Arial", 10), bg="#F5F5F5", state="disabled")
        self.output_area.pack(expand=True, fill="both", padx=20, pady=20)

    def run_yolo_model(self, image_path):
        """Runs the YOLO model locally to detect the disease."""
        model_path = r'C:\Users\student\Downloads\GreenEYe\best.pt'
        model = YOLO(model_path)
        
        results = model(image_path)
        data = {}
        for result in results:
            probs = result.probs  
            class_id = probs.top1
            score = probs.top1conf
            data = {
                'PREDICTION': result.names[class_id], 
                'CONFIDENCE': round(float(score)*100, 2),
                'PLANT': 'Cotton'
            }
        return data

    def get_treatment_details(self, data):
        """Modified API Access based on your new snippet."""
        # Construct the prompt based on YOLO results
        input_prompt = f"Based on the provided data, give me the symptoms and treatment for {data['PREDICTION']} in {data['PLANT']}."
        
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": input_prompt,
            "session_id": str(uuid.uuid4())
        }

        headers = {
            "X-DataStax-Current-Org": "d0ca315c-f483-444f-917f-a40a0ff9769f", 
            "Authorization": 'Bearer AstraCS:DITCAgssAOdEjhOnOUYQUETZ:ec67297f58789214daad0a7dfe059d374dfd8bacb34961e18e1863290aa5c992',
            "Content-Type": "application/json", 
            "Accept": "application/json",
        }
        
        try:
            # Using the POST method from your new snippet logic
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Navigating the response path
            raw_text = result.get('outputs', [{}])[0].get('outputs', [{}])[0].get('results', {}).get('message', {}).get('text')

            if raw_text:
                return raw_text.replace("**", "")
            return "No diagnosis text found in the API response."
            
        except requests.exceptions.RequestException as e:
            return f"Error making API request: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def process_image(self):
        """Full workflow: YOLO -> API -> Display cleaned text."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return

        self.path_label.config(text=f"Analyzing: {os.path.basename(file_path)}")
        self.root.update_idletasks()
        
        # 1. Run local YOLO detection
        prediction = self.run_yolo_model(file_path)
        
        # 2. Get diagnosis from your updated API
        treatment_text = self.get_treatment_details(prediction)
        
        # 3. Update the UI with clean text
        self.output_area.config(state="normal")
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, f"DIAGNOSIS: {prediction['PREDICTION']}\n")
        self.output_area.insert(tk.END, f"CONFIDENCE: {prediction['CONFIDENCE']}%\n")
        self.output_area.insert(tk.END, "-"*40 + "\n\n")
        self.output_area.insert(tk.END, treatment_text)
        self.output_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlantDiagnosticApp(root)

    root.mainloop()
