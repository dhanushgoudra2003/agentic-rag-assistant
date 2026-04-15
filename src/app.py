from src.nodes.generator import generate_followups, evaluate_mcq
from src.graph import app


def clean_question_text(q: str):
    lines = q.strip().split("\n")

    if lines and lines[0].strip().lower() == "question:":
        lines = lines[1:]

    return "\n".join(lines).strip()


def run():
    print("🚀 LangGraph Agentic RAG Ready\n")

    chat_history = []

    # 🧪 Quiz state
    current_mcq = []
    current_mcq_index = 0
    score = 0
    total_questions = 0
    questions = []   # 🔥 NEW: store visible questions

    while True:
        query = input("\n💬 Ask a question (or type 'exit'): ").strip()

        if query.lower() == "exit":
            break

        # =========================
        # 🧪 QUIZ ANSWER HANDLING
        # =========================
        if current_mcq:
            if query.upper() in ["A", "B", "C", "D"]:
                print(f"\n🧪 Question {current_mcq_index + 1}/{total_questions}")
                print("Evaluating your answer...\n")

                result = evaluate_mcq(
                    current_mcq[current_mcq_index],
                    query.upper()
                )
                print(result)

                if "✅" in result:
                    score += 1

                current_mcq_index += 1

                # 👉 SHOW NEXT QUESTION (FIXED)
                if current_mcq_index < total_questions:
                    next_q = clean_question_text(questions[current_mcq_index])
                    print(f"\n🔹 Question {current_mcq_index + 1}:\n{next_q}")
                    print("\n👉 Enter your answer (A/B/C/D)")
                else:
                    print("\n🎉 Quiz Completed!\n")

                    print("📊 RESULT SUMMARY:")
                    print(f"Score: {score}/{total_questions}")

                    percentage = (score / total_questions) * 100
                    print(f"Percentage: {percentage:.2f}%")

                    if percentage >= 80:
                        print("🔥 Excellent! You're interview ready.")
                    elif percentage >= 50:
                        print("👍 Good, but needs improvement.")
                    else:
                        print("📚 Keep practicing!")

                    # reset
                    current_mcq = []
                    current_mcq_index = 0
                    score = 0
                    total_questions = 0
                    questions = []

                continue
            else:
                print("⚠️ Please enter ONLY A / B / C / D")
                continue

        # =========================
        # 🔥 FORCE 10-QUESTION QUIZ
        # =========================
        if "quiz" in query.lower() or "test" in query.lower():
            query = "quiz 10 " + query

        # =========================
        # 🔥 Add memory
        # =========================
        if chat_history:
            history_text = "\n".join(chat_history[-2:])
            query_with_context = f"Previous conversation:\n{history_text}\n\nCurrent question:\n{query}"
        else:
            query_with_context = query

        # =========================
        # 🚀 RUN GRAPH
        # =========================
        result = app.invoke({
            "query": query_with_context
        })

        answer = result["answer"]

        # =========================
        # 🧪 HANDLE QUIZ OUTPUT
        # =========================
        if "__MCQ__" in answer:

            if "__HIDDEN__" not in answer:
                print("⚠️ MCQ generation failed. Please try again.")
                continue

            visible, hidden = answer.split("__HIDDEN__")

            visible_clean = visible.replace("__MCQ__", "").strip()
            hidden_clean = hidden.strip()

            if "ANSWER:" not in hidden_clean:
                print("⚠️ Invalid MCQ format. Regenerating...")
                continue

            current_mcq = hidden_clean.split("||")
            current_mcq_index = 0
            score = 0
            total_questions = len(current_mcq)

            # 🔥 STORE QUESTIONS
            questions = visible_clean.split("\n\n---\n\n")

            print(f"\n🧪 Quiz Mode Activated ({total_questions} Questions)\n")

            # 🔥 SHOW ONLY FIRST QUESTION
            first_q = clean_question_text(questions[0])
            print(f"\n🔹 Question 1:\n{first_q}")

            print("\n👉 Enter your answer (A/B/C/D)")
            continue

        # =========================
        # 🔥 NORMAL ANSWER
        # =========================
        print("\n✅ Final Answer:\n")
        print(answer)

        # =========================
        # 🔥 FOLLOW-UPS
        # =========================
        try:
            followups = generate_followups(answer)

            print("\n💡 Follow-up questions:")
            for f in followups:
                print(f"- {f}")

        except Exception:
            print("\n💡 Follow-up questions:")
            print("- What are the key challenges in this system?")
            print("- How can this system be optimized for scale?")

        # =========================
        # 🔥 Save conversation
        # =========================
        chat_history.append(f"User: {query}")
        chat_history.append(f"AI: {answer}")


if __name__ == "__main__":
    run()