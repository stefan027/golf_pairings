import random
import numpy as np
from copy import deepcopy
import streamlit as st
import pandas as pd
import time


st.title("Gholf vierballe")
st.markdown("")


if 'has_result' not in st.session_state:
    st.session_state.has_result = False
    st.session_state.is_running = False


def clear_result():
    st.session_state.has_result = False

def set_run_state():
    st.session_state.has_result = False
    st.session_state.is_running = True


num_players = st.number_input(
    "Aantal spelers", min_value=8, value=8, step=4, on_change=clear_result
)
num_rounds = st.number_input(
    "Aantal rondtes", min_value=2, value=4, step=1, on_change=clear_result
)
num_groups = num_players // 4


def draw_player(available_players):
    idx = random.randint(0, len(available_players)-1)
    p = available_players.pop(idx)
    return p, available_players


def draw_foursome(available_players):
    foursome = []
    for _ in range(4):
        player, available_players = draw_player(available_players)
        foursome.append(player)
    return sorted(foursome[:2]), sorted(foursome[2:]), available_players


run = st.button(
    "Begin", on_click=set_run_state, use_container_width=True,
    disabled=st.session_state.is_running, type="primary"
)
stop = st.button(
    "Stop", use_container_width=True, disabled=not run,
)

if st.session_state.is_running:
    min_pair_matches = 1e4
    min_group_matches = 1e4
    min_group_max = 1e4
    with st.spinner(
        "Besig om die beste kombinasies te vind. "
        "Kliek stop om die resultaat te sien."
    ):
        info_box = st.empty()
        while True:
            if stop:
                break
            counts_pairs = np.zeros((num_players, num_players))
            counts_groups = np.zeros((num_players, num_players))
            curr_tee_sheet = np.zeros(
                (num_rounds, num_groups, 4), dtype=np.int8
            )
            for r in range(num_rounds):
                players = list(range(num_players))
                for g in range(num_groups):
                    pair1, pair2, players = draw_foursome(players)
                    counts_pairs[pair1[0], pair1[1]] += 1
                    counts_pairs[pair2[0], pair2[1]] += 1
                    group = sorted(pair1 + pair2)
                    for g1 in range(4):
                        for g2 in range(g1+1, 4, 1):
                            counts_groups[group[g1], group[g2]] += 1
                    curr_tee_sheet[r, g, :] = pair1 + pair2
            pair_matches = counts_pairs[counts_pairs > 1].sum()
            group_matches = counts_groups[counts_groups > 1].sum()
            group_max = counts_groups.max()
            new_best = False
            if pair_matches < min_pair_matches:
                new_best = True
            elif (
                pair_matches <= min_pair_matches
                and group_max < min_group_max
            ):
                new_best = True
            elif (
                pair_matches <= min_pair_matches
                and group_max <= min_group_max
                and group_matches < min_group_matches
            ):
                new_best = True
            if new_best:
                with info_box.container():
                    st.caption("Nuwe beste kombinasie gevind!")
                    st.caption(f"Aantal tweebal herhalings: {pair_matches}")
                    st.caption(f"Aantal vierbal herhalings: {group_max}")
                min_pair_matches = pair_matches
                min_group_matches = group_matches
                min_group_max = group_max
                st.session_state.tee_sheet = deepcopy(curr_tee_sheet)
                st.session_state.has_result = True
    st.session_state.is_running = False
    st.rerun()

if not st.session_state.is_running and st.session_state.has_result:
    df = pd.DataFrame(
        st.session_state.tee_sheet.reshape((num_groups*num_rounds, 4)),
        columns=[f"Speler {i+1}" for i in range(4)]
    )
    for r in range(num_rounds):
        st.markdown(f"#### Rondte {r+1}")
        tmp = df.iloc[r*num_groups:r*num_groups+num_groups]
        tmp.index = [f"Vierbal {i+1}" for i in range(num_groups)]
        st.dataframe(tmp, use_container_width=True)
