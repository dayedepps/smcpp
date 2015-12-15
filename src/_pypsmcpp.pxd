from libcpp.vector cimport vector
from libcpp.pair cimport pair
from libcpp.map cimport map
from libcpp cimport bool

cdef extern from "common.h":
    cdef cppclass adouble:
        pass
    cdef cppclass Matrix[T]:
        int rows()
        int cols()
    cdef double toDouble(const adouble &)
    void init_eigen()
    void fill_jacobian(const adouble &, double*)
    void store_matrix[T](const Matrix[T] *, T*)
    void store_admatrix(const Matrix[adouble]&, int, double*, double*)
    void doProgress(bool)

ctypedef Matrix[double]* pMatrixD
ctypedef Matrix[float]* pMatrixF
ctypedef Matrix[adouble]* pMatrixAd

cdef extern from "inference_manager.h":
    ctypedef vector[vector[double]] ParameterVector
    cdef cppclass InferenceManager:
        InferenceManager(const int, const vector[int],
                const vector[int*], const vector[double], const int*, const int, 
                const double, const double, const int)
        void setParams_d(const ParameterVector)
        void setParams_ad(const ParameterVector, vector[pair[int, int]] derivatives)
        void Estep()
        vector[double] loglik(double)
        vector[adouble] Q(double)
        double R(const ParameterVector, double t)
        bool debug
        bool hj
        double getRegularizer()
        vector[pMatrixF] getXisums()
        vector[pMatrixAd] getBs()
        Matrix[adouble]& getPi()
        Matrix[adouble]& getTransition()
        Matrix[adouble]& getEmission()
        Matrix[adouble]& getMaskedEmission()
        vector[vector[pair[bool, map[pair[int, int], int]]]] getBlockKeys()
    Matrix[T] sfs_cython[T](int, const ParameterVector&, double, double, double)
    Matrix[T] sfs_cython[T](int, const ParameterVector&, double, double, double, vector[pair[int, int]])
