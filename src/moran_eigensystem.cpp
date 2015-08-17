#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <iostream>
#include <gmpxx.h>
#include "mpq_support.h"

typedef struct 
{
    MatrixXq U, Uinv;
    Eigen::VectorXi D;
} 
MoranEigensystem;

Eigen::SparseMatrix<mpq_class, Eigen::RowMajor> moran_rate_matrix(int N, int a)
{
    Eigen::SparseMatrix<mpq_class, Eigen::RowMajor> ret(N + 1, N + 1);     
    for (int i = 0; i < N + 1; ++i)
    {
        mpq_class sm = 0, b;
        if (i > 0)
        {
            b = (2_mpq - a) * i + i * (N - i) / 2_mpq;
            ret.insert(i, i - 1) = b;
            sm += b;
        }
        if (i < N)
        {
            b = a * (N - i) + i * (N - i) / 2_mpq;
            ret.insert(i, i + 1) = b;
            sm += b;
        }
        ret.insert(i, i) = -sm;
    }
    return ret;
}

VectorXq solve(const Eigen::SparseMatrix<mpq_class, Eigen::RowMajor> &M)
// VectorXq solve(const Eigen::SparseMatrixBase<Derived> &M)
{
    int n = M.rows();
    VectorXq ret(n);
    ret.setZero();
    ret(n - 1) = 1;
    for (int i = n - 2; i > -1; --i)
        ret(i) = (M.row(i + 1) * ret).sum() / -M.coeff(i + 1, i);
    return ret;
}

MoranEigensystem compute_moran_eigensystem(int N)
{
    MoranEigensystem ret;
    ret.D = Eigen::VectorXi::Zero(N + 1);
    ret.U = MatrixXq::Zero(N + 1, N + 1);
    ret.Uinv = MatrixXq::Zero(N + 1, N + 1);
    for (int i = 2; i < N + 3; ++i)
    {
        ret.D(i) = -(i * (i - 1) / 2 - 1);
    }
}

int main(int argc, char** argv)
{
    int n = atoi(argv[1]);
    Eigen::SparseMatrix<mpq_class, Eigen::RowMajor> M = moran_rate_matrix(n, 0), Mt, I(n + 1, n + 1), A;
    Mt = M.transpose();
    MatrixXq B(n + 1, n + 1), C(n + 1, n + 1);
    B.setZero();
    C.setZero();
    C(0, 0) = 1_mpq;
    I.setIdentity();
    VectorXq D(n + 1), D1;
    for (int k = 2; k < n + 3; ++k)
    {
        std::cout << k << " " << std::flush;
        int rate = -(k * (k - 1) / 2 - 1);
        D(k - 2) = rate;
        A = M - rate * I;
        B.col(k - 2) = solve(A);
        if (k > 2)
        {
            A = Mt - rate * I;
            C.row(k - 2).tail(n) = solve(A.bottomRightCorner(n, n));
            C(k - 2, 0) = -C(k - 2, 1) * A.coeff(0, 1) / A.coeff(0, 0);
        }
    }
    D1 = (C * B).diagonal().cwiseInverse();
    std::cout << "D1 " << std::flush;
    B *= D1.asDiagonal();
    std::cout << "B " << std::flush;
    std::cout << std::endl;
    // std::cout << (B * D.asDiagonal() * C).template cast<double>() << std::endl;
}
