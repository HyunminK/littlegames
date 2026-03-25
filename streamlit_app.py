#!/usr/bin/env python3
import altair as alt
import pandas as pd
import streamlit as st

import coinflip
import guess_game


st.set_page_config(page_title="Little Games", page_icon="🎮")


def reset_guess_game():
    """Start a fresh guessing game in session state."""
    game = guess_game.new_game()
    st.session_state.guess_game_state = {
        "target": game["target"],
        "attempts": game["attempts"],
        "message": "Guess the number between 1 and 100!",
        "won": False,
        "history": [],
    }
    st.session_state.show_secret_number = False
    st.session_state.guess_input_text = ""
    st.session_state.guess_input_error = None


def reset_coin_game():
    """Reset the coin flip state for a fresh game."""
    st.session_state.last_flip = None
    st.session_state.heads_count = 0
    st.session_state.tails_count = 0
    st.session_state.coin_flip_count = 0
    st.session_state.coin_history = []


def apply_coin_flips(num_flips):
    """Run one or more coin flips and update session state."""
    for _ in range(num_flips):
        result = coinflip.flip_coin()
        st.session_state.last_flip = result
        st.session_state.coin_flip_count += 1
        st.session_state.coin_history.append(result)
        if result == "Heads":
            st.session_state.heads_count += 1
        else:
            st.session_state.tails_count += 1


def init_state():
    """Initialize session state once per browser session."""
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "guess_game_state" not in st.session_state:
        reset_guess_game()
    if "last_flip" not in st.session_state:
        reset_coin_game()


def render_coin_history(history):
    """Render a simple history of flips using H/T circles."""
    if not history:
        st.info("Flip the coin to start building the history.")
        return

    history_markup = "".join(
        (
            '<div class="history-chip heads">H</div>'
            if result == "Heads"
            else '<div class="history-chip tails">T</div>'
        )
        for result in history
    )

    st.markdown(
        f"""
        <style>
        .history-wrap {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin: 1rem 0 1.5rem;
        }}

        .history-chip {{
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
            font-weight: 700;
            border: 1px solid #b8c3cd;
        }}

        .history-chip.heads {{
            background: #7a8fa3;
            color: #f8fbff;
            border-color: #7a8fa3;
        }}

        .history-chip.tails {{
            background: #c3ced8;
            color: #213545;
            border-color: #c3ced8;
        }}
        </style>
        <div class="history-wrap">{history_markup}</div>
        """,
        unsafe_allow_html=True,
    )


def render_coin_chart(heads_count, tails_count):
    """Render a stacked bar chart with counts and percentages."""
    total_flips = heads_count + tails_count
    if total_flips == 0:
        st.info("Flip the coin to start building the heads/tails chart.")
        return

    heads_percent = heads_count / total_flips
    tails_percent = tails_count / total_flips
    chart_data = pd.DataFrame(
        [
            {
                "Outcome": "Heads",
                "Count": heads_count,
                "Percent": heads_percent,
            },
            {
                "Outcome": "Tails",
                "Count": tails_count,
                "Percent": tails_percent,
            },
        ]
    )

    color_scale = alt.Scale(domain=["Heads", "Tails"], range=["#7a8fa3", "#c3ced8"])

    st.markdown(
        f"""
        <style>
        .coin-chart-labels {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0.25rem 0 0.5rem;
            gap: 1rem;
            font-size: 0.95rem;
            font-weight: 700;
        }}

        .coin-chart-label {{
            display: flex;
            flex-direction: column;
            line-height: 1.3;
        }}

        .coin-chart-label.left {{
            color: #425769;
            text-align: left;
        }}

        .coin-chart-label.right {{
            color: #51606f;
            text-align: right;
        }}

        .coin-chart-label span {{
            font-size: 0.82rem;
            font-weight: 600;
            opacity: 0.9;
        }}
        </style>
        <div class="coin-chart-labels">
            <div class="coin-chart-label left">
                Heads: {heads_count}
                <span>{heads_percent:.1%} of flips</span>
            </div>
            <div class="coin-chart-label right">
                Tails: {tails_count}
                <span>{tails_percent:.1%} of flips</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bar = (
        alt.Chart(chart_data)
        .mark_bar(size=56)
        .encode(
            x=alt.X("sum(Percent):Q", axis=alt.Axis(format="%"), title="Share of total flips"),
            color=alt.Color("Outcome:N", scale=color_scale, legend=alt.Legend(orient="bottom")),
            order=alt.Order("Outcome:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("Outcome:N"),
                alt.Tooltip("Count:Q"),
                alt.Tooltip("Percent:Q", format=".1%"),
            ],
        )
        .properties(height=110)
    )
    st.altair_chart(bar.configure_view(strokeOpacity=0), use_container_width=True)


def show_home():
    st.title("Little Games")
    st.write("Pick a game to play.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Guess the Number", use_container_width=True):
            st.session_state.page = "Guess the Number"
            st.rerun()
    with col2:
        if st.button("Coin Flip", use_container_width=True):
            st.session_state.page = "Coin Flip"
            st.rerun()


def show_guess_game():
    guess_state = st.session_state.guess_game_state

    def submit_guess(guess_value):
        """Apply a guess and update guess-game session state."""
        message, attempts, won = guess_game.evaluate_guess(
            guess_state["target"],
            guess_state["attempts"],
            int(guess_value),
        )
        guess_state["attempts"] = attempts
        guess_state["message"] = message
        guess_state["won"] = won
        guess_state["history"].append(int(guess_value))

    def parse_typed_guess(raw_value):
        """Validate typed input for the guessing game."""
        try:
            guess_value = int(raw_value)
        except ValueError:
            return None, "Please enter an integer between 1 and 100."

        if not 1 <= guess_value <= 100:
            return None, "Please enter a number between 1 and 100."

        return guess_value, None

    def handle_typed_guess_submit():
        """Submit the current typed guess when Enter is pressed."""
        if guess_state["won"]:
            return

        parsed_guess, error_message = parse_typed_guess(
            st.session_state.guess_input_text.strip()
        )
        if error_message is not None:
            st.session_state.guess_input_error = error_message
            return

        st.session_state.guess_input_error = None
        submit_guess(parsed_guess)
        st.session_state.guess_input_text = ""

    def render_guess_history(history):
        """Render a number line with all past guesses."""
        if not history:
            st.info("Make a guess to start the number line.")
            return

        chart_data = pd.DataFrame(
            [
                {
                    "Guess": guess_value,
                    "Line": 1,
                    "Label": str(guess_value),
                    "IsLatest": index == len(history) - 1,
                    "Size": 520 if index == len(history) - 1 else 300,
                }
                for index, guess_value in enumerate(history)
            ]
        )

        rule = alt.Chart(pd.DataFrame([{"x1": 1, "x2": 100, "y": 1}])).mark_rule(
            color="#8ca1b4",
            strokeWidth=4,
        ).encode(
            x=alt.X("x1:Q", scale=alt.Scale(domain=[1, 100])),
            x2="x2:Q",
            y=alt.Y("y:Q", axis=None),
        )

        points = alt.Chart(chart_data).mark_circle().encode(
            x=alt.X(
                "Guess:Q",
                scale=alt.Scale(domain=[1, 100]),
                axis=alt.Axis(values=[25, 50, 75, 100], tickSize=0, labelPadding=10),
                title="",
            ),
            y=alt.Y("Line:Q", axis=None),
            size=alt.Size("Size:Q", legend=None),
            color=alt.condition(
                alt.datum.IsLatest,
                alt.value("#5c809d"),
                alt.value("#d9e4ed"),
            ),
            tooltip=[
                alt.Tooltip("Guess:Q"),
                alt.Tooltip("IsLatest:N", title="Most Recent"),
            ],
        )

        labels = alt.Chart(chart_data).mark_text(
            fontWeight="bold",
            baseline="middle",
        ).encode(
            x=alt.X("Guess:Q", scale=alt.Scale(domain=[1, 100])),
            y=alt.Y("Line:Q", axis=None),
            text="Label:N",
            color=alt.condition(
                alt.datum.IsLatest,
                alt.value("#f7fbff"),
                alt.value("#2a3f52"),
            ),
        )

        st.altair_chart(
            (rule + points + labels).properties(height=110).configure_view(strokeOpacity=0),
            use_container_width=True,
        )

    st.title("Guess the Number")
    history_container = st.container()
    st.markdown(
        """
        <style>
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextInput"] input:focus-visible {
            border: 1px solid #b9c8d5 !important;
            outline: none !important;
            box-shadow: none !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"] {
            border: 1px solid #b9c8d5 !important;
            box-shadow: none !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"]:focus-within {
            border: 1px solid #7a8fa3 !important;
            box-shadow: 0 0 0 1px #7a8fa3 !important;
        }
        .guess-feedback {
            margin: 0.75rem 0 0.35rem;
            padding: 0.8rem 1rem;
            border-radius: 0.75rem;
            font-weight: 700;
        }
        .guess-feedback.success {
            background: #e6f6ea;
            color: #1f7a39;
            border: 1px solid #b9e3c4;
        }
        .guess-feedback.warning {
            background: #fdeaea;
            color: #b42318;
            border: 1px solid #f3c7c4;
        }
        .guess-feedback.neutral {
            background: #eef3f7;
            color: #314656;
            border: 1px solid #d6e0e8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    secret_col, toggle_col = st.columns([1, 1])
    with toggle_col:
        st.session_state.show_secret_number = st.toggle(
            "Reveal secret number",
            value=st.session_state.show_secret_number,
            key="show_secret_number_toggle",
        )
    with secret_col:
        secret_label = (
            str(guess_state["target"])
            if st.session_state.show_secret_number
            else "•••"
        )
        st.caption(f"Secret number: {secret_label}")

    if guess_state["won"]:
        feedback_class = "success"
    elif guess_state["attempts"] > 0:
        feedback_class = "warning"
    else:
        feedback_class = "neutral"
    st.markdown(
        f'<div class="guess-feedback {feedback_class}">{guess_state["message"]}</div>',
        unsafe_allow_html=True,
    )

    input_mode = st.radio(
        "Choose how to enter your guess",
        ("Typed input", "Slider"),
        horizontal=True,
    )

    if input_mode == "Typed input":
        st.text_input(
            "Your guess",
            key="guess_input_text",
            placeholder="Enter 1 to 100",
            on_change=handle_typed_guess_submit,
        )
        if st.session_state.guess_input_error is not None:
            st.error(st.session_state.guess_input_error)
    else:
        with st.form("guess-form"):
            guess_value = st.slider(
                "Slide to your guess",
                min_value=1,
                max_value=100,
                value=50,
            )
            submitted = st.form_submit_button("Submit Guess")

        if submitted and not guess_state["won"]:
            st.session_state.guess_input_error = None
            submit_guess(guess_value)

    with history_container:
        render_guess_history(guess_state["history"])
    st.write(f"Attempts: {guess_state['attempts']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Restart Game", use_container_width=True):
            reset_guess_game()
            st.rerun()
    with col2:
        if st.button("Back Home", use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()


def show_coin_flip():
    st.title("Coin Flip")
    st.write("Flip coins one at a time or run a batch simulation, then compare the heads/tails split over time.")

    controls_left, controls_right = st.columns([1.4, 1])
    with controls_left:
        flip_count = st.number_input(
            "Number of flips to simulate",
            min_value=1,
            step=1,
            value=10,
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Flip Coin", use_container_width=True):
                apply_coin_flips(1)
                st.rerun()
        with col2:
            if st.button("Flip N Times", use_container_width=True):
                apply_coin_flips(int(flip_count))
                st.rerun()

    with controls_right:
        st.metric("Total Flips", st.session_state.coin_flip_count)
        if st.session_state.last_flip is not None:
            st.caption(f"Last result: {st.session_state.last_flip}")

    render_coin_chart(st.session_state.heads_count, st.session_state.tails_count)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset Counter", use_container_width=True):
            reset_coin_game()
            st.rerun()
    with col2:
        if st.button("Back Home", use_container_width=True):
            reset_coin_game()
            st.session_state.page = "Home"
            st.rerun()

    st.subheader("Flip History")
    render_coin_history(st.session_state.coin_history)


init_state()

if st.session_state.page == "Guess Game":
    show_guess_game()
elif st.session_state.page == "Guess the Number":
    show_guess_game()
elif st.session_state.page == "Coin Flip":
    show_coin_flip()
else:
    show_home()
