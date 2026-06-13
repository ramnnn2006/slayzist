import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

# On langchain 1.x the classic agent helpers live in langchain_classic.
# Fall back to that if the old import path isn't there.
try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

# Running on Groq here since it's free and needs no local setup.
# If you have Ollama running locally, comment the Groq lines below and use these:
# from langchain_ollama import ChatOllama
# llm = ChatOllama(model="llama3.2", temperature=0)
#
# Or for OpenAI:
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


@tool
def attendance_calculator(total_classes: int, attended_classes: int) -> dict:

    """  Takes total classes and attended classes, gives back attendance % and whether the student can sit for exams.
    75% or above = eligible, below that = not eligible.  """
    if total_classes <= 0:
        return {"error": "total classes has to be more than 0"}
    if attended_classes < 0 or attended_classes > total_classes:
        return {"error": "attended classes doesn't make sense with the total given"}

    pct = (attended_classes / total_classes) * 100
    status = "Eligible for Exam" if pct >= 75 else "Not Eligible for Exam"

    return {  "attended": attended_classes,  "total": total_classes,  "attendance_percentage": round(pct, 2),  "eligibility_status": status }


@tool
def result_calculator(
    subject1: float,
    subject2: float,
    subject3: float,
    subject4: float,
    subject5: float,
) -> dict:
    """  Pass marks for 5 subjects. Returns average, grade (A/B/C/D), and pass or fail.
    Grade rule: >=90 -> A, 75-89 -> B, 60-74 -> C, below 60 -> D
    Pass if average >= 50.  """
    marks = [subject1, subject2, subject3, subject4, subject5]
    avg = sum(marks) / 5

    if avg >= 90:
        grade = "A"
    elif avg >= 75:
        grade = "B"
    elif avg >= 60:
        grade = "C"
    else:
        grade = "D"

    return {"marks": marks,  "average": round(avg, 2),  "grade": grade,  "result": "Pass" if avg >= 50 else "Fail"  }

@tool
def fee_balance_calculator(total_fee: float, amount_paid: float) -> dict:
    """ Total fee minus what's already paid gives the pending amount.  """
    if total_fee < 0 or amount_paid < 0:
        return {"error": "fee values can't be negative"}

    pending = total_fee - amount_paid
    return {  "total_fee": total_fee,  "paid": amount_paid,   "pending_fee": max(pending, 0)   }


@tool
def library_fine_calculator(delayed_days: int) -> dict:
    """ Fine is Rs.5 per day delayed. Multiply and return.   """
    if delayed_days < 0:
        return {"error": "days can't be negative"}
    fine = 5 * delayed_days
    return {
        "delayed_days": delayed_days,
        "fine_amount": f"Rs.{fine}"  }


@tool
def hostel_fee_calculator(monthly_fee: float, months_stayed: int) -> dict:
    """   Monthly fee times number of months gives the total hostel fee. """
    if monthly_fee < 0 or months_stayed < 0:
        return {"error": "values can't be negative"}
    total = monthly_fee * months_stayed
    return {     "monthly_fee": monthly_fee, "months_stayed": months_stayed,  "total_hostel_fee": total }


# Bonus tool: look up a student from a local dict by ID.

STUDENTS = {
    "S001": {"name": "Ravi Kumar",        "branch": "Computer Science", "year": 2, "cgpa": 8.7},
    "S002": {"name": "Priya Sharma",      "branch": "Electronics",      "year": 3, "cgpa": 9.1},
    "S003": {"name": "Arjun Singh",       "branch": "Mechanical",       "year": 1, "cgpa": 7.5},
    "S004": {"name": "Neha Patel",        "branch": "Civil",            "year": 4, "cgpa": 8.2},
    "S005": {"name": "Ananya Krishnan",   "branch": "Computer Science", "year": 1, "cgpa": 9.3},
    "S006": {"name": "Rohan Mehta",       "branch": "Civil",            "year": 2, "cgpa": 6.8},
    "S007": {"name": "Sneha Iyer",        "branch": "Electronics",      "year": 4, "cgpa": 7.9},
    "S008": {"name": "Vikram Nair",       "branch": "Mechanical",       "year": 3, "cgpa": 8.5},
    "S009": {"name": "Divya Menon",       "branch": "Computer Science", "year": 2, "cgpa": 7.2},
    "S010": {"name": "Aditya Rao",        "branch": "Civil",            "year": 1, "cgpa": 8.0},
    "S011": {"name": "Pooja Reddy",       "branch": "Electronics",      "year": 2, "cgpa": 9.0},
    "S012": {"name": "Karthik Suresh",    "branch": "Mechanical",       "year": 4, "cgpa": 7.1},
    "S013": {"name": "Meera Pillai",      "branch": "Computer Science", "year": 3, "cgpa": 8.8},
    "S014": {"name": "Rahul Das",         "branch": "Civil",            "year": 1, "cgpa": 6.5},
    "S015": {"name": "Lakshmi Narayanan", "branch": "Electronics",      "year": 3, "cgpa": 8.3},
}

@tool
def student_info(student_id: str, field: str = "") -> dict:
    """Get a student's details by ID. Pass a field like cgpa/branch/year/name for just that one, or leave it empty to get everything."""
    s = STUDENTS.get(student_id.strip().upper())
    if not s:
        return {"error": f"no student with id {student_id}"}
    return {field: s[field]} if field in s else s


tools = [  attendance_calculator,result_calculator, fee_balance_calculator,library_fine_calculator, hostel_fee_calculator,   student_info]

SYSTEM_PROMPT = ( "you are a college assistant chatbot. "
    "you SHOULD/CAN ONLY answer questions related to: attendance, exam results/grades, course fees, library fines, hostel charges, and student information. "
    "if the user asks anything outside of these topics, respond with exactly: "
    "'Sorry, I can't help with that. Please ask only college-related questions.' "
    "do not answer general knowledge, coding, personal, or any other off-topic questions under any circumstances. "
    "keep responses clear and to the point.")

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def ask(query):
    print("\n" + "-" * 60)
    print("Query:", query)
    print("-" * 60)
    result = agent_executor.invoke({"input": query})
    print("\nResponse:", result["output"])


if __name__ == "__main__":
    # test case 1
    ask("I attended 72 classes out of 90. Am I eligible for exams?")
    # test case 2
    ask("My marks are 95, 90, 88, 91 and 87. What is my grade?")
    # test case 3
    ask("My course fee is 50000 and I have paid 35000. How much fee is pending?")
    # test case 4
    ask("I returned a library book 8 days late. What is the fine amount?")
    # test case 5
    ask("Hostel fee is 6000 per month and I stayed for 5 months. Calculate my hostel fee.")
    # multi-tool test, agent should call 3 tools here
    ask(
        "I attended 80 classes out of 100. "
        "My marks are 90, 85, 88, 92 and 95. "
        "My course fee is 60000 and I paid 45000. "
        "Give me my attendance status, grade, and pending fee."  )
    # bonus
    ask("Show me details for student S002.")
