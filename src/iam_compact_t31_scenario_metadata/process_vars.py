"""Functions to use for pre-processing variables for calculating indicators.

Functions
---------
add_missing_aggregates(
        iamdf: pyam.IamDataFrame,
        agg_var: str,
        component_vars: Optional[list[str]] = None,
) -> pyam.IamDataFrame
    Construct an aggregated variable by summing components in models/scenarios
    where the aggregated variable is missing.
"""
import typing as tp

import pandas as pd
import pyam



def _notnone[T](x: tp.Optional[T]) -> T:
    """Helper to ensure an object is not None.

    Returns the object if it is not None, raises a ValueError if it is.
    """
    if x is None:
        raise ValueError("Object is None")
    return x


def add_missing_aggregates(
        iamdf: pyam.IamDataFrame,
        agg_var: str,
        component_vars: tp.Optional[list[str]] = None,
) -> pyam.IamDataFrame:
    """Aggregate component variables in models/scenarios where the aggregate is missing.

    The function sums component variables (explicitly specified or inferred) and
    adds an aggregated variable in model/scenario combinations where the
    aggregated variable is missing. In models/scenarios where it is present,
    the data are returned unchanged.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The IamDataFrame to process.
    agg_var : str
        The name of the aggregated variable to construct.
    component_vars : list[str] | None, optional
        The names of the component variables to sum. If None, the function
        attempts to infer the components from the variable hierarchy (using the
        default behavior of the `pyam.IamDataFrame.aggregate` method).

    Returns
    -------
    pyam.IamDataFrame:
        The IamDataFrame with the aggregated variable added where missing.
    """
    # Split iamdf into a part that has and does not have the aggregated variable
    # First find the index for the models/scenarios that do have the
    # aggregated variable
    has_agg_var_index = _notnone(iamdf.filter(variable=agg_var)).index
    iamdf_agg_present: pyam.IamDataFrame \
        = _notnone(iamdf.filter(index=has_agg_var_index))
    iamdf_agg_missing: pyam.IamDataFrame \
        = _notnone(iamdf.filter(index=has_agg_var_index, keep=False))

    # Aggregate the missing part
    if component_vars is None:
        iamdf_agg_missing.aggregate(
            variable=agg_var,
            append=True,
        )
    else:
        iamdf_agg_missing.aggregate(
            variable=agg_var,
            components=component_vars,
            append=True,
        )
    # Concatenate the two parts
    iamdf_out: pyam.IamDataFrame = pyam.concat([
        iamdf_agg_present,
        iamdf_agg_missing,
    ])
    return iamdf_out

