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
cumulative_end_years: list[int] = [2100]


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
    region : str | list[str]
        The region to filter on (passed as `region=region` to
        `pyam.IamdDataFrame.filter`)
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
    variable_total : str
        The variable to measure the share against.
    name : str
        The name of the criterion. Usually a longish name that includes the
        description of the variable and the year.
    region : str | list[str]
        The region to filter on (passed as `region=region` to
        `pyam.IamdDataFrame.filter`)
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
    unit: str|None,
    cumulative_unit: str|None,
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
    region : str | list[str]
        The region to filter on (passed as `region=region` to
        `pyam.IamdDataFrame.filter`)
    unit : str|None,
        The unit to convert to before aggregating
    cumulative_unit : str|None
        The cumulative unit to set on the output. This should typically be
        `unit` with the "per time" part removed. E.g., if `unit` is "Gt CO2 /
        yr", `cumulative_unit` should be "Gt CO2". *NB!* Note that this
        parameter only affects what unit is set in the `unit` index level of
        the output, i.e., it is just used for labelling. It does not trigger any
        unit conversion. It is the responsibility of the caller to ensure that
        `unit` and `cumulative_unit` are consistent.
    """
    criterion: AggregateCriterion = AggregateCriterion(
        criterion_name=name,
        years=list(range(start_year, end_year + 1)),
        variable=variable,
        aggregation_function=pd.Series.sum,
        unit=unit,
        region=region,
    )
    criterion._cumulative_unit: str|None = cumulative_unit
    return criterion


change_criteria_params: dict[str, tuple[str, str, int, int]] = {
    f'pct_change_{_var_key}_{_reference_year}_{_target_year}': (
        f'Change in {_var_descr} in {_target_year} (% change rel to {_reference_year})',
        _variable,
        _reference_year,
        _target_year
    )
    for _reference_year in (reference_year,) for _target_year in obs_years
    for _var_key, _var_descr, _variable in [
        (
            'co2',
            'CO2 emissions',
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


share_criteria_params: dict[str, tuple[str, str, str, int]] = {
    f'share_{_comp_var_key}_{_year}': (
        f'{_comp_var_descr} share in {_tot_var_descr} in {_year} (%)',
        _comp_variable,
        _tot_variable,
        _year
    )
    for _year in obs_years
    for _comp_var_key, _comp_var_descr, _comp_variable, _tot_var_descr, _tot_variable in [
        (
            'fe_ind',
            'Electricity',
            'Final Energy|Industry|Electricity',
            'Final Energy, Industrial sector',
            'Final Energy|Industry',
        ),
        (
            'fe_bldng',
            'Electricity',
            'Final Energy|Residential and Commercial|Electricity',
            'Final Energy, Buildings sector',
            'Final Energy|Residential and Commercial',
        ),
    ]
}

share_criteria: dict[str, ShareCriterion] = {
    _key: make_share_criterion(
        year=_year,
        variable_component=_comp_variable,
        variable_total=_tot_variable,
        name=_name,
    )
    for _key, _args in share_criteria_params.items()
    for _name, _comp_variable, _tot_variable, _year in (_args,)
}


cumulative_criteria_params: dict[str, tuple[str, str, int, int, str|None, str|None]] = {
    f'cumulative_{_var_key}_{_start_year}_{_end_year}': (
        f'Cumulative {_var_descr} from {_start_year} until {_end_year} ({_cumulative_unit})',
        _variable,
        _start_year,
        _end_year,
        _unit,
        _cumulative_unit,
    )
    for _start_year in (reference_year,) for _end_year in cumulative_end_years
    for _var_key, _var_descr, _variable, _unit, _cumulative_unit in [
        (
            'co2',
            'CO2 emissions',
            'Emissions|CO2',
            'Gt CO2 / yr',
            'Gt CO2',
        ),
    ]
}

cumulative_criteria: dict[str, AggregateCriterion] = {
    _key: make_cumulative_criterion(
        start_year=_start_year,
        end_year=_end_year,
        variable=_variable,
        name=_name,
        unit=_unit,
        cumulative_unit=_cumulative_unit,
    )
    for _key, _args in cumulative_criteria_params.items()
    for _name, _variable, _start_year, _end_year, _unit, _cumulative_unit in (_args,)
}
