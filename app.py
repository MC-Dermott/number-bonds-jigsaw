import random
import time

import streamlit as st

st.set_page_config(page_title="Number Bonds Jigsaw", page_icon="🧩", layout="centered")


def valid_pairs(target: int) -> set[tuple[int, int]]:
    return {(a, b) for a in range(10) for b in range(a, 10) if a + b == target}


def new_game(target: int, timer_enabled: bool, timer_mode: str, countdown_seconds: int) -> None:
    st.session_state.target = target
    st.session_state.order = random.sample(range(10), 10)
    st.session_state.found = []
    st.session_state.selected = None
    st.session_state.message = None
    st.session_state.message_kind = None
    st.session_state.game_over = False
    st.session_state.completed = False
    st.session_state.timer_enabled = timer_enabled
    st.session_state.timer_mode = timer_mode
    st.session_state.countdown_seconds = countdown_seconds
    st.session_state.start_time = time.time()
    st.session_state.elapsed_at_finish = None


def init_state() -> None:
    if "order" not in st.session_state:
        new_game(target=10, timer_enabled=False, timer_mode="Count up (stopwatch)", countdown_seconds=60)


st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        height: 88px;
        font-size: 2rem;
        font-weight: 800;
        border-radius: 16px;
        position: relative;
        border: 3px solid rgba(0,0,0,0.15);
        margin: 6px 10px;
    }
    div.stButton > button::before,
    div.stButton > button::after {
        content: "";
        position: absolute;
        width: 22px;
        height: 22px;
        background-color: inherit;
        border: 3px solid rgba(0,0,0,0.15);
        border-radius: 50%;
        top: 50%;
        transform: translateY(-50%);
    }
    div.stButton > button::before { left: -14px; }
    div.stButton > button::after { right: -14px; }

    @keyframes dropIn {
        from { opacity: 0; transform: translateY(-40px) scale(0.9); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .joined-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 10px 0;
        animation: dropIn 0.45s ease-out;
    }
    .joined-pair {
        position: relative;
        display: inline-flex;
    }
    .joined-piece {
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        font-weight: 800;
        color: white;
        background: #51cf66;
        border: 3px solid rgba(0,0,0,0.15);
    }
    .joined-piece.left { border-radius: 14px 0 0 14px; }
    .joined-piece.right { border-radius: 0 14px 14px 0; border-left: none; }
    .joined-pair::after {
        content: "";
        position: absolute;
        left: 50%;
        top: 50%;
        width: 16px;
        height: 16px;
        background: #51cf66;
        border: 3px solid rgba(0,0,0,0.15);
        border-radius: 50%;
        transform: translate(-50%, -50%);
    }
    .joined-eq {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2f9e44;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()

with st.sidebar:
    st.header("⚙️ Settings")
    randomise = st.checkbox("🎲 Randomise number each game", value=st.session_state.get("randomise", False))
    if randomise:
        st.caption("A random target (1-10) will be picked when you start a new game.")
        target_choice = None
    else:
        target_choice = st.selectbox(
            "Number bonds to:",
            options=list(range(1, 11)),
            index=list(range(1, 11)).index(st.session_state.target),
        )
    timer_choice = st.checkbox("Enable timer", value=st.session_state.timer_enabled)
    mode_choice = st.session_state.timer_mode
    countdown_choice = st.session_state.countdown_seconds
    if timer_choice:
        mode_choice = st.radio(
            "Timer type",
            options=["Count up (stopwatch)", "Countdown"],
            index=["Count up (stopwatch)", "Countdown"].index(st.session_state.timer_mode),
        )
        if mode_choice == "Countdown":
            countdown_choice = st.slider("Time limit (seconds)", 15, 180, st.session_state.countdown_seconds, step=15)

    if st.button("🔄 New Game", type="primary", use_container_width=True):
        st.session_state.randomise = randomise
        chosen_target = random.randint(1, 10) if randomise else target_choice
        new_game(chosen_target, timer_choice, mode_choice, countdown_choice)
        st.rerun()

target = st.session_state.target
pairs = valid_pairs(target)
total_pairs = len(pairs)

st.markdown(
    f"<h1 style='text-align:center;font-size:6rem;margin-bottom:0;'>{target}</h1>"
    f"<p style='text-align:center;color:gray;margin-top:0;'>Click two jigsaw pieces that add up to {target}! "
    f"Click the same piece twice for a double, like 5 + 5.</p>",
    unsafe_allow_html=True,
)


def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:01d}:{seconds % 60:02d}"


def try_pair(a: int, b: int) -> None:
    if (a, b) in pairs and (a, b) not in st.session_state.found:
        st.session_state.found.append((a, b))
        st.session_state.message = f"🎉 {a} + {b} = {target}!"
        st.session_state.message_kind = "success"
    else:
        st.session_state.message = f"❌ {a} + {b} = {a + b}, not {target}. Try again!"
        st.session_state.message_kind = "error"
    st.session_state.selected = None

    if len(st.session_state.found) == total_pairs and total_pairs > 0:
        st.session_state.completed = True
        st.session_state.game_over = True
        st.session_state.elapsed_at_finish = time.time() - st.session_state.start_time


def handle_click(digit: int) -> None:
    if st.session_state.selected is None:
        st.session_state.selected = digit
        st.session_state.message = None
        return

    if st.session_state.selected == digit:
        # Clicked the same piece again: try it as a double, e.g. 5 + 5.
        try_pair(digit, digit)
        return

    a, b = sorted((st.session_state.selected, digit))
    try_pair(a, b)


def render_body() -> None:
    if st.session_state.timer_enabled and not st.session_state.game_over:
        elapsed = time.time() - st.session_state.start_time
        if st.session_state.timer_mode == "Countdown":
            remaining = st.session_state.countdown_seconds - elapsed
            if remaining <= 0:
                st.session_state.game_over = True
                st.session_state.elapsed_at_finish = st.session_state.countdown_seconds
                remaining = 0
            st.markdown(
                f"<h3 style='text-align:center;'>⏱️ {format_time(remaining)}</h3>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<h3 style='text-align:center;'>⏱️ {format_time(elapsed)}</h3>",
                unsafe_allow_html=True,
            )

    st.progress(len(st.session_state.found) / total_pairs if total_pairs else 1.0)
    st.caption(f"Found {len(st.session_state.found)} of {total_pairs} pairs")

    if st.session_state.message:
        if st.session_state.message_kind == "success":
            st.success(st.session_state.message)
        else:
            st.error(st.session_state.message)

    if st.session_state.selected is not None and not st.session_state.game_over:
        if st.button(f"✋ Cancel selection ({st.session_state.selected})"):
            st.session_state.selected = None
            st.rerun()

    if st.session_state.completed:
        st.balloons()
        st.success(f"🏆 All pairs found in {format_time(st.session_state.elapsed_at_finish)}!")
    elif st.session_state.game_over:
        missed = pairs - set(st.session_state.found)
        st.error("⏰ Time's up! Missed pairs: " + ", ".join(f"{a}+{b}" for a, b in sorted(missed)))

    found_digits = {digit for pair in st.session_state.found for digit in pair}
    remaining = [digit for digit in st.session_state.order if digit not in found_digits]

    cols_per_row = 5
    for row_start in range(0, len(remaining), cols_per_row):
        row_digits = remaining[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, digit in zip(cols, row_digits):
            with col:
                is_selected = st.session_state.selected == digit
                if col.button(
                    str(digit),
                    key=f"piece_{digit}",
                    disabled=st.session_state.game_over,
                    type="primary" if is_selected else "secondary",
                    use_container_width=True,
                ):
                    handle_click(digit)
                    st.rerun()

    if st.session_state.found:
        st.markdown("#### 🧩 Completed pairs")
        rows_html = "".join(
            f"<div class='joined-row'>"
            f"<div class='joined-pair'>"
            f"<div class='joined-piece left'>{a}</div>"
            f"<div class='joined-piece right'>{b}</div>"
            f"</div>"
            f"<span class='joined-eq'>= {target}</span>"
            f"</div>"
            for a, b in st.session_state.found
        )
        st.markdown(rows_html, unsafe_allow_html=True)


refresh_interval = 1 if st.session_state.timer_enabled and not st.session_state.game_over else None
st.fragment(render_body, run_every=refresh_interval)()
