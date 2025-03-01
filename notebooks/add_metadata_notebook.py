# %% [markdown]
# # Intro
# This notebook goes through the steps of adding emissions- and energy-related
# scenario metadata for IAM COMPACT T3.1 to a modell output file from
# [Van de Ven et al., 2023](https://doi.org/10.1038/s41558-023-01661-0),
# downloaded from Zenodo at
# [https://doi.org/10.5281/zenodo.7767192](https://doi.org/10.5281/zenodo.7767192).
# The file used is `global_ite2_allmodels.csv`.
#
# ## Get the data
#
# To get the data, go to the folder `/download` under the repository root and
# run the script `download_data.sh`. Alternatively, if you cannot run unix shell
# scripts, download the zip file from the Zenodo page referenced above, create a
# folder called `VanDeVenEtAl_2023_NCC_outputs`, unpack the zip file and move
# the unpacked contents into that folder.
#
# ## Run the code
#
# To run the code, you should create a virtual Python environment and install
# the repo as a Python package. Please contact Jan Ivar
# (jan.ivar.korsbakken@cicero.oslo.no) if you are unsure how to do that.
#

# %% [markdown]
# ### Import necessary packages
# %%
from iam_compact_t31_scenario_metadata.criteria_def import (
    change_criteria,
    change_criteria_params,
    cumulative_criteria,
    cumulative_criteria_params,
    share_criteria,
    share_criteria_params,
)
from iam_compact_t31_scenario_metadata.criteria_eval import (
    get_change_criterion_values,
    get_cumulative_criterion_values,
    get_share_criterion_values,
)

import itertools
from pathlib import Path

import pandas as pd
import pyam


# %% [markdown]
# ### Load data
#
# Set the path to the data and load it into a `pyam.IamDataFrame`. If the
# repository root is somewhere other than the parent folder of the folder where
# this notebook is located, or if you are running in an environment that doesn't
# set the path of the notebook as `__file__`, please set the path of the repo
# root folder manually below

# %%
repo_root: Path = Path(__file__).parents[1]
van_de_ven_folder: Path = repo_root / 'download' / 'VanDeVenEtAl_2023_NCC_outputs'

data_file_name: Path = Path('global_ite2_allmodels.csv')
data_file: Path = van_de_ven_folder / data_file_name

# %% [markdown]
# The CSV has a bunch of empty columns at the end of each row, and empty rows at
# the bottom (just commas with no data in between). So load it into a pandas
# DataFrame first, and remove all columns and rows that have only nulls. Also,
# one of the models appears to have added "UNDF" instead of NaN or empty data in
# some places, so treat that as a missing data value when reading the CSV.
# %%
df = pd.read_csv(data_file, na_values='UNDF') \
    .dropna(axis=1, how='all') \
    .dropna(axis=0, how='all')

# %% [markdown]
# Then load to an `IamDataFrame`
# %%
iamdf: pyam.IamDataFrame = pyam.IamDataFrame(df)

# %% [markdown]
# ## Evaluate the criteria
#
# The criteria have been loaded in the import statements at the top. Evaluate
# them here.

# %% [markdown]
# ### Evaluate the change criteria
# %%
change_values: dict[str, pd.Series] = {
    _key: get_change_criterion_values(iamdf=iamdf, criterion=_value)
    for _key, _value in change_criteria.items()
}

# %% [markdown]
# ### Evaluate the share criteria
# %%
share_values: dict[str, pd.Series] = {
    _key: get_share_criterion_values(iamdf=iamdf, criterion=_value)
    for _key, _value in share_criteria.items()
}

# %% [markdown]
# ### Evaluate the cumulative criteria
# %%
cumulative_values: dict[str, pd.Series] = {
    _key: get_cumulative_criterion_values(
        iamdf=iamdf,
        criterion=_value
    )
    for _key, _value in cumulative_criteria.items()
}

# %% [markdown]
# ## Create a joint DataFrame and add as metadata
#
# We now concatenate the individual Series above to a single indexed by the
# criterion name (in the `variable` index level), and then pivot to a DataFrame
# with one column for each criterion.

# %% [markdown]
# ### Concatenate all Series
#
# First create a single Series that concatenates all the Series from each of the
# three dicts above
# %%
all_values: pd.Series = pd.concat(
    itertools.chain(
        change_values.values(),
        share_values.values(),
        cumulative_values.values(),
    ),
)

# %% [markdown]
# Then find the sum of the lengths of the original Series, and check that it
# equals the length of the concatenated Series, to make sure nothing has been
# overwritten during the concatenation. Finally, also double check that the
# index of the concatenated Series contains only unique indexes, with no
# dupliates.
# %%
orig_length: int = sum(len(s) for s in itertools.chain(
    change_values.values(),
    share_values.values(),
    cumulative_values.values(),
))
assert orig_length == len(all_values)
assert all_values.index.is_unique


# %% [markdown]
# Unstack to a DataFrame to get a table with one column for each criterion.
# Drop the unit index level first, we assume that the unit information is
# contained in the criteria name so that viewers can look at the colun title
# afterwards to know what unit is used.
# %%
all_values_df: pd.DataFrame = all_values.droplevel('unit').unstack('variable')

# %% [markdown]
# ## Write full data and metadata to Excel
#
# Specify the path to save to in the cell below, then run the final cell to save
# the output.
# %%
output_filename: Path = data_file_name \
    .with_stem(data_file_name.stem + '_with_metadata') \
        .with_suffix('.xlsx')
xlsx_output_path: Path = repo_root / 'output' / output_filename

# %% [markdown]
# Set the DataFrame as metadata on `iamdf` in order to write everything to Excel
iamdf_with_meta: pyam.IamDataFrame = iamdf.copy()
iamdf_with_meta.meta = all_values_df

# %% [markdown]
# Write the output to an Excel file
# %%
iamdf_with_meta.to_excel(xlsx_output_path)
