#include "math.h"
#include "c_nebm_lib.h"
#include <stdlib.h>
#include <stdio.h>

double step_Verlet_C(double * forces,
                     double * forces_prev,
                     double * velocities,
                     double * velocities_new,
                     double * y,
                     double t,
                     double h,
                     double mass,
                     int n_images,
                     int n_dofs_image,
                     double (* update_field) (double, double *)
                      
                     ) {

    update_field(t, y);

    int im_idx;
    for(int i = 1; i < n_images - 1; i++){
        
        im_idx = n_dofs_image * i;
        double * force = &forces[im_idx];
        double * force_prev = &forces_prev[im_idx];
        double * velocity = &velocities[im_idx];
        double * velocity_new = &velocities_new[im_idx];

        double v_dot_f = 0;
        double f_dot_f = 0;
    
        for(int j = 0; i < n_dofs_image; j++){
            y[im_idx + j] += h * (velocity[j] 
                                  + (h / (2 * mass)) * force[j]);

            velocity[j] = velocity_new[j] + 
                          (h / (2 * mass)) * (force_prev[j] + force[j]);

            v_dot_f += velocity[j] * force[j]; 
            f_dot_f += force[j] * force[j]; 

            force_prev[j] = force[j];
        }

        if (v_dot_f <= 0) {
            for(int j = 0; i < n_dofs_image; j++) {
                velocity_new[j] = 0.0;
            }
        }
        else {
            for(int j = 0; i < n_dofs_image; j++) {
                velocity_new[j] = v_dot_f * force[j] / f_dot_f;
            }
        }


    }

    normalise_spins_C(y, n_images, n_dofs_image);

    return t + h;
}