"""Module that defines `pea.Criterion` and `iam-validate` `CriterionTargetRange`
objects for the metadata.

Attributes
----------
change_criteria : dict[str, pea.ChangeOverTimeCriterion]
    `pathways_ensemble_analysis.ChangeOverTimeCriterion` objects, one for each
    metadata quantity that involves relative change over time. The keys are
    short codes for the criterion.
share_criteria : dict[str, pea.ShareCriterion]
    `pathways_ensemble_analysis.ShareCriterion` objects, one for each
    metadata quantity that involves the relative change of something
cumulative_criteria : dict[str, pea.AggregateCriterion]
    `pathways_ensemble_analysis.AggregateCriterion` objects, one for each
    metadata quantity that involves the cumulative sum or other aggregate of
    something
reference_year : int
    The base year used to measure changes. *NB!* No check is made that all
    scenarios have data for this year. If you change it, you need to check, or
    expect possibly silent errors.
obs_years : list[int]
    Years used in the metadata measures (e.g., change from `reference_year`
    until a given year).
ccs_end_year : int
    End year used specifically for the cumulative CCS measure.

Functions
---------
make_pct_change_criterion(reference_year, target_year, variable, name) -> pea.ChangeOverTimeCriterion
    Make a Criterion object that calculates change over time of something
make_share_criterion(year, variable_component, variable_total, year, name) -> pea.ShareCriterion
    Make a Criterion object that calculates the percentagewise share of something
make_cumulative_criterion(start_year, end_year, variable, name) -> pea.AggregateCriterion
    Make a Criterion object that calculates the cumulative sum of something
"""
import typing as tp

import pandas as pd
from pathways_ensemble_analysis.criteria.base import (
    AggregateCriterion,
    ChangeOverTimeCriterion,
    ShareCriterion,
)



reference_year: int = 2020
obs_years: list[int] = [2030, 2050]
ccs_end_year: int = 2100


def make_pct_change_criterion(
    reference_year: int,
    target_year: int,
    variable: str,
    name: str,
    region: str|list[str] = '*',
) -> ChangeOverTimeCriterion:
    """Make a Criterion object that calculates change over time.
    
    Parameters
    ----------
    reference_year : int
        The base year used to measure changes.
    target_year : int
        The year to measure change by
    variable : str
        The variable to measure change in.
    name : str
        The name of the criterion. Usually a longish name that includes the
        description of the variable and the base and target years.
    """
    criterion: ChangeOverTimeCriterion = ChangeOverTimeCriterion(
        criterion_name=name,
        year=target_year,
        variable=variable,
        reference_year=reference_year,
        region=region,
    )
    return criterion


def make_share_criterion(
    year: int,
    variable_component: str,
    variable_total: str,
    name: str,
    region: str|list[str] = '*',
) -> ShareCriterion:
    """Make a Criterion object that calculates the percentagewise share of something.
    
    Parameters
    ----------
    year : int
        The year to measure the share in.
    component_var : str
        The variable to measure the share of.
    base_var : str
        The variable to measure the share against.
    name : str
        The name of the criterion. Usually a longish name that includes the
        description of the variable and the year.
    """
    criterion: ShareCriterion = ShareCriterion(
        criterion_name=name,
        year=year,
        variable_component=variable_component,
        variable_total=variable_total,
        region=region,
    )
    return criterion


def make_cumulative_criterion(
    start_year: int,
    end_year: int,
    variable: str,
    name: str,
    region: str|list[str] = '*',
) -> AggregateCriterion:
    """Make a Criterion object that calculates the cumulative sum of something.
    
    Parameters
    ----------
    start_year : int
        The year to start the cumulative sum from.
    end_year : int
        The year to end the cumulative sum at.
    variable : str
        The variable to measure the cumulative sum of.
    name : str
        The name of the criterion. Usually a longish name that includes the
        description of the variable and the start and end years.
    """
    criterion: AggregateCriterion = AggregateCriterion(
        criterion_name=name,
        years=list(range(start_year, end_year + 1)),
        variable=variable,
        aggregation_function=pd.Series.sum,
        region=region,
    )
    return criterion


change_criteria_params: dict[str, tuple[str, str, int, int]] = {
    _key: (_name, _variable, _reference_year, _target_year)
    for _reference_year in (reference_year,) for _target_year in obs_years
    for _key, _name, _variable in [
        (
            f'pct_change_co2_{_reference_year}_{_target_year}',
            f'Change in CO2 emissions in {_target_year} (% rel to {reference_year})',
            'Emissions|CO2',
        ),
    ]
}

change_criteria: dict[str, ChangeOverTimeCriterion] = {
    _key: make_pct_change_criterion(
        reference_year=_reference_year,
        target_year=_target_year,
        variable=_variable,
        name=_name,
    )
    for _key, _args in change_criteria_params.items()
    for _name, _variable, _reference_year, _target_year in (_args,)
}
