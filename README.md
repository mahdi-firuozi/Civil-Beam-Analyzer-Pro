# Civil Engineering Beam Analyzer & Report Suite

A desktop application designed for structural and civil engineers to perform real-time analysis of simply supported beams under concentrated point loads. It calculates reaction forces, maximum bending moments, and automatically compiles detailed engineering reports.

## 🚀 Key Features
* Engineering Computations: Real-time analysis of support reactions ($R_A$, $R_B$) and maximum bending moment based on static equilibrium ($\Sigma F_y = 0, \Sigma M = 0$).
* Dynamic Plotting: Integrates Matplotlib to generate and display shear and bending moment diagrams dynamically.
* Multi-Format Export: Generates professional, client-ready PDF technical reports (via ReportLab) and exports calculation data into structured JSON files for interoperability.
* Intuitive GUI: A clean Tkinter interface featuring input data validation and clear result layouts.

## 🛠️ Tech Stack
* Core Language: Python 3
* Mathematical Operations: NumPy
* Data Visualization: Matplotlib
* Document Generation: ReportLab (PDF Engine)
