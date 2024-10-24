from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit import QuantumCircuit
import numpy as np
import stim

from qiskit.circuit.library import RZGate, RXGate, RYGate
import random

def transform_to_allowed_gates(circuit, **kwargs):
    """
    circuit (QuantumCircuit): Circuit with only Clifford gates (1q rotations Ry, Rz must be k*pi/2).
    kwargs (Dict): All the arguments that need to be passed on to the next function calls.
    
    Returns:
    (QuantumCircuit) Logically equivalent circuit but with gates in required format (no Ry, Rz gates; only S, Sdg, H, X, Z).
    """
    dag = circuit_to_dag(circuit)
    threshold = 1e-3
    # we will substitute nodes inplace
    for node in dag.op_nodes():
        if node.name == "ry":
            angle = float(node.op.params[0])
            # substitute gates
            if abs(angle - 0) < threshold:
                dag.remove_op_node(node)
            elif abs(angle - np.pi/2) < threshold:
                qc_loc = QuantumCircuit(1)
                qc_loc.sdg(0)
                qc_loc.sx(0)
                qc_loc.s(0)
                qc_loc_instr = qc_loc.to_instruction()
                dag.substitute_node(node, qc_loc_instr, inplace = True)
            elif abs(angle - np.pi) < threshold:
                qc_loc = QuantumCircuit(1)
                qc_loc.y(0)
                qc_loc_instr = qc_loc.to_instruction()
                dag.substitute_node(node, qc_loc_instr, inplace=True)
            elif abs(angle - 1.5*np.pi) < threshold:
                qc_loc = QuantumCircuit(1)
                qc_loc.sdg(0)
                qc_loc.sxdg(0)
                qc_loc.s(0)
                qc_loc_instr = qc_loc.to_instruction()
                dag.substitute_node(node, qc_loc_instr, inplace = True)
        elif node.name == 'rz':
            angle = float(node.op.params[0])
            #substitute gates
            if abs(angle - 0) < threshold:
                dag.remove_op_node(node)
            elif abs(angle - np.pi/2) < threshold:
                qc_loc = QuantumCircuit(1)
                qc_loc.s(0)
                qc_loc_instr = qc_loc.to_instruction()
                dag.substitute_node(node, qc_loc_instr, inplace=True)
            elif abs(angle - np.pi) < threshold:
                qc_loc = QuantumCircuit(1)
                qc_loc.z(0)
                qc_loc_instr = qc_loc.to_instruction()
                dag.substitute_node(node, qc_loc_instr, inplace=True)
            elif abs(angle - 1.5*np.pi) < threshold:
                qc_loc = QuantumCircuit(1)
                qc_loc.sdg(0)
                qc_loc_instr = qc_loc.to_instruction()
                dag.substitute_node(node, qc_loc_instr, inplace=True)
        elif node.name == "x":
            qc_loc = QuantumCircuit(1)
            qc_loc.x(0)
            qc_loc_instr = qc_loc.to_instruction()
            dag.substitute_node(node, qc_loc_instr, inplace=True)
    return dag_to_circuit(dag).decompose()

def qiskit_to_stim(circuit):
    """
    Transform Qiskit QuantumCircuit into stim circuit.
    circuit (QuantumCircuit): Clifford-only circuit.

    Returns:
    (stim._stim_sse2.Circuit) stim circuit.
    """
    assert isinstance(circuit, QuantumCircuit), f"Circuit is not a Qiskit QuantumCircuit."
    allowed_gates = ["X", "Y", "Z", "H", "CX", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG"]
    stim_circ = stim.Circuit()
    # make sure right number of qubits in stim circ

    for i in range(circuit.num_qubits):
        stim_circ.append("I", [i])
    for instruction in circuit:
        gate_lbl = instruction.operation.name.upper()
        if gate_lbl == "BARRIER":
            continue
        elif gate_lbl == "SDG":
            gate_lbl = "S_DAG"
        elif gate_lbl == "SX":
            gate_lbl = "SQRT_X"
        elif gate_lbl == "SXDG":
            gate_lbl = "SQRT_X_DAG"
        assert gate_lbl in allowed_gates, f"Invalid gate {gate_lbl}."
        qubit_idc = [circuit.find_bit(qb)[0] for qb in instruction.qubits]
        stim_circ.append(gate_lbl, qubit_idc)
    return stim_circ

def replace_r_gates_with_t(circuit, num_replacements):
    # if no t gates
    if num_replacements == 0:
        return circuit
    
    # Find all RZ, RX, and RY gates in the circuit
    r_gates = []
    for instruction, qargs, _ in circuit.data:
        if isinstance(instruction, (RZGate, RXGate, RYGate)):
            r_gates.append((instruction, qargs))
    
    # If there are fewer R gates than requested replacements, adjust num_replacements
    num_replacements = min(num_replacements, len(r_gates))
    
    # Randomly select R gates to replace
    gates_to_replace = random.sample(r_gates, num_replacements)
    
    # Create a new circuit
    new_circuit = QuantumCircuit(circuit.num_qubits)
    
    # Copy the original circuit, replacing selected R gates with T gates
    for instruction, qargs, cargs in circuit.data:
        if (instruction, qargs) in gates_to_replace:
            new_circuit.t(qargs[0])
        else:
            new_circuit.append(instruction, qargs, cargs)
    
    return new_circuit
