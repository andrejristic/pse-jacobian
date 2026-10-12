"""Structural checks (Unit 3 / Edge): quasi-homogeneity and dimension generalization."""
import sympy as sp

from . import keller


def check_equivariance(components, variables, grading, component_weights):
    """Verify C*-equivariance: under x_i -> lambda^{w_i} x_i, each component scales as
    lambda^{d_j}. Returns (all_ok, per_component residuals).

    grading: dict var -> weight w_i (integer)
    component_weights: iterable d_j aligned with components
    """
    lam = sp.symbols('lambda', positive=True)
    sub = {v: lam**grading[v] * v for v in variables}
    results = []
    all_ok = True
    for comp, d in zip(components, component_weights):
        residual = sp.simplify(comp.subs(sub) - lam**d * comp)
        ok = residual == 0
        all_ok = all_ok and ok
        results.append((d, residual, ok))
    return all_ok, results


def generalize_to_dimension(components, variables, n_extra):
    """Build F x id on n_extra untouched coordinates and return (new_components,
    new_vars, det). The Jacobian determinant must be unchanged (the identity block
    contributes 1), demonstrating the counterexample lifts to all higher dimensions.
    """
    extra = sp.symbols(f'w0:{n_extra}')
    new_vars = tuple(variables) + tuple(extra)
    new_components = tuple(components) + tuple(extra)
    det = keller.jacobian_det_symbolic(new_components, new_vars)
    return new_components, new_vars, det
