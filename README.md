# GalvaSim ⚡

## Overview 🌟

**GalvaSim** is a tool designed to simulate how a galvanic (or electrochemical) cell behaves under different conditions. Whether you're a student learning about electrochemistry 📚 or a researcher needing a quick way to visualize and calculate electrochemical reactions 🧑‍🔬, this simulator can help you understand the processes behind these reactions, including how temperature 🌡️, pressure 💨, solvent 🧪, catalyst 📈, and pH 🧫 affect cell performance.

The simulator uses several scientific Python libraries, making it a great resource for anyone working with scientific simulations. 

## Key Features 🔥

### Input Modes ⌨️
You can choose from three different modes depending on how much control you want over the simulation:

- **Manual Mode:** You provide all the values, like electrode materials, concentrations, and moles of reactant.
- **Auto Mode:** The program suggests the best electrodes, concentrations, and moles based on the conditions.
- **Mixed Mode:** A balance between manual input and auto-calculation. You can choose which values to input and which ones the program will calculate.

### Environmental Settings ⚗️
The simulator lets you customize the following environmental factors:

- **Temperature (K):** Affects reaction rates and cell potential.
- **Pressure (atm):** Influences electrochemical reactions.
- **Solvent:** Choose from solvents like Water, Methanol, or Ethanol.
- **Catalyst:** Select a catalyst like Platinum or Nickel to boost the reaction.
- **pH:** Adjust the pH level to simulate different conditions.

### Simulation Parameters ⚙️
The simulation is based on key parameters defining the cell’s behavior:

- **Anode and Cathode Materials:** These materials determine the overall reaction and cell potential.
- **Concentrations:** The concentration of reactants impacts the cell’s potential.
- **Moles of Reactant:** The amount of reactant determines the total charge transfer.

### Detailed Cell Potential Calculation 🔋
The simulator calculates the cell potential using:

- **Nernst Equation:** Adjusts the potential based on concentration and temperature.
- **Environmental Factors:** Temperature, pressure, and pH.
- **Catalysts:** Improve reaction efficiency and cell potential.

### Requirements 🧰

To use **GalvaSim** , ensure you have the following installed:

- **Python 3.x** (preferably 3.8 or later)
- **pip** (Python package installer)

### Installation 🛠️

1. Clone the repository:

   ```bash
   git clone https://github.com/yourgithubusername/GalvaSim.git
   cd GalvaSim

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt

3. Running the Simulator 🚀

    ```bash
    python3 galvasim.py

---

### Developer  🧑‍💻

This project was developed by [Hassan Karasu](https://github.com/dev-760)
