import pytest
import ad
import numpy as np

import smcpp
from smcpp import util
from smcpp.jcsfs import JointCSFS
from smcpp.model import SMCModel, PiecewiseModel

@pytest.fixture
def model1():
    s = np.diff(np.logspace(np.log10(.001), np.log10(4), 4))
    ret = SMCModel(s, np.logspace(np.log10(.001), np.log10(4), 5))
    ret[:] = np.log(np.arange(1, 6)[::-1])
    ret[:] = 0.
    return ret

@pytest.fixture
def model2():
    s = np.diff(np.logspace(np.log10(.001), np.log10(4), 4))
    ret = SMCModel(s, np.logspace(np.log10(.001), np.log10(4), 5))
    ret[:] = np.log(np.arange(1, 6))
    ret[:] = 0.
    return ret

@pytest.fixture
def jcsfs():
    return JointCSFS(5, 2, 2, 0, [0.0, 0.5, 1.0, np.inf])

def _cumsum0(x):
    return np.concatenate([[0.], np.cumsum(x)])

def _concat_models(model1, model2, split):
    # Return a model which is model1 before split and model2 after it.
    ary = []
    for m in (model1, model2):
        a = m.stepwise_values()
        cs = _cumsum0(m.s)
        cs[-1] = np.inf
        ip = np.searchsorted(cs, split)
        cs = np.insert(cs, ip, split)
        sp = np.diff(cs)
        ap = np.insert(a, ip, a[ip - 1])
        sp[-1] = 1.
        ary.append((sp, ap, ip))
    s, a = [np.concatenate([ary[1][i][:ary[1][2]], ary[0][i][ary[0][2]:]]) for i in [0, 1]]
    return PiecewiseModel(s, a, [])
np.set_printoptions(precision=3, linewidth=100)

def _test_d(model1, model2):
    ts = [0.0, 0.5, 1.0, np.inf]
    split = 0.25
    n1 = 10 
    n2 = 8
    j = JointCSFS(n1, n2, 2, 0, ts, 100)
    ders = model1[:3] = ad.adnumber(model1[:3])
    j0 = j.compute(model1, model2, split)
    model1.reset_derivatives()
    for i in range(3):
        model1[i] += 1e-8
        j1 = j.compute(model1, model2, split)
        model1[i] -= 1e-8
        for x, y in zip(j0.flat, j1.flat):
            print(x.d(ders[i]), (y - x) * 1e-8)
    assert False
    

def test_marginal_pop1(model1, model2):
    ts = [0., 1., 2., np.inf]
    n1 = 5
    n2 = 10
    j = JointCSFS(n1, n2, 2, 0, ts, 1000)
    for split in [0.1, 0.5, 1., 1.5, 2.5]:
        jc = j.compute(model1, model2, split)
        for t1, t2, jjc in zip(ts[:-1], ts[1:], jc):
            A1 = smcpp._smcpp.raw_sfs(model1, n1, t1, t2).astype('float')
            A2 = jjc.sum(axis=(-1, -2)).astype('float')
            assert np.allclose(A1.flat[1:-1], A2.flat[1:-1], 1e-1, 0)

def test_marginal_pop2(model1, model2):
    n1 = 8
    n2 = 10
    j = JointCSFS(n1, n2, 2, 0, [0.0, np.inf], 100)
    for split in [0.1, 0.25, 0.5, 0.75, 1.0, 2.0]:
        true_model2 = _concat_models(model1, model2, split)
        csfs = smcpp._smcpp.raw_sfs(true_model2, n2 - 2, 0., np.inf)
        A1 = util.undistinguished_sfs(csfs).astype('float')[1:]
        jc = j.compute(model1, model2, split)[0]
        A2 = jc.sum(axis=(0, 1, 2)).astype('float')[1:-1]
        assert np.allclose(A1, A2, 1e-1, 0)


def test_equal_py_c(model1, model2):
    ts = [0., 0.5, 1., 2., np.inf]
    n1 = 7
    n2 = 5
    py_jcsfs = JointCSFS(n1, n2, 2, 0, ts, 1000)
    model = smcpp.model.SMCTwoPopulationModel(model1, model2, 0.)
    for split in ts[1:-1]:
        j1 = py_jcsfs.compute(model1, model2, split)
        model.split = split
        j2 = np.array(smcpp._smcpp.joint_csfs(n1, n2, model, ts, 1000)).astype('float')
        assert np.allclose(j1, j2, 1e-1, 0)


# def test_jcsfs(jcsfs, model1, model2):
#     jcsfs.compute(model1, model2, 0.25)
