#include "clib.h"

void compute_uniform_exch(double *spin, double *field, double J, double dx,
		double dy, double dz, int nx, int ny, int nz) {

	int i, j, k;
	int index, id;
	double tmp[3];

	int nyz = ny * nz;
	int nxyz = nx * nyz;

	for (i = 0; i < nx; i++) {
		for (j = 0; j < ny; j++) {
			for (k = 0; k < nz; k++) {

				index = i * nyz + j * nz + k;
				tmp[0] = 0;
				tmp[1] = 0;
				tmp[2] = 0;

				if (i > 0) {
					id = index - nyz;
					tmp[0] += J * spin[id];
					id += nxyz;
					tmp[1] += J * spin[id];
					id += nxyz;
					tmp[2] += J * spin[id];
				}

				if (j > 0) {
					id = index - nz;
					tmp[0] += J * spin[id];
					id += nxyz;
					tmp[1] += J * spin[id];
					id += nxyz;
					tmp[2] += J * spin[id];
				}

				if (k > 0) {
					id = index - 1;
					tmp[0] += J * spin[id];
					id += nxyz;
					tmp[1] += J * spin[id];
					id += nxyz;
					tmp[2] += J * spin[id];
				}

				if (i < nx - 1) {
					id = index + nyz;
					tmp[0] += J * spin[id];
					id += nxyz;
					tmp[1] += J * spin[id];
					id += nxyz;
					tmp[2] += J * spin[id];
				}

				if (j < ny - 1) {
					id = index + nz;
					tmp[0] += J * spin[id];
					id += nxyz;
					tmp[1] += J * spin[id];
					id += nxyz;
					tmp[2] += J * spin[id];
				}

				if (k < nz - 1) {
					id = index + 1;
					tmp[0] += J * spin[id];
					id += nxyz;
					tmp[1] += J * spin[id];
					id += nxyz;
					tmp[2] += J * spin[id];
				}

				field[index] = tmp[0];
				index += nxyz;
				field[index] = tmp[1];
				index += nxyz;
				field[index] = tmp[2];
			}
		}
	}

}