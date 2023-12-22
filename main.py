#!/usr/bin/env python

import streamlit as st
from streamlit_sortables import sort_items
from messages import messages

import numpy as np 
import pandas as pd
import my_lib 
from my_lib import next_ayear, previous_ayear, format_ayear

DESCRIBE_COLS = ['mean', 'std', 'min', 'max']

st.write("# Student Projection Model")

# Step 1 - split country into tiers

st.write("---")
st.write("### Split country into tiers")

st.write("Note: Can insert here graphs showing reason for default tiers in terms of proportion of NE that enroll in SETU.")

counties = ['Carlow', 'Cavan', 'Clare', 'Cork', 'Donegal', 'Dublin', 'Galway',
       'Kerry', 'Kildare', 'Kilkenny', 'Laois', 'Leitrim', 'Limerick',
       'Longford', 'Louth', 'Mayo', 'Meath', 'Monaghan', 'Offaly',
       'Roscommon', 'Sligo', 'Tipperary', 'Waterford', 'Westmeath',
       'Wexford', 'Wicklow']
tiers = {}
tiers['Tier 1'] = sorted(["Kilkenny", "Wexford", "Carlow", "Waterford"])
tiers['Tier 2'] = sorted(["Wicklow", "Kildare", "Tipperary", "Laois"])
tiers['Tier 3'] = sorted([c for c in counties if c not in tiers['Tier 1'] and c not in tiers['Tier 2']])

original_tiers = [
    {'header': f'Tier {k}',  'items': tiers[f'Tier {k}']} for k in range(1,4)
]

sorted_items = sort_items(original_tiers, multi_containers=True)
user_tiers = {item['header']:item['items'] for item in sorted_items}


st.write("### New Entrant to SETU rate for each tier")


df_tier_ne, df_tier_ne_to_setu = my_lib.get_df_tier_ne_datasets(user_tiers)

with st.expander("Data source and calculation"):
    st.write(messages['DS - computing tier NE_to_SETU rates'])
    st.write(messages['computing tier NE_to_SETU rates'])

    st.write("The New Entrant to SETU rate for each tier for each year, is calculated by grouping the New Entrants to SETU by tier and year."
             " Then divide by the number of New Entrant going to all institutions from that tier in that year.")
    st.dataframe(df_tier_ne_to_setu)
    st.write("A line plot of this data is:")
    st.line_chart(df_tier_ne_to_setu.T, use_container_width=True)

df_tier_ne_to_setu_stats = df_tier_ne_to_setu.T.describe().loc[DESCRIBE_COLS].T
st.dataframe(df_tier_ne_to_setu_stats)


st.write("### Distribution of New Entrants by tier")


df_tmp = df_tier_ne.iloc[:-1] / df_tier_ne.loc['Total']

with st.expander("Data source and calculation"):
    st.write(messages['DS - computing tier NE proportions'])
    st.dataframe(df_tier_ne)
    st.write("A line plot of this data is")
    st.line_chart(df_tier_ne.iloc[:-1].T, use_container_width=True)
    st.write("The proportions are then obtained on dividing by the overall count of New Entrants.")
    st.dataframe(df_tmp)

st.dataframe(df_tmp.T.describe().loc[DESCRIBE_COLS].T)


st.write("### LC Enrolment by tier")


df_tier_lc = my_lib.get_df_tier_lc(user_tiers)


with st.expander("Data source and calculation"):
    st.write(messages['DS - LC Enrolment by tier'])
    #st.write(df_tier_lc)
    #st.line_chart(df_tier_lc, use_container_width=True)
    st.write("The proportion of LC students from each tier is obtained by counting the students in each tier in each year")
    st.write(df_tier_lc)
    st.write("Then dividing by the total number of LC students in that year")

    st.dataframe((df_tier_lc.iloc[:-1]/df_tier_lc.loc['Total']))


df_tier_lc_stats = (df_tier_lc.iloc[:-1]/df_tier_lc.loc['Total']).T.describe().loc[DESCRIBE_COLS].T
st.dataframe(df_tier_lc_stats)


st.write("### LC Enrolment (Projection)")


df_lc = my_lib.get_df_lc()

with st.expander("Data source and calculation"):
    st.write(messages['DS - LC Enrolment (Projection)'])
    st.write(df_lc)
    st.line_chart(df_lc, use_container_width=True)


st.write("### Transfer rate from second to third level")

start_ayear = max(next_ayear(min(df_tier_lc.columns)), min(df_tier_ne.columns))
end_ayear = min(next_ayear(max(df_tier_lc.columns)), max(df_tier_ne.columns))
ayears = [ format_ayear(y) for y in range(int(start_ayear[:4]),int(end_ayear[:4])+1) ]
lc_ayears = [ previous_ayear(ay) for ay in ayears ]
df_tmp = df_tier_lc[lc_ayears].copy()
df_tmp.columns = ayears

df_tier_tr = df_tier_ne[ayears] / df_tmp

with st.expander("Data source and calculation"):
    st.write(messages['DS - Transfer rate from second to third level - 1'])
    df_tr = pd.read_csv("data/Transfer_Rate.csv").set_index("Year")
    st.dataframe(df_tr)
    st.write(messages['DS - Transfer rate from second to third level - 2'])

    st.write(f"Given available datasets we can estimate the tier-specific transfer rate for each academic year from {start_ayear} to {end_ayear} inclusive.")

    st.write(df_tier_tr)

df_tier_tr_stats = df_tier_tr.T.describe().loc[DESCRIBE_COLS].T
st.dataframe(df_tier_tr_stats)


st.write("### Rate of Undergraduate Turnover (ROUT)")


df_rout = my_lib.compute_ROUT("SETU")
with st.expander("Data source and calculation"):
    st.write(messages['DS - Rate of Undergraduate Turnover (ROUT) - 1'])

    st.write("Using the HEA published data the national ROUT is")
    df_tmp = my_lib.compute_ROUT()
    st.dataframe(df_tmp)
    st.write("And for SETU the ROUT estimate is")
    st.dataframe(df_rout)

df_rout_stats = pd.DataFrame(df_rout.loc['ROUT'].T.describe().loc[DESCRIBE_COLS]).T
st.dataframe(df_rout_stats)


st.divider()
st.write("### National, Full-time, Undergraduate Projections")

st.write('#### Model Parameters')

st.write("""\
The projections generated by the model depend greatly on the model parameters. To aid understanding of this relationship 
a number of parameter presets are specified below. The
 * `Pessimistic` assumes lowest LC projections scenario and lowest observed values for transfer to 3rd level, for rate of SETU selection, and for ROUT.
 * `Average` assumes average LC projections scenario and mean of the  observed values for transfer to 3rd level, for rate of SETU selection, and for ROUT.
 * `Optimistic` assumes optimistic LC projections scenario and maximum observed values for transfer to 3rd level, for rate of SETU selection, and for ROUT.
 * `National` assumes average LC projections scenario and assumes 2nd to 3rd level transfer rate and SETU ROUT matches national values, while using mean values for rate of SETU selection.
""")

df_param_orig = pd.DataFrame(
    [
        {'scenario': 'Pessimistic', 'LC': 'M3F2',  
            'T1TR': np.round(df_tier_tr_stats.loc['Tier 1','min'],4), 
            'T2TR': np.round(df_tier_tr_stats.loc['Tier 2','min'],4), 
            'T3TR': np.round(df_tier_tr_stats.loc['Tier 3','min'],4), 
            'T1NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 1','min'],4), 
            'T2NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 2','min'],4),
            'T3NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 3','min'],4),
            'ROUT': np.round(df_rout_stats.loc['ROUT','min'],4), 
         'show': True},
        {'scenario': 'Average', 'LC': 'M2F1',  
            'T1TR': np.round(df_tier_tr_stats.loc['Tier 1','mean'],4), 
            'T2TR': np.round(df_tier_tr_stats.loc['Tier 2','mean'],4), 
            'T3TR': np.round(df_tier_tr_stats.loc['Tier 3','mean'],4), 
            'T1NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 1','mean'],4), 
            'T2NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 2','mean'],4),
            'T3NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 3','mean'],4),
            'ROUT': np.round(df_rout_stats.loc['ROUT','mean'],4), 
         'show': True},
        {'scenario': 'Optimistic', 'LC': 'M1F1',  
            'T1TR': np.round(df_tier_tr_stats.loc['Tier 1','max'],4), 
            'T2TR': np.round(df_tier_tr_stats.loc['Tier 2','max'],4), 
            'T3TR': np.round(df_tier_tr_stats.loc['Tier 3','max'],4), 
            'T1NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 1','max'],4), 
            'T2NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 2','max'],4),
            'T3NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 3','max'],4),
            'ROUT': np.round(df_rout_stats.loc['ROUT','max'],4), 
         'show': True},
        {'scenario': 'National', 'LC': 'M2F1',  
            'T1TR': 0.66, 
            'T2TR': 0.66, 
            'T3TR': 0.66, 
            'T1NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 1','max'],4), 
            'T2NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 2','max'],4),
            'T3NESETU': np.round(df_tier_ne_to_setu_stats.loc['Tier 3','max'],4),
            'ROUT': 0.745, 
         'show': True},
    ] + [
        {'scenario': f'Model {k}', 'LC': 'M2F1',  
            'T1TR': 0, 'T2TR': 0, 'T3TR': 0, 
            'T1NESETU': 0, 
            'T2NESETU': 0, 
            'T3NESETU': 0,
            'ROUT': 0, 'show': False}
        for k in range(5)
    ]
)
df_param = st.data_editor(
    df_param_orig,
    column_config={
        "scenario": st.column_config.TextColumn(
            "Model Scenario",
            help="Name used to identify model parameter set."
        ),

        "LC": st.column_config.SelectboxColumn(
            "LC",
            help="Leaving Cert projection scenario, as listed in the DoE LC projection 2021-2040 report.",
            width="small",
            options=df_lc.columns,
            required=True
        ),

        'T1TR': st.column_config.NumberColumn(
            'T1 TR',
            help='Tier 1 Transfer rate from 2nd level to 3rd level.',
            min_value = 0,
            max_value = 1,
            required=True
        ),

        'T2TR': st.column_config.NumberColumn(
            'T2 TR',
            help='Tier 2 Transfer rate from 2nd level to 3rd level.',
            min_value = 0,
            max_value = 1,
            required=True
        ),

        'T3TR': st.column_config.NumberColumn(
            'T3 TR',
            help='Tier 3 Transfer rate from 2nd level to 3rd level.',
            min_value = 0,
            max_value = 1,
            required=True
        ),

        'T1NESETU': st.column_config.NumberColumn(
            'T1 NE SETU',
            help='Proportion of New Entrants from Tier 1 that enrolled at SETU.',
            min_value = 0,
            max_value = 1,
            required=True
        ),

        'T2NESETU': st.column_config.NumberColumn(
            'T2 NE SETU',
            help='Proportion of New Entrants from Tier 2 that enrolled at SETU.',
            min_value = 0,
            max_value = 1,
            required=True
        ),

        'T3NESETU': st.column_config.NumberColumn(
            'T3 NE SETU',
            help='Proportion of New Entrants from Tier 3 that enrolled at SETU.',
            min_value = 0,
            max_value = 1,
            required=True
        ),

        'ROUT': st.column_config.NumberColumn(
            'ROUT',
            help='Rate of Undergraduate Turnover (ROUT)',
            min_value = 0,
            max_value = 1,
            required=True
        ),
        "show": st.column_config.CheckboxColumn(
            "Show ?",
            help="Include this scenario in generated tables and plots?"
        ),
    },
    #disabled=["command"],
    hide_index=True,
)


if st.button("Build Projections", type="primary"):
    tabs = st.tabs(list(df_param.scenario.values))

    df_projections = pd.DataFrame(index=df_lc.index)

    for k, tab in enumerate(tabs):
    
        row = df_param.iloc[k]

        with tab:
            if not row.show: 
                st.write("Select 'Show' to generate projections")
                continue

            df = df_lc[[row.LC]].copy()
            df.columns = ['LC']

            for tier in [1,2,3]:
                df[f'T{tier}_LC'] = np.round(df.LC * df_tier_lc_stats['mean'][f"Tier {tier}"])
            for tier in [1,2,3]:
                df[f'T{tier}_NE'] = np.round((df[f'T{tier}_LC'] * row[f"T{tier}TR"]).shift(1))
            for tier in [1,2,3]:
                df[f'T{tier}_NE_SETU'] = np.round(df[f'T{tier}_NE'] * row[f"T{tier}NESETU"])

            df['NE'] = df['T1_NE_SETU'] + df['T2_NE_SETU'] + df['T3_NE_SETU']
            df['UG'] = 0

            ug_projections = [df_rout.loc['Stock']['2020/21']]
            for ne in df['NE'].values[1:]:
                ug_projections.append(ne + row.ROUT*ug_projections[-1])
            df['UG'] = np.round(np.array(ug_projections))
            
            df_projections[row.scenario] = df['UG'] 
            with tab:
                st.dataframe(df)

    st.write("The full-time undergraduate national projection are:")
    st.dataframe(df_projections)

    st.line_chart(df_projections, use_container_width=True)

    st.write("""\

**Notes:**
 * These projections use constant values for the model parameters. A more prudent approach would allow a parameter to 
    change over time, say SETU's ROUT might increase to the national average with more focus on retention. 
    This is not a significant change to implement/model and the generated projections would line within 
    the envelope given here.
 * Only full-time, national, undergraduate enrollments accounted for here.
             
""")
else:
    pass
