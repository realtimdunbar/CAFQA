from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit import QuantumCircuit
import numpy as np
import stim

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

import random

from qiskit import QuantumCircuit
import random

def insert_random_t_gates(circuit: QuantumCircuit, num_gates: int) -> QuantumCircuit:
    """
    Randomly inserts a given number of T gates into the provided quantum circuit.
    
    Args:
    circuit (QuantumCircuit): The input quantum circuit.
    num_gates (int): The number of T gates to insert.
    
    Returns:
    QuantumCircuit: A new quantum circuit with randomly inserted T gates.
    """
    # Create a copy of the input circuit to avoid modifying the original
    new_circuit = circuit.copy()
    
    # Get the number of qubits in the circuit
    num_qubits = new_circuit.num_qubits
    
    # Get the current number of gates in the circuit
    num_operations = len(new_circuit.data)
    
    # Generate random insertion points
    insertion_points = random.sample(range(num_operations + 1), num_gates)
    
    # Sort the insertion points in descending order to maintain the relative positions
    insertion_points.sort(reverse=True)
    
    # Insert T gates at the random points
    for point in insertion_points:
        qubit = random.randint(0, num_qubits - 1)
        new_circuit.t(qubit)
        new_circuit.data.insert(point, new_circuit.data.pop())
    
    return new_circuit


from qiskit import QuantumCircuit
from qiskit.circuit.library import (
    HGate, SGate, SdgGate, XGate, YGate, ZGate, 
    CXGate, CYGate, CZGate, SwapGate
)
from qiskit.quantum_info import Operator
import numpy as np

def incorporate_t_gates(ansatz: QuantumCircuit, num_t_gates: int) -> QuantumCircuit:
    """
    Incorporate a specified number of T gates into the input ansatz,
    replacing existing Clifford gates while maintaining the original functionality.
    
    Args:
    ansatz (QuantumCircuit): The input ansatz to modify
    num_t_gates (int): The target number of T gates to incorporate
    
    Returns:
    QuantumCircuit: The modified ansatz with incorporated T gates
    """
    
    modified_ansatz = QuantumCircuit(ansatz.num_qubits)
    t_gates_added = 0
    
    def add_t_gate():
        nonlocal t_gates_added
        if t_gates_added < num_t_gates:
            modified_ansatz.t(qargs)
            t_gates_added += 1
        else:
            modified_ansatz.s(qargs)  # S = T^2, so we use S if we've reached our T gate limit
    
    for inst, qargs, _ in ansatz.data:
        if isinstance(inst, HGate):
            # H = THTHTHt
            add_t_gate()
            modified_ansatz.h(qargs)
            add_t_gate()
            modified_ansatz.h(qargs)
            add_t_gate()
            modified_ansatz.h(qargs)
            add_t_gate()
        elif isinstance(inst, SGate):
            # S = T^2
            add_t_gate()
            add_t_gate()
        elif isinstance(inst, SdgGate):
            # S† = (T†)^2
            modified_ansatz.tdg(qargs)
            modified_ansatz.tdg(qargs)
        elif isinstance(inst, XGate):
            # X = HtH
            modified_ansatz.h(qargs)
            add_t_gate()
            modified_ansatz.h(qargs)
        elif isinstance(inst, YGate):
            # Y = SX = StHtH
            add_t_gate()
            add_t_gate()
            modified_ansatz.h(qargs)
            add_t_gate()
            modified_ansatz.h(qargs)
        elif isinstance(inst, ZGate):
            # Z = S^2 = T^4
            add_t_gate()
            add_t_gate()
            add_t_gate()
            add_t_gate()
        elif isinstance(inst, CXGate):
            # CX (CNOT) = (I⊗H) * CZ * (I⊗H)
            modified_ansatz.h(qargs[1])
            modified_ansatz.cz(qargs[0], qargs[1])
            modified_ansatz.h(qargs[1])
        elif isinstance(inst, CYGate):
            # CY = (I⊗S†) * CX * (I⊗S)
            modified_ansatz.sdg(qargs[1])
            modified_ansatz.cx(qargs[0], qargs[1])
            add_t_gate()
            add_t_gate()
        elif isinstance(inst, CZGate):
            # CZ remains as is, as it's already a Clifford gate
            modified_ansatz.cz(qargs[0], qargs[1])
        elif isinstance(inst, SwapGate):
            # SWAP = CX * CX * CX
            modified_ansatz.cx(qargs[0], qargs[1])
            modified_ansatz.cx(qargs[1], qargs[0])
            modified_ansatz.cx(qargs[0], qargs[1])
        else:
            # For other gates, we'll just append them as-is
            modified_ansatz.append(inst, qargs)
    
    # If we haven't added enough T gates, add more at the end
    while t_gates_added < num_t_gates:
        qubit = t_gates_added % ansatz.num_qubits
        modified_ansatz.t(qubit)
        modified_ansatz.tdg(qubit)
        t_gates_added += 1
    
    return modified_ansatz
