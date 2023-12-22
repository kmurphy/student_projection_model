import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', None)

from IPython.display import display, Markdown
import glob

REPORT_OPTIONS = {
    "Students__Multi": ["Row", "Column", "Year", "Domicile", "Mode of Study", "Gender", "Age Group", "New Entrant"],
    "Students__Geographical": ["Age Group", "Course Level", "Gender", "Institute", "New Entrant", "Programme Type", "Mode of Study"],
}


def year(a_year):
    return int(a_year[:4])

def previous_ayear(ayear):
    return format_ayear(int(format_ayear(ayear)[:4])-1)

def next_ayear(ayear):
    return format_ayear(int(format_ayear(ayear)[:4])+1)

def format_ayear(y):
    try:
        y = int(y)
        if y<99: return f"20{y}/{y+1:02d}"
        if y<9999: return f"{y}/{(y+1)%100:02d}"
        if y<999999: return f"{y//100}/{(y//100+1)%100:02d}"
    except:
        if "/" in y: return format_ayear(y.split("/")[0])
        return y


def get_dataset(filename, melt=False, verbose=False, debug=False):
    
    basename = filename.rsplit("/")[-1].split(".")[0]
    
    if verbose: display(Markdown(f"**Report**:\n\n{basename}"))

    report, option_values = basename.split("_-_")
    option_values = option_values.split("__")
    
    assert len(option_values)==len(REPORT_OPTIONS[report])
    options = {k:v for k,v in zip(REPORT_OPTIONS[report], option_values)}

    if "Year" in options:
        options["Year"] = format_ayear(options["Year"])
    if debug: print(f"report: {report}")
    
    df = pd.read_excel(filename, skiprows=1)
    if debug: print(f"dataframe shape: {df.shape}")
    if debug: print(f"report: {options}")
    
    if report=="Students__Multi":
        df.rename(columns={"Row":options['Row']}, inplace=True)
        
        if melt:
            df = df.melt(id_vars=options['Row'], var_name=options["Column"])
    elif report=="Students__Geographical":
        df.loc[df.County.isna(),"County"] = "Unknown"
        df.fillna(0, inplace=True)
        for c in df.columns: 
            if df[c].dtype=='float': df[c] = df[c].astype(int)
        df.set_index('County', inplace=True)
        df.rename(columns={c:format_ayear(c) for c in df.columns}, inplace=True)
        
    if verbose:
        display(Markdown("**Options**:"))
        for k,v in options.items():
            display(Markdown(f" * **{k}**: {v}"))
        display(df.head(verbose))
    return df, options


def add_column_tiers(df, tiers):
    "Given df with County index add Tier column"

    df['Tier'] = 'Tier 3'
    df.loc[df.index.isin(tiers['Tier 1']), "Tier"] = "Tier 1"
    df.loc[df.index.isin(tiers['Tier 2']), "Tier"] = "Tier 2"

    return df


def get_df_tier_ne_datasets(tiers):
    file = 'hea_ie/Students__Geographical_-_23_and_under__Undergraduate__All__All__Yes__All__Full-time.xlsx'
    df_a, meta_a = get_dataset(file, verbose=0, melt=0)
    df_a = df_a.drop('Grand Total')
    file = 'hea_ie/Students__Geographical_-_23_and_under__Undergraduate__All__SETU__Yes__All__Full-time.xlsx'
    df_s, meta_c = get_dataset(file, verbose=0, melt=0)
    df_s = df_s.drop('Grand Total')

    df_a = add_column_tiers(df_a, tiers)
    df_s['Tier'] = df_a['Tier']

    df_tier_ne = df_a.groupby("Tier").sum()
    df_tier_ne.loc['Total'] = df_a.sum()
    # df_tier_ne.drop(columns=['Tier'],inplace=True)
    for c in df_tier_ne.columns:
        df_tier_ne[c] = df_tier_ne[c].astype(int)

    df_tier_ne_to_setu = pd.DataFrame(index=df_s.groupby("Tier").sum().index)
    years = [c for c in df_a.columns if "/" in c]
    for y in years:
        df_tier_ne_to_setu[f'{y}'] = df_s.groupby("Tier").sum()[y] / df_a.groupby("Tier").sum()[y]
    df_tier_ne_to_setu.head()

    return df_tier_ne, df_tier_ne_to_setu



def get_df_lc():
    filename = "gov_ie/Projections_of_full-time_enrolment_Primary_and_Second_Level_2021_-_2040.xlsx"
    dfs = pd.read_excel(filename, sheet_name=None,skiprows=28)
    scenarios = [s for s in dfs.keys() if s!="Summary"]
    df_lc = dfs[scenarios[0]][['Year']].copy()
    for s in scenarios:
        df_lc[s] = dfs[s][['LC2 (including repeats)']].round().astype(int)

    df_lc.set_index("Year", inplace=True)

    return df_lc


def get_df_tier_lc(tiers):

    df_tier_lc = pd.DataFrame()

    for year in ['2020', '2021', '2022']:
        a_year = format_ayear(year)
        filename = f"gov_ie/Total_Enrolment_in_Post-Primary_Schools_-_Programme_and_Year_-_{a_year.replace('/','_')}.xlsx"
        df = pd.read_excel(filename, sheet_name="Programme & Year", skiprows=1)
        df_school_enrollment = df.loc[df.County.notna(),['County','LC 2']].set_index('County')
        df_school_enrollment = add_column_tiers(df_school_enrollment, tiers)
        df_school_enrollment = df_school_enrollment.groupby("Tier")['LC 2'].sum()

        df_tier_lc[a_year] = df_school_enrollment

    df_tier_lc.loc['Total'] = df_tier_lc.sum()

    return df_tier_lc


def compute_ROUT(institution='All'):
    file = f'hea_ie/Students__Geographical_-_23_and_under__Undergraduate__All__{institution}__Yes__All__Full-time.xlsx'
    df_ne, _ = get_dataset(file, verbose=0, melt=0)
    file = f'hea_ie/Students__Geographical_-_23_and_under__Undergraduate__All__{institution}__All__All__Full-time.xlsx'
    df_ug, _ = get_dataset(file, verbose=0, melt=0)

    df = pd.DataFrame(index=['Entrants', 'Stock'], data = [
        df_ne.loc['Grand Total'],
        df_ug.loc['Grand Total'],
    ]).T
    df['ROUT'] = (df.Stock - df.Entrants) / df.Stock.shift(1)

    return df.T


if __name__ == "__main__":
    print("Testing format_ayear ...")
    for y in ["22", "2022", "202223", "2022/2023"]:
        print(f"\t{y:9} -> {format_ayear(y)}")

    for y in [2000, 2020]:

        print(f"{y=} {format_ayear(y)=} {previous_ayear(y)=} {next_ayear(y)=}")
    print()