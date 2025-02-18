from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Union, List
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle, Circle, Arrow, PathPatch, FancyArrowPatch
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from rich.markdown import Markdown
import random
from enum import Enum
import colorsys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class InputMode(Enum):
    MANUAL = "manual"
    AUTO = "auto"
    MIXED = "mixed"

@dataclass
class EnvironmentSettings:
    temperature: float = 25.0  # Celsius
    pressure: float = 1.0  # atm
    solvent: str = "Water"
    catalyst: Optional[str] = None
    pH: float = 7.0
    ionic_strength: float = 0.0  # M
    
    def modify_potential(self, base_potential: float) -> float:
        """Modify potential based on environmental conditions."""
        # Convert Celsius to Kelvin
        temperature_K = self.temperature + 273.15
        
        # Temperature effect (simplified Nernst equation modification)
        temp_factor = temperature_K / 298.15
        
        # Pressure effect (simplified)
        pressure_factor = np.log(self.pressure)
        
        # pH effect
        ph_factor = -0.059 * (self.pH - 7)
        
        # Solvent effect (simplified)
        solvent_factors = {
            "Water": 1.0,
            "Methanol": 0.95,
            "Ethanol": 0.90,
            "DMSO": 1.1,
            "Acetonitrile": 1.05
        }
        solvent_factor = solvent_factors.get(self.solvent, 1.0)
        
        # Catalyst effect
        catalyst_boost = 0.05 if self.catalyst else 0.0
        
        modified_potential = (base_potential * temp_factor * solvent_factor + 
                            pressure_factor * 0.01 + ph_factor + catalyst_boost)
        
        return round(modified_potential, 3)

@dataclass
class SimulationParameters:
    anode: str
    cathode: str
    conc_anode: float
    conc_cathode: float
    moles_reactant: float
    environment: EnvironmentSettings = EnvironmentSettings()

WELCOME_MESSAGE = """
[bold cyan]╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                   GalvaSim  v3.0                           ║
║                                                            ║
║           Developed by: dev-760                            ║
║                Last Update: Feb 2025                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝[/bold cyan]
"""

USAGE_GUIDE = """
[bold green]HOW TO USE THIS SIMULATOR:[/bold green]
1. [yellow]Select Input Mode:[/yellow]
   - Manual: You input all values
   - Auto: Program calculates optimal values
   - Mixed: Randomly selects values to input/auto-calculate
2. [yellow]Select Electrodes:[/yellow]
   - Choose from the extensive list of available materials
   - Program will automatically determine anode/cathode roles
   - Press Enter to let program choose optimal electrodes
3. [yellow]Enter Concentrations (M):[/yellow]
   - For anode and cathode compartments
   - Use any format: 0.5, 1.5e-3, 1.5x10^-3
   - Press Enter for optimal concentration
4. [yellow]Enter Moles of Reactant:[/yellow]
   - Determines total charge transfer
   - Press Enter for recommended amount
   - Typical range: 0.1 to 1.0 moles
5. [yellow]Environmental Controls (Optional):[/yellow]
   - Temperature (°C)
   - Pressure (atm)
   - Solvent selection
   - Catalyst options
   - pH control
   
6. [yellow]Analyze Results:[/yellow]
   - Cell potential
   - Charge transfer
   - Detailed half-reactions
   - Environmental effects
   - Professional visualization
[bold red]Note:[/bold red] Default conditions are 25°C, 1 atm, water solvent, no catalyst
"""

# Standard Reduction Potentials (V) relative to SHE (Standard Hydrogen Electrode)
STANDARD_REDUCTION_POTENTIALS = {
    "Li": {"potential": -3.04},
    "K": {"potential": -2.93},
    "Ca": {"potential": -2.87},
    "Na": {"potential": -2.71},
    "Mg": {"potential": -2.37},
    "Al": {"potential": -1.66},
    "Zn": {"potential": -0.76},
    "Fe": {"potential": -0.44},
    "Ni": {"potential": -0.25},
    "Sn": {"potential": -0.14},
    "Pb": {"potential": -0.13},
    "H2": {"potential": 0.00},  # Standard Hydrogen Electrode
    "Cu": {"potential": 0.34},
    "Ag": {"potential": 0.80},
    "Hg": {"potential": 0.85},
    "Pt": {"potential": 1.20},
    "Au": {"potential": 1.50}
}

class AdvancedElectrochemicalCell:
    def __init__(self):
        self.environment = EnvironmentSettings()
        
    def suggest_optimal_electrodes(self) -> Tuple[str, str]:
        """Suggest optimal electrode materials for maximum potential."""
        electrodes = list(STANDARD_REDUCTION_POTENTIALS.items())
        random.shuffle(electrodes)  # Randomize the selection
        electrodes.sort(key=lambda x: x[1]['potential'])
        return electrodes[0][0], electrodes[-1][0]  # Returns anode, cathode pair
    
    def suggest_optimal_concentration(self, is_anode: bool) -> float:
        """Suggest optimal concentration based on electrode role."""
        if is_anode:
            return round(random.uniform(0.5, 1.0), 2)  # Higher for anode
        return round(random.uniform(0.1, 0.5), 2)  # Lower for cathode
    
    def suggest_optimal_moles(self, cell_potential: float) -> float:
        """Suggest optimal moles based on cell potential."""
        return round(cell_potential * 0.1, 3)
    
    def calculate_cell_potential(self, params: SimulationParameters) -> float:
        """Calculate cell potential with environmental considerations."""
        E0_anode = self.environment.modify_potential(
            STANDARD_REDUCTION_POTENTIALS[params.anode]['potential'])
        E0_cathode = self.environment.modify_potential(
            STANDARD_REDUCTION_POTENTIALS[params.cathode]['potential'])
        
        E0_cell = E0_cathode - E0_anode
        
        # Convert Celsius to Kelvin
        temperature_K = self.environment.temperature + 273.15
        
        # Enhanced Nernst equation with temperature correction
        RT_nF = (temperature_K * 8.314) / (2 * 96485)
        Q = params.conc_anode / params.conc_cathode
        E_cell = E0_cell - RT_nF * np.log(Q)
        
        return round(E_cell, 3)
    
    def get_half_reactions(self, anode: str, cathode: str) -> Tuple[str, str, str]:
        """Get half reactions and overall reaction equation for the galvanic cell."""
        half_reaction_anode = f"{anode}ⁿ⁺ + n e⁻ ⇌ {anode}"
        half_reaction_cathode = f"{cathode}ᵐ⁺ + m e⁻ ⇌ {cathode}"
        overall_reaction = f"m {anode} + n {cathode}ᵐ⁺ ⇌ n {cathode} + m {anode}ⁿ⁺"
        return half_reaction_anode, half_reaction_cathode, overall_reaction
    
    def get_reaction_summary(self, anode: str, cathode: str, moles_anode: float, moles_cathode: float) -> str:
        """Get a summary of the overall reaction."""
        return f"The overall reaction suggests that {moles_anode} moles of {anode} are oxidized and {moles_cathode} moles of {cathode} ions are reduced, forming {cathode} metal and {anode} ions."

import re

def parse_scientific_notation(value: str) -> float:
    """Parse numbers written in standard or scientific notation."""
    value = value.replace("x10^", "e")  # Convert formats like 1.5x10^-3 to 1.5e-3
    if re.match(r"^-?\d+(\.\d+)?(e-?\d+)?$", value):
        return float(value)
    raise ValueError(f"Invalid number format: {value}")

def get_user_input(prompt: str, allow_auto: bool = True) -> Union[str, float]:
    """Enhanced input handling with auto option."""
    while True:
        try:
            value = console.input(prompt).strip().lower()
            if allow_auto and value == '':
                return 'auto'
            return parse_scientific_notation(value)
        except ValueError as e:
            console.print(f"[red]{str(e)}[/red]")
            console.print("[yellow]Please enter a valid number or press Enter for auto[/yellow]")

def configure_environment() -> EnvironmentSettings:
    """Configure environmental parameters."""
    env = EnvironmentSettings()
    
    if Confirm.ask("Would you like to modify environmental parameters?"):
        env.temperature = float(get_user_input("[cyan]Enter temperature (°C) [default=25]: [/cyan]") or 25)
        env.pressure = float(get_user_input("[cyan]Enter pressure (atm) [default=1.0]: [/cyan]") or 1.0)
        
        # Solvent selection
        solvents = ["Water", "Methanol", "Ethanol", "DMSO", "Acetonitrile"]
        console.print("[cyan]Available solvents:[/cyan]")
        for i, solvent in enumerate(solvents, 1):
            console.print(f"{i}. {solvent}")
        choice = int(get_user_input("[cyan]Select solvent (1-5) [default=1]: [/cyan]") or 1)
        env.solvent = solvents[choice-1]
        
        # Catalyst selection
        catalysts = ["None", "Platinum", "Palladium", "Nickel"]
        console.print("[cyan]Available catalysts:[/cyan]")
        for i, catalyst in enumerate(catalysts):
            console.print(f"{i}. {catalyst}")
        choice = int(get_user_input("[cyan]Select catalyst (0-3) [default=0]: [/cyan]") or 0)
        env.catalyst = None if choice == 0 else catalysts[choice]
        
        env.pH = float(get_user_input("[cyan]Enter pH [default=7.0]: [/cyan]") or 7.0)
        
    return env

def draw_galvanic_cell(anode: str, cathode: str, E_cell: float):
    plt.figure(figsize=(10, 6))
    
    G = nx.DiGraph()
    G.add_node(anode, pos=(0, 0), label=anode)
    G.add_node(cathode, pos=(1, 0), label=cathode)
    G.add_edge(anode, cathode, weight=E_cell)
    
    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_node_attributes(G, 'label')
    
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color='skyblue', font_size=15, font_color='black', font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(anode, cathode): f"{E_cell} V"}, font_size=15)
    
    plt.title("Galvanic Cell Diagram")
    plt.show()

def main():
    console.print(WELCOME_MESSAGE)
    console.print(USAGE_GUIDE)
    
    cell = AdvancedElectrochemicalCell()
    
    # Select input mode
    console.print("\n[bold cyan]Select Input Mode:[/bold cyan]")
    console.print("1. Manual - You input all values")
    console.print("2. Auto - Program calculates optimal values")
    console.print("3. Mixed - Randomly selects values to input/auto-calculate")
    
    mode = int(get_user_input("[cyan]Select mode (1-3): [/cyan]"))

    # Configure environment
    cell.environment = configure_environment()

    # **Ensure the program continues collecting input**
    if mode == 1:  # Manual Mode
        anode = console.input("[cyan]Enter anode material: [/cyan]").strip()
        cathode = console.input("[cyan]Enter cathode material: [/cyan]").strip()
        conc_anode = float(get_user_input("[cyan]Enter anode concentration (M): [/cyan]"))
        conc_cathode = float(get_user_input("[cyan]Enter cathode concentration (M): [/cyan]"))
        moles_reactant = float(get_user_input("[cyan]Enter moles of reactant: [/cyan]"))
        
        params = SimulationParameters(
            anode=anode,
            cathode=cathode,
            conc_anode=conc_anode,
            conc_cathode=conc_cathode,
            moles_reactant=moles_reactant,
            environment=cell.environment
        )

    elif mode == 2:  # Auto Mode
        anode, cathode = cell.suggest_optimal_electrodes()
        params = SimulationParameters(
            anode=anode,
            cathode=cathode,
            conc_anode=cell.suggest_optimal_concentration(True),
            conc_cathode=cell.suggest_optimal_concentration(False),
            moles_reactant=cell.suggest_optimal_moles(1.0),
            environment=cell.environment
        )

    elif mode == 3:  # Mixed Mode
        if random.choice([True, False]):
            anode = cell.suggest_optimal_electrodes()[0]
        else:
            anode = console.input("[cyan]Enter anode material (or press Enter for auto): [/cyan]").strip() or cell.suggest_optimal_electrodes()[0]
        
        if random.choice([True, False]):
            cathode = cell.suggest_optimal_electrodes()[1]
        else:
            cathode = console.input("[cyan]Enter cathode material (or press Enter for auto): [/cyan]").strip() or cell.suggest_optimal_electrodes()[1]
        
        if random.choice([True, False]):
            conc_anode = cell.suggest_optimal_concentration(True)
        else:
            conc_anode = get_user_input("[cyan]Enter anode concentration (M) (or press Enter for auto): [/cyan]")
        
        if random.choice([True, False]):
            conc_cathode = cell.suggest_optimal_concentration(False)
        else:
            conc_cathode = get_user_input("[cyan]Enter cathode concentration (M) (or press Enter for auto): [/cyan]")
        
        if random.choice([True, False]):
            moles_reactant = cell.suggest_optimal_moles(1.0)
        else:
            moles_reactant = get_user_input("[cyan]Enter moles of reactant (or press Enter for auto): [/cyan]")
        
        # Ensure 'auto' values are converted to float using suggestions
        conc_anode = cell.suggest_optimal_concentration(True) if conc_anode == 'auto' else float(conc_anode)
        conc_cathode = cell.suggest_optimal_concentration(False) if conc_cathode == 'auto' else float(conc_cathode)
        moles_reactant = cell.suggest_optimal_moles(1.0) if moles_reactant == 'auto' else float(moles_reactant)
        
        params = SimulationParameters(
            anode=anode,
            cathode=cathode,
            conc_anode=conc_anode,
            conc_cathode=conc_cathode,
            moles_reactant=moles_reactant,
            environment=cell.environment
        )

    else:
        console.print("[red]Invalid mode selected. Exiting...[/red]")
        return

    # **Calculate and display results**
    E_cell = cell.calculate_cell_potential(params)
    console.print(f"\n[bold green]Calculated Cell Potential: {E_cell} V[/bold green]")
    
    # Get and display half-reactions and overall reaction
    half_reaction_anode, half_reaction_cathode, overall_reaction = cell.get_half_reactions(params.anode, params.cathode)
    console.print(f"\n[bold blue]Anode Half-Reaction: {half_reaction_anode}[/bold blue]")
    console.print(f"[bold blue]Cathode Half-Reaction: {half_reaction_cathode}[/bold blue]")
    console.print(f"[bold blue]Overall Reaction: {overall_reaction}[/bold blue]")
    
    # Calculate moles of anode and cathode
    moles_anode = params.moles_reactant
    moles_cathode = (params.moles_reactant * params.conc_anode) / params.conc_cathode
    reaction_summary = cell.get_reaction_summary(params.anode, params.cathode, moles_anode, moles_cathode)
    console.print(f"\n[bold green]{reaction_summary}[/bold green]")
    console.print(f"[bold green]Moles of Anode Reactant: {moles_anode}[/bold green]")
    console.print(f"[bold green]Moles of Cathode Reactant: {moles_cathode}[/bold green]")
    
    # Draw the galvanic cell diagram
    draw_galvanic_cell(params.anode, params.cathode, E_cell)

if __name__ == "__main__":
    main()
