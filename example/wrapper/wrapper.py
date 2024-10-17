import numpy as np
from qiskit_ibm_runtime.fake_provider import FakeMumbai
import sys
sys.path.append("../../")

from vqe_experiment import *


def main():
    budget = 500
    # molecule strings
    atom_strings = { 'h2':('H 0 0 0; H 0 0 1.00', 2),
                    #  'h6':('H 3.0000 0.0000 0; H 1.5000 2.5981 0; H -1.5000 2.5981 0; H -3.0000 0.0000 0; H -1.5000 -2.5981 0; H 1.5000 -2.5981 0', 3),
                    #  'h2o':('O 0 0 0; H 0.757 0.586 0; H -0.757 0.586 0', 7),
                    #  'cr2':('Cr 0 0 0; Cr 0 0 1.68', 32),
                    #  'n2':('N 0 0 0; N 0 0 1.0975', 10),
                    #  'nah':('Na 0 0 0; H 0 0 1.887', 6),
                    #  'h2_s1':('H 0 0 0; H 0 0 0.74; S 0 0 2.5', 11),
                    #  'beh2':('Be 0 0 0; H 0 0 1.32; H 0 0 -1.32', 10),
                    #  'Lih':('Li 0.0000 0.0000 0; H 1.6000 0.0000 0', 6)
                    }

    for key, value in atom_strings.items():
        atom = key
        atom_string = value[0]
        num_orbitals = value[1]


        coeffs, paulis, HF_bitstring = molecule(atom_string, num_orbitals)
        n_qubits = len(paulis[0])

        save_dir = "./"
        
        vqe_kwargs = {
            "ansatz_reps": 2,
            "init_last": False,
            "HF_bitstring": HF_bitstring
        }

        t_gates_max = 3
        for t in range(t_gates_max):
            result_file = str(t)+"_"+atom + ".txt"
            # run CAFQA
            cafqa_guess = [] # will start from all 0 parameters
            loss_file = str(t)+"_"+atom+"_cafqa_loss.txt"
            params_file = str(t)+"_"+atom+"_cafqa_params.txt"
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

        
            # VQE with CAFQA initialization
            shots = 8192
            loss_file = str(t)+"_"+atom+"_vqe_loss.txt"
            params_file = str(t)+"_"+atom+"_vqe_params.txt"
            vqe_energy, vqe_params = run_vqe(
                n_qubits=n_qubits,
                t_gates=t,
                coeffs=coeffs,
                paulis=paulis,
                param_guess=np.array(cafqa_params)*np.pi/2,
                budget=budget,
                shots=shots,
                mode="device_execution",
                backend=FakeMumbai(),
                save_dir=save_dir,
                loss_file=loss_file,
                params_file=params_file,
                vqe_kwargs=vqe_kwargs
            )
            with open(save_dir + result_file, "a") as res_file:
                res_file.write(f"VQE energy:\n{vqe_energy}\n")
                res_file.write(f"VQE params:\n{np.array(vqe_params)}\n\n")


if __name__ == "__main__":
    main()
