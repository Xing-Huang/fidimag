cdef extern from "nebm_spherical_lib.h":

    void normalise_spherical(double * a, int n)

    void normalise_images_spherical_C(double * y, int n_images,
                                      int n_dofs_image)

    double compute_distance_spherical(double * A, double * B, int n,
                                      int * material, int n_dofs_image_material
                                      )

cdef extern from "nebm_lib.h":

    void compute_image_distances(double * distances,
                                 double * path_distances,
                                 double * y,
                                 int n_images,
                                 int n_dofs_image,
                                 double (* compute_distance)(double *,
                                                             double *,
                                                             int,
                                                             int *,
                                                             int),
                                 int *  material,
                                 int n_dofs_image_material
                                 )

    void compute_tangents_C(double *tangents,
                            double *y,
                            double *energies,
                            int n_dofs_image,
                            int n_images
                            )

    void compute_effective_force_C(double * G,
                                   double * tangents,
                                   double * gradientE,
                                   double * spring_force,
                                   int * climbing_image,
                                   int n_images,
                                   int n_dofs_image)

def normalise_images(double [:] y,
                     n_images,
                     n_dofs_image
                     ):

    normalise_images_spherical_C(&y[0], n_images, n_dofs_image)

def image_distances_Spherical(double [:] distances,
                              double [:] path_distances,
                              double [:] y,
                              int n_images,
                              int n_dofs_image,
                              int [:] material,
                              int n_dofs_image_material
                              ):

    return compute_image_distances(&distances[0],
                                   &path_distances[0],
                                   &y[0],
                                   n_images,
                                   n_dofs_image,
                                   compute_distance_spherical,
                                   &material[0],
                                   n_dofs_image_material
                                   )
