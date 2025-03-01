"""Module for applying criteria from the `criteria_def` module.

Applying the `Criterion` objects from the collections in the `criteria_def`
module requires special functions defined here.
`pathways_ensemble_analysis.Criterion` as implemented in version 1.1.0 removes
region names and units in the returned Series from `Criterion.get_values`, and
the functions here are therefore needed to modify the behavior of that method
to preserve region coordinates, and apply the correct units if needed.

Functions
---------
get_change_criterion_values(iamdf, criterion) -> pandas.Series
    Get values for an IamDataFrame using a Criterion from
    `.criteria_defs.change_criteria`.
get_share_criterion_values(iamdf, criterion) -> pandas.Series
    Get values for an IamDataFrame using a Criterion from
    `.criteria_defs.share_criteria`.
get_cumulative_criterion_values(iamdf, criterion) -> pandas.Series
    Get values for an IamDataFrame using a Criterion from
    `.criteria_defs.share_criteria`.
criterion_eval_return(keep_regions, unit) -> context manager
    Return a context manager that controls whether or not regions should be kept
    in calls to `Criterion.get_values`, and whether and what unit to include. In
    the current version, this only affects the behavior of `Criterion`
    subclasses from the `pathways_ensemble_analysis.criteria.base` module. Note
    that this context manager relies on implementation details in the
    `pathways_ensemble_analysis` package, and may therefore break or need
    updates if those details change in that package.
"""
import contextlib
import typing as tp

import pandas as pd
import pyam

from pathways_ensemble_analysis.criteria.base import (
    ChangeOverTimeCriterion,
    AggregateCriterion,
    ShareCriterion,
)



keep_name: bool = True


def get_change_criterion_values(
    iamdf: pyam.IamDataFrame, criterion: ChangeOverTimeCriterion
) -> pd.Series:
    """Get values for an IamDataFrame using a Criterion from
    `.criteria_defs.change_criteria`.
    """
    with criterion_eval_return(
            keep_regions=True,
            unit='%',
            keep_name=keep_name,
    ):
        values: pd.Series = criterion.get_values(iamdf)
    return values * 100.0


def get_share_criterion_values(
    iamdf: pyam.IamDataFrame, criterion: ShareCriterion
) -> pd.Series:
    """Get values for an IamDataFrame using a Criterion from
    `.criteria_defs.share_criteria`.
    """
    with criterion_eval_return(
            keep_regions=True,
            unit='%',
            keep_name=keep_name,
    ):
        values: pd.Series = criterion.get_values(iamdf)
    return values * 100.0


def get_cumulative_criterion_values(
    iamdf: pyam.IamDataFrame, criterion: AggregateCriterion
) -> pd.Series:
    """Get values for an IamDataFrame using a Criterion from
    `.criteria_defs.cumulative_criteria`.
    """
    with criterion_eval_return(
            keep_regions=True,
            unit=True,
            keep_name=keep_name,
    ):
        values: pd.Series = criterion.get_values(iamdf)
    return values


@contextlib.contextmanager
def criterion_eval_return(
    keep_regions: bool,
    unit: str|bool = False,
    keep_name: bool = False,
) -> tp.Generator[None]:
    """Preserve region and/or set units on return from `pea.Criterion.get_values`.

    The function returns a context manager that makes `pea.Criterion.get_values`
    preserve regions and/or preserve or set a custom unit on returned
    `pandas.Series`. Specifically, it modifies the behavior of the
    `pea.utils.format_value_series` function, which the `Criterion` classes in
    `pathways_ensemble_analysis.criteria.base` call at the end of their
    `.get_values` methods (as of version 1.1.0). That function simply drops
    the `region` and `unit` index levels from the returned Series and sets its
    `name` attribute to `None`. The context manager replaces it temporarily with
    a modified function.

    Note that this context manager may not work with other classes than those
    defined in `pathways_ensemble_analysis.criteria.base`.

    Parameters
    ----------
    keep_regions : bool
        Whether to keep region information in the Series returned from
        `Criterion.get_values`.
    unit : str or bool, optional
        Whether to keep units, or what to set them to. Can be a bool or string.
        If False (the default), the `unit` index level is dropped, as in the
        standard implementation of `Criterion.get_values`. If True, the original
        index level is kept. If a string, the `unit` index level is kept, and
        the values are set to the provided string. The last option is often
        needed because the returned values often have logical units that differ
        from the underlying veriable(s) (e.g., calculating ratios or relative
        changes), and `Criterion.get_values` does not usually try to infer the
        correct units (since the standard implementation drops them anyway).
        *NB!* The string value is used for all rows, and no check is made on
        whether all rows had the same value for `unit` to begin with.
    keep_name : bool
        Whether to keep the `.name` attribute of the returned Series. The
        standard implementation sets it to None before returning. Optional, by
        default False.
    """
    import pathways_ensemble_analysis.criteria.base as pea_crit_base
    original_format_value_series = pea_crit_base.format_value_series

    def new_format_value_series(series: pd.Series) -> pd.Series:
        if not isinstance(series, pd.Series):
            raise TypeError(
                '`series` must be a pandas.Series.'
            )
        orig_name: tp.Final = series.name
        if keep_regions == False:
            series = series.droplevel('region')
        elif keep_regions != True:
            raise ValueError(
                '`keep_regions` must be either True or False.'
            )
        if unit == False:
            series = series.droplevel('unit')
        elif isinstance(unit, str):
            series_frame: pd.DataFrame = series.reset_index('unit', drop=False)
            series_frame['unit'] = unit
            series = (y := series_frame.set_index('unit', append=True)) \
                [y.columns[0]]
            del series_frame
        elif unit != True:
            raise ValueError(
                '`unit` must be True, False or a string.'
            )
        if keep_name != False:
            series.name = None
        elif keep_name == True:
            series.name = orig_name
        else:
            raise ValueError(
                '`keep_name` must be either True or False.'
            )
        return series

    pea_crit_base.format_value_series = new_format_value_series
    try:
        yield
    finally:
        pea_crit_base.format_value_series = original_format_value_series
