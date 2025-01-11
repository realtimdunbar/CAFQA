import numpy as np
from qiskit_ibm_runtime.fake_provider import FakeMumbai
import sys
sys.path.append("../../")

from vqe_experiment import *
from vqe_helpers import *


def main():
    budget = 250
    # molecule strings
    atom_strings = {'h2':['H', 'H']
                    # 'h6':['H', 'H', 'H', 'H', 'H', 'H'],
                    # 'NaH':['Na', 'H'],
                    # 'LiH':['Li', 'H']
                    }
    
    for key, value in atom_strings.items():
        atom = key
        atoms = value
        bond_lengths = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]

        for bond_length in bond_lengths:
            mol = build_molecule(atoms, bond_length)

            num_orbitals = mol.nao

            atom_string = get_atom_string(mol)

            coeffs, paulis, HF_bitstring = molecule(atom_string, num_orbitals)
            n_qubits = len(paulis[0])

            save_dir = "./"
            
            vqe_kwargs = {
                "ansatz_reps": 2,
                "init_last": False,
                "HF_bitstring": HF_bitstring
            }

            # params
            t_gates = [0]

            for t in t_gates:
                result_file = str(bond_length)+"_"+str(t)+"_"+atom + "_result.txt"
                # run CAFQA
                cafqa_guess = [] # will start from all 0 parameters
                loss_file = str(bond_length)+"_"+str(t)+"_"+atom+"_cafqa_loss.txt"
                params_file = str(bond_length)+"_"+str(t)+"_"+atom+"_cafqa_params.txt"
                cafqa_energy, cafqa_params = run_cafqa(
                    n_qubits=n_qubits,
                    t_gates=t,
                    coeffs=coeffs,
                    paulis=paulis,
                    param_guess=cafqa_guess,
                    budget=budget,
                    save_dir=save_dir,
                    loss_file=loss_file,
                    params_file=params_file,
                    vqe_kwargs=vqe_kwargs
                )
                with open(save_dir + result_file, "w") as res_file:
                    res_file.write(f"CAFQA energy:\n{cafqa_energy}\n")
                    res_file.write(f"CAFQA params (x pi/2):\n{np.array(cafqa_params)}\n\n")


if __name__ == "__main__":
    main()
