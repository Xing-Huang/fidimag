double step_Verlet_C(double *restrict forces,
                     double *restrict forces_prev,
                     double *restrict velocities,
                     double *restrict velocities_new,
                     double *restrict y,
                     double t,
                     double h,
                     double mass,
                     int n_images,
                     int n_dofs_image,
                     double (* update_field) (double, double *)
                     );
