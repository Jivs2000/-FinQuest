#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import random
import datetime

# --- Configuration and Data Initialization ---

# Initialize session state variables if they don't exist
# This is crucial for Streamlit apps to maintain state across reruns
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'users' not in st.session_state:
    # In a real app, this would be a database. For this demo, it's a dictionary.
    # Structure: {username: {"password": "pwd", "points": 0, "goals": [], "savings_history": [], "badges": []}}
    st.session_state.users = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

# Define quiz questions and answers
QUIZ_QUESTIONS = [
    {
        "question": "What is the primary purpose of a budget?",
        "options": [
            "To track daily expenses",
            "To make more money",
            "To plan how to spend and save money",
            "To invest in stocks"
        ],
        "answer": "To plan how to spend and save money"
    },
    {
        "question": "What does 'APY' stand for in banking?",
        "options": [
            "Annual Percentage Yield",
            "Annual Payment Year",
            "Average Personal Yield",
            "Automated Payment System"
        ],
        "answer": "Annual Percentage Yield"
    },
    {
        "question": "Which of these is generally considered a 'good' debt?",
        "options": [
            "Credit card debt",
            "Payday loan",
            "Mortgage for a primary residence",
            "Car loan for a luxury vehicle"
        ],
        "answer": "Mortgage for a primary residence"
    },
    {
        "question": "What is diversification in investing?",
        "options": [
            "Putting all your money in one stock",
            "Spreading your investments across different assets",
            "Investing only in bonds",
            "Only investing in your home country"
        ],
        "answer": "Spreading your investments across different assets"
    },
    {
        "question": "What is an emergency fund typically used for?",
        "options": [
            "Vacations",
            "Unexpected expenses like job loss or medical bills",
            "Buying a new car",
            "Daily groceries"
        ],
        "answer": "Unexpected expenses like job loss or medical bills"
    }
]

# Define badges and their criteria (points or actions)
BADGE_CRITERIA = {
    "Newbie": {"type": "on_action", "action": "register"},
    "First Saver": {"type": "on_action", "action": "first_save"},
    "Goal Setter": {"type": "on_action", "action": "first_goal"},
    "Quiz Whiz": {"type": "quiz_correct_count", "count": 3}, # Get 3 correct quiz answers
    "Budget Boss": {"type": "total_points", "threshold": 500},
    "Goal Achiever": {"type": "on_action", "action": "complete_goal"}
}

# --- Helper Functions ---

def award_points(user, amount):
    """Awards points to a user."""
    st.session_state.users[user]["points"] += amount
    st.success(f"🎉 You earned {amount} points!")
    check_for_badges(user) # Check for new badges after earning points

def award_badge(user, badge_name):
    """Awards a badge to a user if they don't already have it."""
    if badge_name not in st.session_state.users[user]["badges"]:
        st.session_state.users[user]["badges"].append(badge_name)
        st.balloons()
        st.success(f"🏆 Congratulations! You earned the '{badge_name}' badge!")

def check_for_badges(user):
    """Checks if the user qualifies for any new badges."""
    user_data = st.session_state.users[user]
    current_points = user_data["points"]
    correct_quiz_answers = user_data.get("correct_quiz_answers", 0)

    for badge, criteria in BADGE_CRITERIA.items():
        if badge not in user_data["badges"]:
            if criteria["type"] == "total_points" and current_points >= criteria["threshold"]:
                award_badge(user, badge)
            elif criteria["type"] == "quiz_correct_count" and correct_quiz_answers >= criteria["count"]:
                award_badge(user, badge)

def calculate_total_saved(user):
    """Calculates the total amount saved by the user."""
    return sum(s["amount"] for s in st.session_state.users[user]["savings_history"])

# --- Authentication Functions ---

def login_user(username, password):
    """Attempts to log in a user."""
    if username in st.session_state.users and st.session_state.users[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.current_page = "dashboard"
        st.success(f"Welcome back, {username}!")
    else:
        st.error("Invalid username or password.")

def register_user(username, password):
    """Registers a new user."""
    if username in st.session_state.users:
        st.error("Username already exists. Please choose a different one.")
    else:
        st.session_state.users[username] = {
            "password": password,
            "points": 0,
            "goals": [],
            "savings_history": [],
            "badges": [],
            "correct_quiz_answers": 0 # Track correct answers for quiz badge
        }
        award_points(username, 100) # Award points for registration
        award_badge(username, "Newbie") # Award Newbie badge
        st.success(f"Account created for {username}! You earned 100 points and the 'Newbie' badge.")
        # Automatically log in the new user
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.current_page = "dashboard"

def logout():
    """Logs out the current user."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.current_page = "login"
    st.info("You have been logged out.")

# --- UI Pages ---

def login_page():
    """Displays the login and registration forms."""
    st.title("💰 FinQuest") # Changed app name here
    st.subheader("Your Gamified Financial Journey")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.header("Login")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_button = st.form_submit_button("Login")
            if login_button:
                login_user(username, password)

    with col2:
        st.header("Register")
        with st.form("register_form"):
            new_username = st.text_input("New Username", key="register_username")
            new_password = st.text_input("New Password", type="password", key="register_password")
            register_button = st.form_submit_button("Register")
            if register_button:
                register_user(new_username, new_password)

def dashboard_page():
    """Displays the user's financial overview and progress."""
    user = st.session_state.username
    user_data = st.session_state.users[user]

    st.title(f"Welcome, {user}! 👋")
    st.subheader("Your Financial Snapshot")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Points", value=user_data["points"])
    with col2:
        st.metric(label="Total Saved", value=f"${calculate_total_saved(user):,.2f}")
    with col3:
        st.metric(label="Badges Earned", value=len(user_data["badges"]))

    st.markdown("---")

    st.header("Your Active Goals")
    if not user_data["goals"]:
        st.info("You haven't set any goals yet! Go to the 'Set Goals' page to get started.")
    else:
        for i, goal in enumerate(user_data["goals"]):
            progress = goal["saved"] / goal["target"] if goal["target"] > 0 else 0
            st.write(f"**{goal['name']}**")
            st.progress(progress, text=f"${goal['saved']:,.2f} / ${goal['target']:,.2f}")
            if progress >= 1.0 and not goal.get("completed", False):
                st.success(f"Goal '{goal['name']}' completed! 🎉")
                award_points(user, 200) # Award points for completing a goal
                award_badge(user, "Goal Achiever")
                st.session_state.users[user]["goals"][i]["completed"] = True # Mark as completed
            st.markdown("---")

    st.header("Recent Savings Activity")
    if not user_data["savings_history"]:
        st.info("No savings logged yet. Start saving!")
    else:
        # Display last 5 savings entries
        for entry in reversed(user_data["savings_history"][-5:]):
            st.write(f"💰 Saved ${entry['amount']:,.2f} on {entry['date']}")

def set_goals_page():
    """Allows users to set and manage financial goals."""
    user = st.session_state.username
    user_data = st.session_state.users[user]

    st.title("🎯 Set Your Financial Goals")
    st.markdown("Set clear financial goals to stay motivated!")

    with st.form("new_goal_form"):
        goal_name = st.text_input("Goal Name (e.g., 'New Car Down Payment', 'Emergency Fund')")
        goal_target = st.number_input("Target Amount ($)", min_value=10.0, step=10.0, format="%.2f")
        add_goal_button = st.form_submit_button("Add Goal")

        if add_goal_button:
            if goal_name and goal_target > 0:
                user_data["goals"].append({"name": goal_name, "target": goal_target, "saved": 0.0, "completed": False})
                award_points(user, 20) # Award points for setting a goal
                award_badge(user, "Goal Setter")
                st.success(f"Goal '{goal_name}' added successfully! You earned 20 points.")
            else:
                st.error("Please enter a valid goal name and a positive target amount.")

    st.markdown("---")
    st.header("Your Current Goals")

    if not user_data["goals"]:
        st.info("You haven't set any goals yet.")
    else:
        for i, goal in enumerate(user_data["goals"]):
            progress = goal["saved"] / goal["target"] if goal["target"] > 0 else 0
            st.write(f"### {goal['name']}")
            st.write(f"**Target:** ${goal['target']:,.2f} | **Saved:** ${goal['saved']:,.2f}")
            st.progress(progress, text=f"{progress:.1%}")

            if st.button(f"Delete '{goal['name']}'", key=f"delete_goal_{i}"):
                user_data["goals"].pop(i)
                st.success(f"Goal '{goal['name']}' deleted.")
                st.rerun() # Rerun to update the display

            st.markdown("---")

def log_savings_page():
    """Allows users to log their savings."""
    user = st.session_state.username
    user_data = st.session_state.users[user]

    st.title("💸 Log Your Savings")
    st.markdown("Every penny counts! Record your savings here.")

    with st.form("log_savings_form"):
        amount = st.number_input("Amount Saved ($)", min_value=0.01, step=1.0, format="%.2f")
        # Optional: Select which goal this saving contributes to
        goal_options = ["None"] + [g["name"] for g in user_data["goals"] if not g.get("completed", False)]
        selected_goal = st.selectbox("Contribute to which goal?", goal_options)
        log_button = st.form_submit_button("Log Savings")

        if log_button:
            if amount > 0:
                user_data["savings_history"].append({
                    "amount": amount,
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                })
                award_points(user, 50) # Award points for logging savings

                if "First Saver" not in user_data["badges"]:
                    award_badge(user, "First Saver")

                # Update selected goal's saved amount
                if selected_goal != "None":
                    for goal in user_data["goals"]:
                        if goal["name"] == selected_goal:
                            goal["saved"] += amount
                            st.success(f"Added ${amount:,.2f} to '{selected_goal}'.")
                            break
                st.success(f"Successfully logged ${amount:,.2f} savings! You earned 50 points.")
            else:
                st.error("Please enter a positive amount to save.")

    st.markdown("---")
    st.header("Your Savings History")
    if not user_data["savings_history"]:
        st.info("No savings logged yet.")
    else:
        for entry in reversed(user_data["savings_history"]):
            st.write(f"💰 **${entry['amount']:,.2f}** on {entry['date']}")

def learn_quiz_page():
    """Presents financial literacy quizzes."""
    user = st.session_state.username
    user_data = st.session_state.users[user]

    st.title("🧠 Financial Wisdom Quizzes")
    st.markdown("Test your knowledge and learn new financial concepts!")

    if 'current_quiz_question_idx' not in st.session_state:
        st.session_state.current_quiz_question_idx = 0
    if 'quiz_answered' not in st.session_state:
        st.session_state.quiz_answered = False

    if st.session_state.current_quiz_question_idx < len(QUIZ_QUESTIONS):
        question_data = QUIZ_QUESTIONS[st.session_state.current_quiz_question_idx]
        st.subheader(f"Question {st.session_state.current_quiz_question_idx + 1}:")
        st.write(question_data["question"])

        with st.form(key=f"quiz_form_{st.session_state.current_quiz_question_idx}"):
            selected_option = st.radio("Choose your answer:", question_data["options"], key="quiz_option")
            submit_answer = st.form_submit_button("Submit Answer")

            if submit_answer and not st.session_state.quiz_answered:
                st.session_state.quiz_answered = True
                if selected_option == question_data["answer"]:
                    st.success("Correct! 🎉")
                    award_points(user, 30)
                    user_data["correct_quiz_answers"] = user_data.get("correct_quiz_answers", 0) + 1
                    check_for_badges(user) # Check for quiz whiz badge
                else:
                    st.error(f"Incorrect. The correct answer was: **{question_data['answer']}**")

                st.session_state.quiz_feedback_shown = True # Flag to indicate feedback has been shown
                st.session_state.quiz_next_button_enabled = True # Enable next button
            elif submit_answer and st.session_state.quiz_answered:
                st.warning("You've already answered this question. Click 'Next Question' to continue.")

        if st.session_state.get('quiz_feedback_shown', False) and st.session_state.get('quiz_next_button_enabled', False):
            if st.button("Next Question"):
                st.session_state.current_quiz_question_idx += 1
                st.session_state.quiz_answered = False
                st.session_state.quiz_feedback_shown = False
                st.session_state.quiz_next_button_enabled = False
                st.rerun() # Rerun to load next question
    else:
        st.info("You've completed all the quizzes for now! Check back later for more.")
        if st.button("Restart Quizzes"):
            st.session_state.current_quiz_question_idx = 0
            st.session_state.quiz_answered = False
            st.session_state.quiz_feedback_shown = False
            st.session_state.quiz_next_button_enabled = False
            st.rerun()

def badges_page():
    """Displays the badges earned by the user."""
    user = st.session_state.username
    user_data = st.session_state.users[user]

    st.title("🏆 Your Achievements")
    st.markdown("Celebrate your financial milestones!")

    if not user_data["badges"]:
        st.info("You haven't earned any badges yet. Keep engaging with the app to unlock them!")
    else:
        st.write("Here are the badges you've earned:")
        for badge in user_data["badges"]:
            st.success(f"🏅 **{badge}**")
            # You could add descriptions for each badge here
            if badge == "Newbie":
                st.write("*(Awarded for joining FinLearn Play)*")
            elif badge == "First Saver":
                st.write("*(Awarded for logging your first savings)*")
            elif badge == "Goal Setter":
                st.write("*(Awarded for setting your first financial goal)*")
            elif badge == "Quiz Whiz":
                st.write("*(Awarded for mastering financial quizzes)*")
            elif badge == "Budget Boss":
                st.write("*(Awarded for accumulating significant points)*")
            elif badge == "Goal Achiever":
                st.write("*(Awarded for successfully completing a financial goal)*")
            st.markdown("---")

# --- Main App Logic ---

def main_app():
    """Main function to run the Streamlit app."""
    st.sidebar.title("Navigation")
    if st.session_state.logged_in:
        st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
        if st.sidebar.button("Dashboard"):
            st.session_state.current_page = "dashboard"
        if st.sidebar.button("Set Goals"):
            st.session_state.current_page = "set_goals"
        if st.sidebar.button("Log Savings"):
            st.session_state.current_page = "log_savings"
        if st.sidebar.button("Learn & Quiz"):
            st.session_state.current_page = "learn_quiz"
        if st.sidebar.button("My Badges"):
            st.session_state.current_page = "badges"
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout"):
            logout()
    else:
        st.sidebar.info("Please log in or register to access the app features.")

    # Render the current page
    if st.session_state.logged_in:
        if st.session_state.current_page == "dashboard":
            dashboard_page()
        elif st.session_state.current_page == "set_goals":
            set_goals_page()
        elif st.session_state.current_page == "log_savings":
            log_savings_page()
        elif st.session_state.current_page == "learn_quiz":
            learn_quiz_page()
        elif st.session_state.current_page == "badges":
            badges_page()
    else:
        login_page()

# Run the app
if __name__ == "__main__":
    main_app()

