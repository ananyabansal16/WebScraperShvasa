import gspread
from openai import OpenAI
from sheets_client import init_google_sheets
import os
from dotenv import load_dotenv

def init_openai():
    load_dotenv()
    if openai_api_key := os.getenv('OPENAI_API_KEY'):
        return OpenAI(api_key=openai_api_key)
    else:
        raise ValueError("Please set the OPENAI_API_KEY environment variable in .env file.")


def get_answer_from_openai(client, question, model_name):
    try:
        # prompts = [f"You are a helpful assistant.\n{question}" for question in questions]
        response = client.chat.completions.create(
            model = model_name,
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Please provide complete and coherent answers that end naturally within the given context in a paragraph with the point of view of yogi/yoga instructor"},
                {"role": "user", "content": question}
            ],
            # prompt=prompts,
            max_tokens = 150, 
            n = 1, 
            stop = ["\n\n", "\n- ", "\n* "],
            temperature = 0.7)
        # answers = [choice.text.strip() for choice in response.choices]
        answer = response.choices[0].message.content.strip()
        if not answer.endswith("."):
            answer += "."  # Ensure the answer ends with a period
        return answer
    except Exception as e:
        print(f"Error getting answer from OpenAI: {e}")
        return None
    
def insert_answers_into_google_sheets(client, openai_client, model_name, spreadsheet_name='questions'):
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        print("Spreadsheet not found, creating a new one.")
        spreadsheet = client.create(spreadsheet_name)
        spreadsheet.share(client.auth.service_account_email, perm_type='user', role='writer')
        
    worksheet = spreadsheet.sheet1
    
    header = worksheet.row_values(1)
    answer_col_index = header.index("Answer")+1 if "Answer" in header else len(header) + 1
    status_col_index = header.index("Status")+1 if "Status" in header else len(header) + 1
    
    if "Answer" not in header:
        worksheet.update_cell(1, answer_col_index, "Answer")
        header.append("Answer")
    
    if "Status" not in header:
        worksheet.update_cell(1, status_col_index, "Status")
        header.append("Status")

    rows = worksheet.get_all_records()
    print(f"Total rows fetched: {len(rows)}")
    # if rows:
    #     print("Row structure:", rows[0])
    # else:
    #     print("No rows found in the worksheet.")
    #     return
    
    unanswered_questions = [row for row in rows if row.get('Status')=='Unanswered']
    print(f"Unanswered questions count: {len(unanswered_questions)}")
    
    for question in unanswered_questions:
        print("Processing question:", question.get("Title"))
        
        title = question.get("Title")
        if not title:
            print(f"Skipping question without title: {question}")
            continue
            
        answer = get_answer_from_openai(openai_client, title, model_name)
        question['Answer'] = answer
        
        try:
            row_index = worksheet.find(title).row
            worksheet.update_cell(row_index, answer_col_index, answer)
            worksheet.update_cell(row_index, status_col_index, "Pending")
            print(f"Updated row {row_index} with answer: {answer}")
        except Exception as e:
            print(f"Error updating cell for question '{title}': {e}")
            
def verify_and_update_answered_status(client, spreadsheet_name='questions'):
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        print("Spreadsheet not found, creating a new one.")
        spreadsheet = client.create(spreadsheet_name)
        spreadsheet.share(client.auth.service_account_email, perm_type='user', role='writer')
        
    worksheet = spreadsheet.sheet1

    header = worksheet.row_values(1)
    answer_col_index = header.index("Answer") + 1 if "Answer" in header else None
    status_col_index = header.index("Status") + 1 if "Status" in header else None
    question_id_col_index = header.index("Question ID") + 1 if "Question ID" in header else None
    
    if answer_col_index is None or status_col_index is None or question_id_col_index is None:
        print("Required columns not found. Please ensure the 'Answer' and 'Status' columns exist.")
        return

    rows = worksheet.get_all_records()

    for row_index, row in enumerate(rows, start=2):  # start=2 to account for the header row
        answer = row.get("Answer")
        status = row.get("Status")
        quesid = row.get("Question ID")

        # correct_status = ("Pending" if answer else "Unanswered") and ("Posted" or "Answered" if quesid else )
        if answer:
            if quesid:
                correct_status = "Posted" if status != "Answered" else "Answered"
            else:
                correct_status = "Pending"
        else:
            correct_status = "Unanswered"

        if status != correct_status:
            try:
                worksheet.update_cell(row_index, status_col_index, correct_status)
                print(f"Updated row {row_index} with correct 'Status': {correct_status}")
            except Exception as e:
                print(f"Error updating 'Status' status for row {row_index}: {e}")

def test_openai():
    openai_client = init_openai()
    sheets_client = init_google_sheets()
    verify_and_update_answered_status(sheets_client)
    insert_answers_into_google_sheets(sheets_client, openai_client)

if __name__ == "__main__":
    test_openai()