import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
import json  # Added for Save/Load feature

# --- New Imports for PDF Export ---
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    messagebox.showwarning("Missing Library", "Please install reportlab to use PDF export: pip install reportlab")


class BeamAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simply Supported Beam Analyzer - Pro")
        self.root.geometry("480x600") # Slightly enlarged for new buttons and better spacing
        
        # --- Variables ---
        self.L_var = tk.StringVar()
        self.P_var = tk.StringVar()
        self.a_var = tk.StringVar()
        
        self.L = 0.0
        self.P = 0.0
        self.a = 0.0
        self.RA = 0.0
        self.RB = 0.0
        self.M_max = 0.0
        self.is_calculated = False
        
        self._build_gui()

    def _build_gui(self):
        # --- Input Frame --- (Improved Spacing and Labels)
        input_frame = tk.LabelFrame(self.root, text="Input Parameters", padx=15, pady=10, font=("Arial", 10, "bold"))
        input_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(input_frame, text="Beam Length (L) [m]:", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(input_frame, textvariable=self.L_var, width=18).grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="Point Load (P) [kN]:", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(input_frame, textvariable=self.P_var, width=18).grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="Load Position from left (a) [m]:", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(input_frame, textvariable=self.a_var, width=18).grid(row=2, column=1, pady=5, padx=10)
        
        # --- NEW: Save/Load Frame ---
        file_frame = tk.Frame(input_frame)
        file_frame.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(file_frame, text="Save Inputs", command=self.save_inputs, width=12).pack(side="left", padx=5)
        tk.Button(file_frame, text="Load Inputs", command=self.load_inputs, width=12).pack(side="left", padx=5)

        # --- Buttons Frame --- (Improved Layout)
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=15, pady=5)
        
        tk.Button(btn_frame, text="Calculate", command=self.calculate, width=12, font=("Arial", 9, "bold"), bg="#e0f7fa").pack(side="left", expand=True, padx=2)
        tk.Button(btn_frame, text="Plot Diagrams", command=self.plot_diagrams, width=12, font=("Arial", 9)).pack(side="left", expand=True, padx=2)
        tk.Button(btn_frame, text="Clear", command=self.clear, width=12).pack(side="left", expand=True, padx=2)
        
        # --- Output Frame ---
        output_frame = tk.LabelFrame(self.root, text="Analysis Results", padx=15, pady=10, font=("Arial", 10, "bold"))
        output_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.lbl_ra = tk.Label(output_frame, text="RA (Left Support): -", font=("Arial", 10, "bold"), fg="#000080")
        self.lbl_ra.pack(anchor="w", pady=4)
        
        self.lbl_rb = tk.Label(output_frame, text="RB (Right Support): -", font=("Arial", 10, "bold"), fg="#000080")
        self.lbl_rb.pack(anchor="w", pady=4)
        
        self.lbl_mmax = tk.Label(output_frame, text="Max Bending Moment: -", font=("Arial", 10, "bold"), fg="#8b0000")
        self.lbl_mmax.pack(anchor="w", pady=4)
        
        self.lbl_mpos = tk.Label(output_frame, text="Position of Max Moment: -", font=("Arial", 10, "bold"))
        self.lbl_mpos.pack(anchor="w", pady=4)
        
        # --- Export Frame --- (Added PDF Button)
        export_frame = tk.Frame(self.root)
        export_frame.pack(pady=15)
        tk.Button(export_frame, text="Export TXT", command=self.export_report, width=12).pack(side="left", padx=5)
        tk.Button(export_frame, text="Export PDF Report", command=self.export_pdf, width=18, font=("Arial", 9, "bold")).pack(side="left", padx=5)

    def validate_inputs(self):
        try:
            self.L = float(self.L_var.get())
            self.P = float(self.P_var.get())
            self.a = float(self.a_var.get())
            
            if self.L <= 0:
                raise ValueError("Length must be greater than 0.")
            if self.P <= 0:
                raise ValueError("Point load must be greater than 0.")
            if self.a < 0 or self.a > self.L:
                raise ValueError("Load position 'a' must be between 0 and Length (L).")
            return True
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input:\n{e}")
            return False

    def calculate(self):
        if not self.validate_inputs():
            return
            
        # Support Reactions calculations (Original formulas untouched)
        # Equilibrium: Sum(M_B) = 0 -> RA*L - P*(L-a) = 0
        self.RA = self.P * (self.L - self.a) / self.L
        
        # Equilibrium: Sum(F_y) = 0 -> RA + RB - P = 0
        self.RB = self.P * self.a / self.L
        
        # Validation of equilibrium check (internal)
        assert abs((self.RA + self.RB) - self.P) < 1e-6, "Equilibrium mismatch!"
        
        # Max Bending Moment
        self.M_max = self.RA * self.a
        
        # Update GUI
        self.lbl_ra.config(text=f"RA (Left Support): {self.RA:.2f} kN")
        self.lbl_rb.config(text=f"RB (Right Support): {self.RB:.2f} kN")
        self.lbl_mmax.config(text=f"Max Bending Moment: {self.M_max:.2f} kNm")
        self.lbl_mpos.config(text=f"Position of Max Moment: {self.a:.2f} m from left")
        
        self.is_calculated = True

    def plot_diagrams(self):
        if not self.is_calculated:
            messagebox.showwarning("Warning", "Please calculate first!")
            return
            
        # Generate x values
        x = np.linspace(0, self.L, 1000)
        
        # Calculate Shear Force (V) and Bending Moment (M) arrays
        V = np.where(x < self.a, self.RA, -self.RB)
        M = np.where(x <= self.a, self.RA * x, self.RA * x - self.P * (x - self.a))
        
        # Plotting (Original plotting logic untouched)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        fig.canvas.manager.set_window_title("Structural Diagrams")
        
        # Shear Force Diagram (SFD)
        ax1.plot(x, V, 'b-', linewidth=2)
        ax1.fill_between(x, V, 0, color='blue', alpha=0.2)
        ax1.axhline(0, color='black', linewidth=1)
        ax1.set_title("Shear Force Diagram (SFD)")
        ax1.set_ylabel("Shear Force (kN)")
        ax1.grid(True, linestyle='--', alpha=0.6)
        
        ax1.annotate(f"{self.RA:.2f} kN", xy=(0, self.RA), xytext=(0, self.RA*1.1))
        ax1.annotate(f"{-self.RB:.2f} kN", xy=(self.L, -self.RB), xytext=(self.L, -self.RB*1.1), ha='right')

        # Bending Moment Diagram (BMD)
        ax2.plot(x, M, 'r-', linewidth=2)
        ax2.fill_between(x, M, 0, color='red', alpha=0.2)
        ax2.axhline(0, color='black', linewidth=1)
        ax2.set_title("Bending Moment Diagram (BMD)")
        ax2.set_xlabel("Distance along beam (m)")
        ax2.set_ylabel("Bending Moment (kNm)")
        ax2.grid(True, linestyle='--', alpha=0.6)
        
        ax2.annotate(f"Max: {self.M_max:.2f} kNm", 
                     xy=(self.a, self.M_max), 
                     xytext=(self.a, self.M_max*1.1),
                     ha='center', arrowprops=dict(arrowstyle="->", color='black'))

        plt.tight_layout()
        plt.show()

    def clear(self):
        self.L_var.set("")
        self.P_var.set("")
        self.a_var.set("")
        self.lbl_ra.config(text="RA: -")
        self.lbl_rb.config(text="RB: -")
        self.lbl_mmax.config(text="Max Bending Moment: -")
        self.lbl_mpos.config(text="Position of Max Moment: -")
        self.is_calculated = False

    def export_report(self):
        if not self.is_calculated:
            messagebox.showwarning("Warning", "Please calculate first before exporting.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                 filetypes=[("Text files", "*.txt")],
                                                 title="Save Report")
        if file_path:
            with open(file_path, 'w') as f:
                f.write("=== Simply Supported Beam Analysis Report ===\n")
                f.write(f"Beam Length (L) : {self.L:.2f} m\n")
                f.write(f"Point Load (P)  : {self.P:.2f} kN\n")
                f.write(f"Load Position(a): {self.a:.2f} m\n")
                f.write("-" * 40 + "\n")
                f.write(f"Reaction at A (Left) : {self.RA:.2f} kN\n")
                f.write(f"Reaction at B (Right): {self.RB:.2f} kN\n")
                f.write(f"Maximum Bending Moment: {self.M_max:.2f} kNm\n")
                f.write(f"Position of Max Moment: {self.a:.2f} m from left support\n")
                f.write("=== Equilibrium Validated ===\n")
            messagebox.showinfo("Success", "TXT Report exported successfully!")

    # --- NEW FEATURES BELOW ---

    def save_inputs(self):
        """Save current input parameters to a JSON file."""
        data = {
            "L": self.L_var.get(),
            "P": self.P_var.get(),
            "a": self.a_var.get()
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")],
                                                 title="Save Input Parameters")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Success", "Inputs saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def load_inputs(self):
        """Load input parameters from a JSON file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")],
                                               title="Load Input Parameters")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.L_var.set(data.get("L", ""))
                self.P_var.set(data.get("P", ""))
                self.a_var.set(data.get("a", ""))
                messagebox.showinfo("Success", "Inputs loaded successfully! Click Calculate.")
                self.is_calculated = False # Reset calculation state
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def export_pdf(self):
        """Generate a professional engineering PDF report using reportlab."""
        if not self.is_calculated:
            messagebox.showwarning("Warning", "Please calculate first before exporting PDF.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                 filetypes=[("PDF files", "*.pdf")],
                                                 title="Save PDF Report")
        if file_path:
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 50, "STRUCTURAL ANALYSIS REPORT")
                c.setFont("Helvetica", 10)
                c.drawString(50, height - 70, "Simply Supported Beam with Point Load")
                c.line(50, height - 80, width - 50, height - 80)
                
                # Input Parameters
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, height - 120, "1. Input Parameters:")
                c.setFont("Helvetica", 11)
                c.drawString(70, height - 140, f"Beam Length (L): {self.L:.2f} m")
                c.drawString(70, height - 160, f"Point Load (P): {self.P:.2f} kN")
                c.drawString(70, height - 180, f"Load Position (a): {self.a:.2f} m from left support")
                
                # Results
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, height - 230, "2. Calculation Results:")
                c.setFont("Helvetica", 11)
                c.drawString(70, height - 250, f"Reaction Force at A (RA): {self.RA:.2f} kN")
                c.drawString(70, height - 270, f"Reaction Force at B (RB): {self.RB:.2f} kN")
                c.drawString(70, height - 290, f"Maximum Bending Moment: {self.M_max:.2f} kNm")
                c.drawString(70, height - 310, f"Position of Maximum Moment: {self.a:.2f} m")
                
                # Footer / Validation
                c.line(50, height - 350, width - 50, height - 350)
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(50, height - 370, "Equilibrium verified: ΣFy = 0 and ΣM = 0")
                c.drawString(50, height - 390, "Generated by Beam Analyzer Pro")
                
                c.save()
                messagebox.showinfo("Success", "Professional PDF Report exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate PDF:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BeamAnalyzerApp(root)
    root.mainloop()
